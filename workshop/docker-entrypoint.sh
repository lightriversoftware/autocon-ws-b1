#!/usr/bin/env bash
set -euo pipefail

# 1) Prepare a matching group and user so host-mounted files have sane ownership.
if ! getent group "${USER_GID}" >/dev/null 2>&1; then
  # If the group id exists under a different name, reuse it; else create new.
  groupadd -g "${USER_GID}" "${USER_NAME}" 2>/dev/null || true
fi

if ! id -u "${USER_NAME}" >/dev/null 2>&1; then
  useradd -m -u "${USER_UID}" -g "${USER_GID}" -s "${SHELL}" "${USER_NAME}"
fi

# 2) Ensure home and .ssh exist with correct permissions (mount will override if provided).
HOME_DIR="/home/${USER_NAME}"
mkdir -p "${HOME_DIR}/.ssh"
chmod 700 "${HOME_DIR}/.ssh"
# Provide a placeholder authorized_keys if none is mounted.
: > "${HOME_DIR}/.ssh/authorized_keys" || true
chmod 600 "${HOME_DIR}/.ssh/authorized_keys"
chown -R "${USER_UID}:${USER_GID}" "${HOME_DIR}"

# 3) Symlink workshop content into user's home for convenience (no overwrite).
#    Users will see ~/workshop pointing to the baked /opt/workshop.
if [ ! -e "${HOME_DIR}/workshop" ]; then
  ln -s /opt/workshop "${HOME_DIR}/workshop"
  chown -h "${USER_UID}:${USER_GID}" "${HOME_DIR}/workshop"
fi

# 4) Make /workspace owned by the user (handy when not mounting a volume).
mkdir -p /workspace
chown "${USER_UID}:${USER_GID}" /workspace

# 5) Tweak a couple sshd settings at runtime (idempotent).
#    - Disallow password logins; keys only.
#    - Allow user-provided environment (.ssh/environment) if you want TERM etc.
#    - KeepAlive knobs are nice for classroom wifi.
SSHD_CFG="/etc/ssh/sshd_config"
sed -i 's/^#\?PasswordAuthentication .*/PasswordAuthentication no/' "${SSHD_CFG}"
sed -i 's/^#\?PermitUserEnvironment .*/PermitUserEnvironment yes/' "${SSHD_CFG}"
grep -q '^ClientAliveInterval' "${SSHD_CFG}" || echo 'ClientAliveInterval 60' >> "${SSHD_CFG}"
grep -q '^ClientAliveCountMax' "${SSHD_CFG}" || echo 'ClientAliveCountMax 3' >> "${SSHD_CFG}"

# 6) Print a helpful banner once (goes to container logs).
echo "Workshop image ready. SSH user=${USER_NAME} uid=${USER_UID} gid=${USER_GID}" >&2

# 7) Exec the final command (from CMD) as root; sshd must start as root to bind 22.
#    Users will get their own shell from sshd with the correct UID.
exec "$@"
