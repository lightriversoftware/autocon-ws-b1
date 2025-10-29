# Network Simulator API Reference

Quick reference for building agents that interact with the network simulator.

## Network Overview

- **48 nodes** across eastern US (Albany, Boston, NYC, Miami, etc.)
- **~200 edges** (bidirectional connections between nodes)
- **Geographic routing** with real distances
- **Capacity constraints** on both nodes and edges

## SDK Setup

```python
from network_simulator_client import NetworkSimulatorClient

client = NetworkSimulatorClient()  # Uses BACKEND_URL from environment
# ... use client ...
client.close()

# Or with context manager:
with NetworkSimulatorClient() as client:
    # Your code here
    pass
```

## Core Data Models

### Node
```python
node.uuid                 # Unique ID
node.name                 # City name (e.g., "Albany-NY")
node.latitude             # Geographic coordinate
node.longitude            # Geographic coordinate
node.vendor               # Equipment vendor
node.capacity_gbps        # Total capacity
node.free_capacity_gbps   # Available capacity
```

### Edge
```python
edge.uuid          # Unique ID
edge.node1_uuid    # First endpoint
edge.node2_uuid    # Second endpoint
edge.capacity_gbps # Edge capacity
```

### Service
```python
service.uuid                 # Unique ID
service.name                 # Service name
service.source_node_uuid     # Start node
service.destination_node_uuid # End node
service.demand_gbps          # Bandwidth requirement
service.hop_count            # Number of edges in path
service.path_node_uuids      # Ordered list of nodes
service.path_edge_uuids      # Ordered list of edges
service.total_distance_km    # Path distance
```

## Common Operations

### Search Nodes
```python
# Search by name
nodes = client.search_nodes_by_name("Albany")

# Get all nodes
all_nodes = client.get_nodes()

# Get specific node
node = client.get_node(uuid)
```

### Compute Routes
```python
route = client.compute_route(
    source_node_uuid=source.uuid,
    destination_node_uuid=dest.uuid,
    demand_gbps=10.0
)

# Route includes:
# - path_node_uuids: ordered list of nodes
# - path_edge_uuids: ordered list of edges
# - total_distance_km: path distance
# - hop_count: number of edges
# - min_available_capacity: bottleneck capacity
```

### Validate Paths
```python
validation = client.validate_path(
    path_node_uuids=["uuid1", "uuid2", "uuid3"],
    path_edge_uuids=["edge1", "edge2"],
    demand_gbps=10.0
)

# Returns: {"valid": True/False, "errors": [...], ...}
```

### Create Services
```python
from network_simulator_client.models import ServiceCreate
from datetime import datetime

service_data = ServiceCreate(
    name="My-Service",
    source_node_uuid=source.uuid,
    destination_node_uuid=dest.uuid,
    demand_gbps=10.0,
    routing_stage="stage_a",
    path_node_uuids=route.path_node_uuids,
    path_edge_uuids=route.path_edge_uuids,
    total_distance_km=route.total_distance_km,
    service_timestamp=datetime.utcnow().isoformat() + "Z"
)

created = client.create_service(service_data)
```

### Manage Services
```python
# Get service
service = client.get_service(service_uuid)

# Get all services
services = client.get_services(limit=100)

# Delete service
client.delete_service(service_uuid)
```

### Monitor Capacity
```python
# Get edge utilization
util = client.get_edge_utilization(edge_uuid)
# Returns: capacity_gbps, total_demand_gbps, utilization_pct, service_count

# Find violations (over 100%)
violations = client.get_capacity_violations()

# Find high utilization edges
high_util = client.get_high_utilization_edges(threshold_pct=80.0)
```

### Create Edges
```python
from network_simulator_client.models import EdgeCreate

edge_data = EdgeCreate(
    node1_uuid=node1.uuid,
    node2_uuid=node2.uuid,
    capacity_gbps=100.0
)

# Note: Can only create edges where connection already exists
# This expands capacity, doesn't create new connections
edge = client.create_edge(edge_data)
```

## Error Handling

```python
from network_simulator_client import (
    NodeNotFoundError,
    EdgeNotFoundError,
    ServiceNotFoundError,
    RouteNotFoundError,
    ValidationError,
    APIConnectionError
)

try:
    route = client.compute_route(source, dest, demand_gbps=100.0)
except RouteNotFoundError:
    # No feasible route with that capacity
    pass
except NodeNotFoundError:
    # Invalid node UUID
    pass
except APIConnectionError:
    # Can't connect to simulator
    pass
```

## Example: Complete Workflow

```python
from network_simulator_client import NetworkSimulatorClient
from network_simulator_client.models import ServiceCreate
from datetime import datetime

with NetworkSimulatorClient() as client:
    # 1. Find nodes
    sources = client.search_nodes_by_name("Albany")
    dests = client.search_nodes_by_name("Boston")

    source = sources[0]
    dest = dests[0]

    # 2. Compute route
    route = client.compute_route(
        source_node_uuid=source.uuid,
        destination_node_uuid=dest.uuid,
        demand_gbps=10.0
    )

    print(f"Route: {route.hop_count} hops, {route.total_distance_km:.1f} km")

    # 3. Validate path
    validation = client.validate_path(
        route.path_node_uuids,
        route.path_edge_uuids,
        10.0
    )

    if not validation["valid"]:
        print(f"Invalid path: {validation['errors']}")
        exit(1)

    # 4. Create service
    service_data = ServiceCreate(
        name="Albany-to-Boston-10G",
        source_node_uuid=source.uuid,
        destination_node_uuid=dest.uuid,
        demand_gbps=10.0,
        routing_stage="stage_a",
        path_node_uuids=route.path_node_uuids,
        path_edge_uuids=route.path_edge_uuids,
        total_distance_km=route.total_distance_km,
        service_timestamp=datetime.utcnow().isoformat() + "Z"
    )

    service = client.create_service(service_data)
    print(f"Created service: {service.uuid}")
```

## API Documentation

For complete API reference, see interactive docs when simulator is running:
- **Swagger UI**: http://localhost:8003/docs
- **ReDoc**: http://localhost:8003/redoc

## Tips

1. **Always validate** paths before creating services
2. **Check capacity** - `compute_route()` respects capacity constraints
3. **Use context managers** - ensures connections are closed properly
4. **Handle errors** - network operations can fail for many reasons
5. **Test incrementally** - verify each operation works before chaining them
