#!/usr/bin/env bash
set -euo pipefail

# ^ Fail fast on any error (-e), undefined var (-u), or pipeline error (-o pipefail).

IMAGE="${IMAGE:-ghcr.io/lightriversoftware/workshop}"

# ^ Default GHCR image; override by: IMAGE=ghcr.io/acme/lab/workshop:sha-abc123 ./student_start_lab.sh

USER_NAME="${USER_NAME:-$(id -un)}"

# ^ Default the in-container Linux user to the current host user.

PORT="${PORT:-2222}"

# ^ Host TCP port to map to container's SSH (22). EACH STUDENT MUST PICK A UNIQUE PORT.

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/srv/workshop}"

# ^ Host path for persistent files. Each student gets ${WORKSPACE_ROOT}/${USER_NAME}.

CONTAINER_NAME="lab-${USER_NAME}"

# ^ Stable name so "docker exec -it lab-$USER_NAME bash" works later if needed.

UID_NUM="$(id -u "${USER_NAME}")"
GID_NUM="$(id -g "${USER_NAME}")"

# ^ Match container user to host UID/GID to avoid permission headaches on bind mounts.

# Ensure workspace exists and is owned by the student user.

# sudo mkdir -p "${WORKSPACE_ROOT}/${USER_NAME}"
# sudo chown "${USER_NAME}:${USER_NAME}" "${WORKSPACE_ROOT}/${USER_NAME}"

# Ensure authorized_keys exists with secure perms (required by sshd).

# sudo install -d -m 700 -o "${USER_NAME}" -g "${USER_NAME}" "/home/${USER_NAME}/.ssh"
# sudo install -m 600 -o "${USER_NAME}" -g "${USER_NAME}" /dev/null "/home/${USER_NAME}/.ssh/authorized_keys"

# ^ If you already have keys, this won't overwrite contents; it only ensures the file exists with correct mode.

# Pull the image (no-op if already present).

docker pull "${IMAGE}"

# If a previous container exists, (re)start it; else create it.

if docker ps -a --format '{{.Names}}' | grep -qx "${CONTAINER_NAME}"; then
  docker start "${CONTAINER_NAME}" >/dev/null
else
docker run -d \
 --name "${CONTAINER_NAME}" \
    --hostname "${CONTAINER_NAME}" \
 --restart unless-stopped \
 -p "${PORT}:22" \
    -e USER_NAME="${USER_NAME}" \
 -e USER_UID="${UID_NUM}" \
    -e USER_GID="${GID_NUM}" \
 -v "/home/${USER_NAME}/.ssh/authorized_keys:/home/${USER_NAME}/.ssh/authorized_keys:ro" \
 -v "${WORKSPACE_ROOT}/${USER_NAME}:/workspace" \
 "${IMAGE}"
fi

# ^ Launches an sshd-in-container using your Dockerfile+entrypoint design:

# -p maps host $PORT → container 22

# env vars make a matching user inside the container

# mounts read-only authorized_keys and a writable per-user workspace

HOST_TARGET="${HOST_TARGET:-$(hostname -f 2>/dev/null || hostname || ip route get 1 | awk '{print $7; exit}')}"
echo "${CONTAINER_NAME} running → ssh -p ${PORT} ${USER_NAME}@${HOST_TARGET}"

