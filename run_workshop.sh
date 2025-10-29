#!/usr/bin/env bash
set -euo pipefail


IMAGE="${IMAGE:-ghcr.io/lightriversoftware/workshop}"


USER_NAME="${USER_NAME:-$(id -un)}"


PORT="${PORT:-$1}"


WORKSPACE_ROOT="${WORKSPACE_ROOT:-/srv/workshop}"


CONTAINER_NAME="lab-${USER_NAME}"


UID_NUM="$(id -u "${USER_NAME}")"
GID_NUM="$(id -g "${USER_NAME}")"

docker pull "${IMAGE}"

if docker ps -a --format '{{.Names}}' | grep -qx "${CONTAINER_NAME}"; then
  docker start "${CONTAINER_NAME}" >/dev/null
else
docker run -d \
 --name "${CONTAINER_NAME}" \
    --hostname "${CONTAINER_NAME}" \
 --restart unless-stopped \
 --network lab-network \
 -p "${PORT}:22" \
    -e USER_NAME="${USER_NAME}" \
 -e USER_UID="${UID_NUM}" \
    -e USER_GID="${GID_NUM}" \
 -v "/home/${USER_NAME}/.ssh/authorized_keys:/home/${USER_NAME}/.ssh/authorized_keys:ro" \
 -v "${WORKSPACE_ROOT}/${USER_NAME}:/workspace" \
 "${IMAGE}"
fi


HOST_TARGET="${HOST_TARGET:-$(hostname -f 2>/dev/null || hostname || ip route get 1 | awk '{print $7; exit}')}"
echo "${CONTAINER_NAME} running → ssh -p ${PORT} ${USER_NAME}@${HOST_TARGET}"

