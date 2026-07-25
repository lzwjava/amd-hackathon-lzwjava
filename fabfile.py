"""Fabric deployment file for ahl — AMD Hackathon Launcher.

Deploys the local source tree to /root/ahl on the remote server.

Usage:
    fab -H 36.150.116.206:31005 deploy    # Deploy to remote
    fab -H root@36.150.116.206:31005 deploy
    fab -H 36.150.116.206:31005 status    # Show deployed version
    fab -H 36.150.116.206:31005 shell -- cmd="ls -la /root/ahl"
"""

from fabric import Connection, task

DEFAULT_HOST = "36.150.116.206"
DEFAULT_PORT = 31005
DEFAULT_USER = "root"
REMOTE_DIR = "/root/ahl"

EXCLUDE = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".DS_Store",
    ".git",
    ".venv",
    "venv",
    "env",
    "*.egg-info",
    ".env",
    "*.png",
    "*.mp4",
    "cat_hd.png",
    "cat.png",
    "flux_output_*.png",
]


def _conn(c):
    """Create a Fabric Connection from the invoke context.

    Uses -H flag if provided, otherwise falls back to defaults.
    """
    # Try to extract host/port from -H flag
    hosts = getattr(c.config, "hosts", None)
    if hosts:
        host_str = hosts[0]  # e.g. "root@host:31005" or "host:31005"
        user = DEFAULT_USER
        host = host_str
        port = DEFAULT_PORT

        if "@" in host_str:
            user, host = host_str.split("@", 1)
        if ":" in host:
            host, port_str = host.split(":", 1)
            port = int(port_str)

        return Connection(
            host=host,
            port=port,
            user=user,
            connect_kwargs={"allow_agent": True},
        )

    # Fall back to defaults
    return Connection(
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        user=DEFAULT_USER,
        connect_kwargs={"allow_agent": True},
    )


@task
def deploy(c):
    """Rsync local source tree to /root/ahl on remote, then pip install -e ."""
    conn = _conn(c)
    print(f"🚀 Deploying to {conn.user}@{conn.host}:{conn.port} → {REMOTE_DIR}")

    # Ensure remote dir exists
    conn.run(f"mkdir -p {REMOTE_DIR}", hide=True)

    # Rsync with exclusions
    exclude_args = " ".join(f"--exclude={e}" for e in EXCLUDE)
    ssh_cmd = f"ssh -o StrictHostKeyChecking=no -p {conn.port}"
    rsync_cmd = (
        f"rsync -avz --delete -e '{ssh_cmd}' {exclude_args} "
        f"./ {conn.user}@{conn.host}:{REMOTE_DIR}/"
    )

    print("  Rsyncing files...")
    # Use local subprocess instead of c.local for clarity
    import subprocess as sp
    result = sp.run(rsync_cmd, shell=True, text=True)
    if result.returncode != 0:
        print("❌ Rsync failed")
        return

    print("  Installing package...")
    # Use /opt/venv (as used by all remote scripts) for pip install
    conn.run(f"cd {REMOTE_DIR} && /opt/venv/bin/pip install -e .", hide=False, pty=True)
    print("✅ Deploy complete")


@task
def install(c):
    """Deploy + pip install (alias for deploy)."""
    deploy(c)


@task
def status(c):
    """Show deployed version and check service status."""
    conn = _conn(c)
    print("=== Deployed version ===")
    conn.run(
        f"cd {REMOTE_DIR} && "
        "python3 -c \"from ahl import __version__; print(__version__)\" 2>/dev/null || "
        "grep 'version' pyproject.toml | head -1 || "
        "echo '(version not found)'"
    )
    print()
    print("=== Package info ===")
    conn.run("/opt/venv/bin/pip show ahl 2>/dev/null | head -5 || echo '(not installed via pip)'")
    print()
    print("=== Remote files ===")
    conn.run(f"ls -la {REMOTE_DIR}/")


@task
def shell(c, cmd=""):
    """Run an arbitrary shell command on the remote server.

    Usage: fab -H host:port shell -- cmd="ls -la /root/ahl"
    """
    conn = _conn(c)
    conn.run(cmd or "echo 'Usage: fab shell -- cmd=\"ls -la /root/ahl\"'", pty=True)
