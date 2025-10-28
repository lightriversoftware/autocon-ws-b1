"""
Database-driven service generation.
Generates services directly into SQLite database with full UUID tracking.
"""

import sys
import uuid as uuid_module
import networkx as nx
from pathlib import Path
from typing import Dict, Tuple, List, Optional, Set

from core.config_loader import load_config
from database.database_manager import NetworkDatabase
from services.edge_cover import EdgeCoverBuilder, create_threshold_graph
from services.dijkstra_router import CapacityAwareDijkstra
from services.service import Service
import numpy as np


class DatabaseServiceRouter:
    """
    Two-stage service generation with capacity-feasible guarantees.

    Stage A: Guaranteed endpoint coverage via minimum edge cover
    Stage B: Randomized Dijkstra routing with high-capacity corridor bias

    Correctness Guarantees:
    - Capacity safety: No edge capacity ever exceeded
    - Endpoint coverage: Every node is a service endpoint (Stage A)
    - Path simplicity: All paths are simple (no repeated vertices)
    - Reproducibility: Fixed random seed produces identical results
    """

    def __init__(
        self,
        db: NetworkDatabase,
        demand: float,
        p_exponent: float = 1.5,
        rho_exponent: float = 1.0,
        noise_delta: float = 0.01,
        random_seed: int = 42,
        enable_stage_a: bool = True
    ):
        """
        Initialize the database service router.

        Args:
            db: NetworkDatabase instance
            demand: Fixed demand D per service (Gbps)
            p_exponent: Cost function exponent p in (r_e/D)^(-p)
            rho_exponent: Endpoint sampling exponent ρ in (Σr_e)^ρ
            noise_delta: Uniform noise range [-δ, +δ] for tie-breaking
            random_seed: Random seed for reproducibility
            enable_stage_a: Whether to run Stage A edge cover
        """
        self.db = db
        self.demand = demand
        self.p_exponent = p_exponent
        self.rho_exponent = rho_exponent
        self.noise_delta = noise_delta
        self.enable_stage_a = enable_stage_a

        # Initialize RNG for reproducibility
        self.rng = np.random.RandomState(random_seed)

        # Will be populated by _load_network_from_db()
        self.graph = None
        self.residuals = {}
        self.node_name_to_uuid = {}
        self.node_uuid_to_name = {}
        self.edge_to_uuid = {}
        self.node_coordinates = {}

        # Services generated
        self.services = []

    def generate_services(self, target_count: int = 100) -> int:
        """
        Generate services using two-stage algorithm.

        Args:
            target_count: Target number of services to generate

        Returns:
            Number of services actually generated
        """
        print(f"\n{'=' * 70}")
        print("SERVICE GENERATION - Two-Stage Algorithm")
        print(f"{'=' * 70}")
        print(f"Target services: {target_count}")
        print(f"Demand per service: {self.demand} Gbps")
        print(f"Stage A enabled: {self.enable_stage_a}")
        print()

        # Load network from database
        self._load_network_from_db()

        stage_a_count = 0
        stage_b_count = 0

        # Stage A: Edge cover for guaranteed endpoint coverage
        if self.enable_stage_a:
            print("=" * 70)
            print("STAGE A: Guaranteed Endpoint Coverage (Edge Cover)")
            print("=" * 70)
            stage_a_services = self._stage_a_edge_cover()
            stage_a_count = len(stage_a_services)
            self.services.extend(stage_a_services)
            print(f"  Generated {stage_a_count} Stage A services")
            print()

        # Stage B: Randomized Dijkstra routing
        remaining_target = target_count - len(self.services)
        if remaining_target > 0:
            print("=" * 70)
            print("STAGE B: Randomized Dijkstra Routing")
            print("=" * 70)
            print(f"Target: {remaining_target} additional services")
            stage_b_services = self._stage_b_randomized_dijkstra(remaining_target)
            stage_b_count = len(stage_b_services)
            self.services.extend(stage_b_services)
            print(f"  Generated {stage_b_count} Stage B services")
            print()

        # Persist services to database
        print("=" * 70)
        print("PERSISTING SERVICES TO DATABASE")
        print("=" * 70)
        self._persist_services_to_db(self.services)

        print()
        print("=" * 70)
        print("SERVICE GENERATION COMPLETE")
        print("=" * 70)
        print(f"Total services generated: {len(self.services)}")
        print(f"  Stage A (edge cover): {stage_a_count}")
        print(f"  Stage B (Dijkstra):   {stage_b_count}")
        print("=" * 70)
        print()

        return len(self.services)

    def _load_network_from_db(self) -> None:
        """Load network topology from database into NetworkX graph."""
        print("Loading network topology from database...")

        # Build NetworkX graph
        self.graph = nx.Graph()

        # Load nodes
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT uuid, name, latitude, longitude, capacity_gbps FROM nodes")
        nodes = cursor.fetchall()

        for node in nodes:
            node_uuid = node['uuid']
            node_name = node['name']
            lat = node['latitude']
            lon = node['longitude']
            capacity = node['capacity_gbps']

            self.graph.add_node(node_name,
                              uuid=node_uuid,
                              latitude=lat,
                              longitude=lon,
                              capacity_gbps=capacity)

            self.node_name_to_uuid[node_name] = node_uuid
            self.node_uuid_to_name[node_uuid] = node_name
            self.node_coordinates[node_name] = (lat, lon)

        # Load edges
        cursor.execute("SELECT uuid, node1_uuid, node2_uuid, capacity_gbps FROM edges")
        edges = cursor.fetchall()

        for edge in edges:
            edge_uuid = edge['uuid']
            node1_uuid = edge['node1_uuid']
            node2_uuid = edge['node2_uuid']
            capacity = edge['capacity_gbps']

            node1_name = self.node_uuid_to_name[node1_uuid]
            node2_name = self.node_uuid_to_name[node2_uuid]

            self.graph.add_edge(node1_name, node2_name,
                              uuid=edge_uuid,
                              capacity_gbps=capacity)

            # Initialize residual capacity
            edge_key = tuple(sorted([node1_name, node2_name]))
            self.residuals[edge_key] = capacity

            # Store edge UUID mapping (in canonical order)
            edge_uuid_key = tuple(sorted([node1_uuid, node2_uuid]))
            self.edge_to_uuid[edge_uuid_key] = edge_uuid

        cursor.close()

        print(f"  Loaded {self.graph.number_of_nodes()} nodes")
        print(f"  Loaded {self.graph.number_of_edges()} edges")
        print(f"  Total initial capacity: {sum(self.residuals.values()):.2f} Gbps")
        print()

    def _stage_a_edge_cover(self) -> List[Service]:
        """
        Stage A: Generate services via minimum edge cover.

        Guarantees every node is a service endpoint (if no isolated vertices).

        Returns:
            List of Stage A services (one per edge in cover)
        """
        services = []

        # Create threshold graph G_D (edges with r_e >= D)
        threshold_graph, available_edges = create_threshold_graph(
            self.graph, self.residuals, self.demand
        )

        print(f"  Threshold graph G_D: {threshold_graph.number_of_edges()} edges with r_e >= {self.demand} Gbps")

        # Check for isolated vertices
        isolated = [node for node in threshold_graph.nodes()
                   if threshold_graph.degree(node) == 0]
        if isolated:
            print(f"  WARNING: {len(isolated)} isolated vertices in G_D")
            print(f"  Stage A cannot cover: {isolated[:5]}{'...' if len(isolated) > 5 else ''}")
            print("  Skipping Stage A")
            return services

        # Find minimum edge cover
        try:
            edge_cover_builder = EdgeCoverBuilder()
            edge_cover = edge_cover_builder.find_edge_cover(
                threshold_graph,
                available_edges=available_edges
            )
            print(f"  Minimum edge cover size: {len(edge_cover)} edges")

            # Verify coverage
            if edge_cover_builder.verify_coverage(threshold_graph, edge_cover):
                print("  ✓ Edge cover verified: all vertices covered")
            else:
                print("  ✗ Edge cover verification FAILED")
                return services

        except ValueError as e:
            print(f"  ERROR: {e}")
            print("  Skipping Stage A")
            return services

        # Route one-edge paths on edge cover
        print(f"  Routing one-edge services on edge cover...")
        for idx, (u, v) in enumerate(edge_cover, start=1):
            # Create service
            service_id = f"SVC-{idx:03d}"
            path = [u, v]

            # Calculate distance
            if u in self.node_coordinates and v in self.node_coordinates:
                lat1, lon1 = self.node_coordinates[u]
                lat2, lon2 = self.node_coordinates[v]
                distance = CapacityAwareDijkstra.haversine_distance(lat1, lon1, lat2, lon2)
            else:
                distance = 0.0

            # Generate timestamp
            timestamp = Service.generate_random_timestamp(idx, base_seed=self.rng.randint(0, 100000))

            service = Service(
                service_id=service_id,
                name=f"Service {u} to {v}",
                source=u,
                destination=v,
                path=path,
                demand_gbps=self.demand,
                total_distance_km=distance,
                timestamp=timestamp,
                _routing_stage="stage_a"
            )

            services.append(service)

            # Update residual capacity
            edge_key = tuple(sorted([u, v]))
            self.residuals[edge_key] -= self.demand

            if self.residuals[edge_key] < 0:
                print(f"    WARNING: Negative residual on edge {edge_key}: {self.residuals[edge_key]}")

        print(f"  ✓ Generated {len(services)} Stage A services")

        return services

    def _stage_b_randomized_dijkstra(self, target_count: int) -> List[Service]:
        """
        Stage B: Generate services using randomized Dijkstra routing.

        Samples endpoints with bias toward high-capacity nodes.
        Routes using cost function that favors high-residual edges.

        Args:
            target_count: Number of services to generate

        Returns:
            List of Stage B services
        """
        services = []

        # Initialize Dijkstra router
        dijkstra = CapacityAwareDijkstra(
            rng=self.rng,
            node_coordinates=self.node_coordinates
        )

        # Track statistics
        attempts = 0
        max_consecutive_failures = 100
        consecutive_failures = 0

        service_offset = len(self.services) + 1  # Continue numbering from Stage A

        while len(services) < target_count:
            attempts += 1

            # Update threshold graph (remove edges with r_e < D)
            threshold_graph, available_edges = create_threshold_graph(
                self.graph, self.residuals, self.demand
            )

            # Check if network is exhausted
            if threshold_graph.number_of_edges() == 0:
                print(f"  Network capacity exhausted after {len(services)} services")
                break

            # Sample endpoints with ρ-weighting
            source, target = self._sample_endpoints(threshold_graph, self.rho_exponent)

            if source is None or target is None:
                consecutive_failures += 1
                if consecutive_failures >= max_consecutive_failures:
                    print(f"  Failed to sample valid endpoints {max_consecutive_failures} times")
                    print(f"  Network likely disconnected. Stopping.")
                    break
                continue

            # Check connectivity
            if not dijkstra.check_connectivity(
                threshold_graph, source, target, self.residuals, self.demand
            ):
                consecutive_failures += 1
                if consecutive_failures >= max_consecutive_failures:
                    print(f"  Network disconnected after {len(services)} services")
                    break
                continue

            # Reset consecutive failures on success
            consecutive_failures = 0

            # Compute path using Dijkstra
            path = dijkstra.compute_path(
                graph=threshold_graph,
                source=source,
                target=target,
                residuals=self.residuals,
                demand=self.demand,
                p_exponent=self.p_exponent,
                noise_delta=self.noise_delta
            )

            if path is None:
                continue

            # Calculate path distance
            distance = dijkstra.get_path_distance(self.graph, path)

            # Create service
            service_id = f"SVC-{service_offset + len(services):03d}"
            timestamp = Service.generate_random_timestamp(
                service_offset + len(services),
                base_seed=self.rng.randint(0, 100000)
            )

            service = Service(
                service_id=service_id,
                name=f"Service {source} to {target}",
                source=source,
                destination=target,
                path=path,
                demand_gbps=self.demand,
                total_distance_km=distance,
                timestamp=timestamp,
                _routing_stage="stage_b"
            )

            services.append(service)

            # Reserve capacity on path
            for i in range(len(path) - 1):
                edge_key = tuple(sorted([path[i], path[i + 1]]))
                self.residuals[edge_key] -= self.demand

                if self.residuals[edge_key] < -1e-6:  # Small tolerance for floating point
                    print(f"    WARNING: Negative residual on edge {edge_key}: {self.residuals[edge_key]}")

            # Progress reporting
            if len(services) % 10 == 0:
                print(f"  Progress: {len(services)}/{target_count} services generated "
                      f"({attempts} attempts, {threshold_graph.number_of_edges()} edges available)")

        print(f"  ✓ Generated {len(services)} Stage B services in {attempts} attempts")

        return services

    def _sample_endpoints(
        self,
        threshold_graph: nx.Graph,
        rho_exponent: float
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Sample endpoints (s, t) with probability proportional to (Σr_e)^ρ.

        Args:
            threshold_graph: G_D with edges where r_e >= D
            rho_exponent: Exponent ρ for weighting

        Returns:
            Tuple of (source, target) node names, or (None, None) if sampling fails
        """
        if threshold_graph.number_of_nodes() < 2:
            return None, None

        # Compute weights for each node: w(v) = (Σ_{e∋v} r_e)^ρ
        weights = {}
        for node in threshold_graph.nodes():
            incident_residual_sum = 0.0
            for neighbor in threshold_graph.neighbors(node):
                edge_key = tuple(sorted([node, neighbor]))
                incident_residual_sum += self.residuals.get(edge_key, 0.0)

            if incident_residual_sum > 0:
                weights[node] = incident_residual_sum ** rho_exponent
            else:
                weights[node] = 0.0

        # Filter nodes with positive weight
        valid_nodes = [node for node, w in weights.items() if w > 0]
        if len(valid_nodes) < 2:
            return None, None

        # Normalize weights
        total_weight = sum(weights[node] for node in valid_nodes)
        if total_weight == 0:
            return None, None

        probabilities = np.array([weights[node] / total_weight for node in valid_nodes])

        # Sample two distinct nodes
        sampled = self.rng.choice(valid_nodes, size=2, replace=False, p=probabilities)

        return sampled[0], sampled[1]

    def _persist_services_to_db(self, services: List[Service]) -> None:
        """
        Persist services to database with full path information.

        Args:
            services: List of Service objects to persist
        """
        if not services:
            print("  No services to persist")
            return

        print(f"  Persisting {len(services)} services to database...")

        for idx, service in enumerate(services, start=1):
            try:
                # Generate service UUID
                service_uuid = str(uuid_module.uuid4())

                # Get source and destination UUIDs
                source_uuid = self.node_name_to_uuid[service.source]
                dest_uuid = self.node_name_to_uuid[service.destination]

                # Get path node UUIDs
                path_node_uuids = [
                    self.node_name_to_uuid[node_name]
                    for node_name in service.path
                ]

                # Get path edge UUIDs
                path_edge_uuids = []
                for i in range(len(service.path) - 1):
                    u_name = service.path[i]
                    v_name = service.path[i + 1]

                    u_uuid = self.node_name_to_uuid[u_name]
                    v_uuid = self.node_name_to_uuid[v_name]

                    # Edge UUID key must be in canonical order
                    edge_uuid_key = tuple(sorted([u_uuid, v_uuid]))
                    edge_uuid = self.edge_to_uuid.get(edge_uuid_key)

                    if edge_uuid is None:
                        raise ValueError(f"Edge UUID not found for {u_name}-{v_name}")

                    path_edge_uuids.append(edge_uuid)

                # Insert into database
                self.db.insert_service_with_path(
                    service_uuid=service_uuid,
                    name=service.name,
                    source_node_uuid=source_uuid,
                    destination_node_uuid=dest_uuid,
                    demand_gbps=service.demand_gbps,
                    hop_count=service.hop_count,
                    total_distance_km=service.total_distance_km,
                    service_timestamp=service.timestamp,
                    path_node_uuids=path_node_uuids,
                    path_edge_uuids=path_edge_uuids
                )

                if idx % 20 == 0:
                    print(f"    Progress: {idx}/{len(services)} services persisted")

            except Exception as e:
                print(f"    ERROR persisting service {service.service_id}: {e}")
                raise

        print(f"  ✓ Successfully persisted {len(services)} services")


def main():
    """
    Standalone service generation script for testing.
    """
    print("\n" + "=" * 70)
    print("DATABASE SERVICE GENERATION")
    print("=" * 70)

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

    # Initialize database
    db_path = Path(config.data_dir) / "network.db"
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        print("Please run container_init.py first to create the network.")
        sys.exit(1)

    db = NetworkDatabase(str(db_path))

    # Get database stats
    stats = db.get_stats()
    print(f"\nDatabase: {db_path}")
    print(f"  Nodes: {stats['nodes']}")
    print(f"  Edges: {stats['edges']}")
    print(f"  Existing services: {stats['services']}")
    print()

    # Initialize router
    router = DatabaseServiceRouter(
        db=db,
        demand=config.demand_gbps,
        p_exponent=config.p_exponent,
        rho_exponent=config.rho_exponent,
        noise_delta=config.noise_delta,
        random_seed=config.service_random_seed or 42,
        enable_stage_a=config.enable_stage_a
    )

    # Generate services
    try:
        service_count = router.generate_services(target_count=config.target_services)
        print(f"\nSuccessfully generated {service_count} services")
    except Exception as e:
        print(f"\nError during service generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

    print("\n" + "=" * 70)
    print("SERVICE GENERATION COMPLETE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
