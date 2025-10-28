FROM python:3.12-slim AS base

# 3. Keep noninteractive APT installs quiet in CI.
ENV DEBIAN_FRONTEND=noninteractive

# 4. Install only what we need: openssh-server for SSH, tini for PID 1 hygiene,
#    gosu for safe privilege drop if you ever need it, plus certificates.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    openssh-server tini gosu ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 5. SSHD needs this directory to exist.
RUN mkdir -p /var/run/sshd

# 6. Set a stable working directory for the project.
WORKDIR /opt/workshop

# 7. Copy only requirements first to leverage Docker layer cache for pip installs.
COPY requirements.txt /opt/workshop/requirements.txt

# 8. Upgrade pip and install Python dependencies. The --no-cache-dir keeps image slim.
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r /opt/workshop/requirements.txt

# 9. Now copy the rest of the workshop files (code, notebooks, scripts, etc.).
#    Keeping this after requirements preserves cache if your code changes often.
COPY . /opt/workshop

# 10. Create a default workspace directory that users can work out of.
#     You can mount a host volume to /workspace later if you want persistence.
RUN mkdir -p /workspace

# 11. Provide sensible defaults for runtime user creation (overridable via -e).
ENV USER_NAME=participant \
    USER_UID=1000 \
    USER_GID=1000 \
    SHELL=/bin/bash

# 12. Make Tini the container's PID 1 for signal handling and zombie reaping.
#     We wrap our entrypoint with tini in ENTRYPOINT below.
#     Also, put the entrypoint script in a standard path and mark executable.
COPY docker-entrypoint.sh /usr/local/sbin/entrypoint.sh
RUN chmod +x /usr/local/sbin/entrypoint.sh

# 13. Expose port 22 for SSH (documentation only; -p binds at runtime).
EXPOSE 22

# 14. Default working dir once someone logs in.
WORKDIR /workspace

# 15. Use Tini as the entrypoint, then run our entrypoint script.
ENTRYPOINT ["/usr/bin/tini","-g","--","/usr/local/sbin/entrypoint.sh"]

# 16. By default, start OpenSSH in the foreground with logs to stderr (-e).
CMD ["/usr/sbin/sshd","-D","-e"]
