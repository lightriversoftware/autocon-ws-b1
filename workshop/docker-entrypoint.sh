#!/usr/bin/env bash
set -euo pipefail

# Default SHELL if not provided via environment
: "${SHELL:=/bin/bash}"

# --- 0) Inputs expected from `docker run -e ...` ---
# USER_NAME : login name to create (e.g., "spatel")
# USER_UID  : numeric UID to match host user (avoids permission issues)
# USER_GID  : numeric GID to match host user's primary group
# SHELL     : preferred shell (defaults to /bin/bash)

# --- 1) Ensure group + user exist with requested IDs ---
# Create (or reuse) a group with GID=USER_GID. If it already exists under
# another name, groupadd will fail; we ignore errors to keep idempotency.
if ! getent group "${USER_GID}" >/dev/null 2>&1; then
  groupadd -g "${USER_GID}" "${USER_NAME}" 2>/dev/null || true
fi

# Create the user if missing, with home dir and requested shell.
# If it already exists (e.g., container restarted), do nothing.
if ! id -u "${USER_NAME}" >/dev/null 2>&1; then
  useradd -m -u "${USER_UID}" -g "${USER_GID}" -s "${SHELL}" "${USER_NAME}"
fi

HOME_DIR="/home/${USER_NAME}"

# --- 2) Prepare ~/.ssh but be polite with read-only mounts ---
# Some hosts mount either ~/.ssh or just authorized_keys read-only into the container.
# We only create/chmod when paths are writable.

mkdir -p "${HOME_DIR}/.ssh" 2>/dev/null || true

# If the directory itself is writable, enforce 700 perms.
if [ -d "${HOME_DIR}/.ssh" ] && [ -w "${HOME_DIR}/.ssh" ]; then
  chmod 700 "${HOME_DIR}/.ssh" || true
fi

# If authorized_keys doesn't exist and the directory is writable, create an empty file.
if [ ! -e "${HOME_DIR}/.ssh/authorized_keys" ] && [ -w "${HOME_DIR}/.ssh" ]; then
  : > "${HOME_DIR}/.ssh/authorized_keys" || true
fi

# If authorized_keys exists *and is writable*, enforce 600; skip if it's a RO bind mount.
if [ -e "${HOME_DIR}/.ssh/authorized_keys" ] && [ -w "${HOME_DIR}/.ssh/authorized_keys" ]; then
  chmod 600 "${HOME_DIR}/.ssh/authorized_keys" || true
fi

# Chown what we safely can (skip if RO). We don't recurse over entire HOME to avoid RO errors.
chown "${USER_UID}:${USER_GID}" "${HOME_DIR}" 2>/dev/null || true
chown "${USER_UID}:${USER_GID}" "${HOME_DIR}/.ssh" 2>/dev/null || true
chown "${USER_UID}:${USER_GID}" "${HOME_DIR}/.ssh/authorized_keys" 2>/dev/null || true

# --- 3) Writable workspace for participant output ---
mkdir -p /workspace
chown "${USER_UID}:${USER_GID}" /workspace 2>/dev/null || true

# --- 4) Copy-once working tree so participant can edit freely ---
WORK_COPY="/workspace/workshop"
if [ ! -d "${WORK_COPY}" ]; then
  if command -v rsync >/dev/null 2>&1; then
    rsync -a /opt/workshop/ "${WORK_COPY}/"
  else
    # Fallback if rsync isn't installed
    mkdir -p "${WORK_COPY}"
    cp -a /opt/workshop/. "${WORK_COPY}/"
  fi
  chown -R "${USER_UID}:${USER_GID}" "${WORK_COPY}" 2>/dev/null || true
fi

# Repoint the convenience symlink to the writable copy (force replace)
ln -sfn "${WORK_COPY}" "${HOME_DIR}/workshop"
chown -h "${USER_UID}:${USER_GID}" "${HOME_DIR}/workshop" 2>/dev/null || true

# --- 5) SSH daemon hygiene (idempotent tweaks) ---
SSHD_CFG="/etc/ssh/sshd_config"

# Disable password auth; we rely on keys from authorized_keys.
sed -i 's/^#\?PasswordAuthentication .*/PasswordAuthentication no/' "${SSHD_CFG}" || true

# Allow user env (useful for TERM, custom tweaks via ~/.ssh/environment).
sed -i 's/^#\?PermitUserEnvironment .*/PermitUserEnvironment yes/' "${SSHD_CFG}" || true

# Keep-alive to help with flaky Wi-Fi in classrooms.
grep -q '^ClientAliveInterval' "${SSHD_CFG}" || echo 'ClientAliveInterval 60' >> "${SSHD_CFG}"
grep -q '^ClientAliveCountMax'  "${SSHD_CFG}" || echo 'ClientAliveCountMax 3'  >> "${SSHD_CFG}"

# Ensure runtime directory exists (normally created in Dockerfile; safe to re-assert).
mkdir -p /var/run/sshd

# --- 6) Banner to logs for debugging ---
echo "Workshop image ready: user=${USER_NAME} uid=${USER_UID} gid=${USER_GID}" >&2

# --- 7) Start the main process (from CMD) ---
# Keep running as root because sshd must bind to 22. SSH sessions will drop users to USER_NAME.
exec "$@"
