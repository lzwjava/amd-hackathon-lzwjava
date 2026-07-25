"""ahl - AMD Hackathon Launcher: CLI for remote server management."""

import argparse
import os
import subprocess
import sys


def ssh_cmd(ssh_base, remote_script):
    """Run a bash script on the remote server via SSH heredoc."""
    full_cmd = (
        f"""{ssh_base} 'bash -s' << 'REMOTE'\n"""
        f"""{remote_script}\n"""
        f"""REMOTE"""
    )
    print(f"🚀 {ssh_base.split()[0]} {ssh_base.split()[1][:20]}...")
    print()
    result = subprocess.run(full_cmd, shell=True, text=True)
    if result.returncode != 0:
        sys.exit(result.returncode)


def run_local(cmd):
    """Run a local shell command."""
    result = subprocess.run(cmd, shell=True, text=True)
    if result.returncode != 0:
        sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(
        prog="ahl",
        description="AMD Hackathon Launcher — manage remote server, tunnel, and downloads",
    )
    parser.add_argument(
        "--host", default="36.150.116.206", help="Remote server host"
    )
    parser.add_argument("-p", "--port", type=int, default=31005, help="SSH port")
    parser.add_argument("--user", default="root", help="SSH user")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ── tunnel ──────────────────────────────────────────────
    tp = subparsers.add_parser("tunnel", help="Manage rc-tunnel")
    tsub = tp.add_subparsers(dest="tunnel_action", help="Tunnel actions")
    tsub.add_parser("setup", help="Install rc-tunnel and expose a port")
    tsub.add_parser("status", help="Check tunnel status")
    tsub.add_parser("stop", help="Stop the tunnel")
    tsub.add_parser("logs", help="Show tunnel logs")

    # ── download ────────────────────────────────────────────
    dp = subparsers.add_parser("download", help="Download models")
    dsub = dp.add_subparsers(dest="download_action", help="Download targets")

    fp = dsub.add_parser("flux", help="Download FLUX model")
    fp.add_argument(
        "variant", nargs="?", default="schnell",
        choices=["schnell", "dev", "2-dev"],
        help="FLUX variant (default: schnell)",
    )
    fp.add_argument("--token", default=None, help="HuggingFace token")
    fp.add_argument(
        "--local-dir", default=None,
        help="Download target directory on remote",
    )

    # ── gen-video ───────────────────────────────────────────
    gvp = subparsers.add_parser("gen-video", help="Generate short-form videos from markdown")
    gvsub = gvp.add_subparsers(dest="gen_video_action", help="gen-video actions")

    gv_generate = gvsub.add_parser("generate", help="Read markdown from pasteboard and submit to gen-video server")
    gv_generate.add_argument("--output", help="Output video path")
    gv_generate.add_argument("--model", help="LLM model override")
    gv_generate.add_argument("--image-model", help="Image generation model override")
    gv_generate.add_argument("--server", help="Gen-video server URL override")
    gv_generate.add_argument("--poll", action="store_true", help="Wait for completion and download")
    gv_generate.add_argument("--upload", action="store_true", help="Upload to YouTube after creation")
    gv_generate.add_argument("--privacy", default="public", choices=["public", "private", "unlisted"], help="YouTube privacy (default: public)")

    gv_query = gvsub.add_parser("query", help="Query job status")
    gv_query.add_argument("job_id", help="Job ID to query")
    gv_query.add_argument("--server", help="Server URL override")
    gv_query.add_argument("--json", action="store_true", help="Output raw JSON")

    gv_server = gvsub.add_parser("server", help="Start the gen-video API server")
    gv_server.add_argument("--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    gv_server.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    gv_server.add_argument("--reload", action="store_true", help="Enable auto-reload")

    gv_video = gvsub.add_parser("video", help="Generate a video directly from a markdown file")
    gv_video.add_argument("file", help="Path to markdown file")
    gv_video.add_argument("--output", help="Output video path")
    gv_video.add_argument("--model", help="LLM model for script generation")
    gv_video.add_argument("--image-model", default="black-forest-labs/flux.2-pro", help="Image generation model")
    gv_video.add_argument("--upload", action="store_true", help="Upload to YouTube after creation")
    gv_video.add_argument("--private", action="store_true", help="Set YouTube video to private")

    # ── ssh / shell / info / check ──────────────────────────
    subparsers.add_parser("ssh", help="Open an interactive SSH session")
    sp = subparsers.add_parser("shell", help="Run a shell command on remote")
    sp.add_argument("cmd", nargs=argparse.REMAINDER, help="Command to run")
    subparsers.add_parser("info", help="Show remote server info")
    subparsers.add_parser("check", help="Check download progress")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    ssh_base = f"ssh -o StrictHostKeyChecking=no -p {args.port} {args.user}@{args.host}"

    if args.command == "tunnel":
        return handle_tunnel(args, ssh_base)
    elif args.command == "download":
        return handle_download(args, ssh_base)
    elif args.command == "gen-video":
        return handle_gen_video(args)
    elif args.command == "ssh":
        print(f"🔌 Connecting...")
        subprocess.run(f"{ssh_base} -t", shell=True)
    elif args.command == "shell":
        cmd = " ".join(args.cmd) if args.cmd else ""
        if cmd:
            subprocess.run(f"""{ssh_base} "cd /root && {cmd}" """, shell=True)
        else:
            print("❌ Specify a command to run")
    elif args.command == "info":
        show_info(ssh_base)
    elif args.command == "check":
        check_download(ssh_base)
    else:
        parser.print_help()


# ── Tunnel ─────────────────────────────────────────────────────

# ── Gen-Video ──────────────────────────────────────────────────

def handle_gen_video(args):
    action = args.gen_video_action
    if not action:
        print("Usage: ahl gen-video {generate|query|server|video}")
        sys.exit(1)

    if action == "generate":
        from ahl.gen_video.generate import main as gv_generate
        # Map ahl args to the generate module's sys.argv convention
        gv_args = ["ahl", "gen-video", "generate"]
        if args.output:
            gv_args += ["--output", args.output]
        if args.model:
            gv_args += ["--model", args.model]
        if args.image_model:
            gv_args += ["--image-model", args.image_model]
        if args.server:
            gv_args += ["--server", args.server]
        if args.poll:
            gv_args += ["--poll"]
        if args.upload:
            gv_args += ["--upload"]
        if args.privacy:
            gv_args += ["--privacy", args.privacy]
        sys.argv = gv_args
        gv_generate()
    elif action == "query":
        from ahl.gen_video.query import main as gv_query
        gv_args = ["ahl", "gen-video", "query", args.job_id]
        if args.server:
            gv_args += ["--server", args.server]
        if args.json:
            gv_args += ["--json"]
        sys.argv = gv_args
        gv_query()
    elif action == "server":
        from ahl.gen_video.server import main as gv_server
        gv_args = ["ahl", "gen-video", "server"]
        if args.host:
            gv_args += ["--host", args.host]
        if args.port:
            gv_args += ["--port", str(args.port)]
        if args.reload:
            gv_args += ["--reload"]
        sys.argv = gv_args
        gv_server()
    elif action == "video":
        from ahl.gen_video.video import main as gv_video
        gv_args = ["ahl", "gen-video", "video", args.file]
        if args.output:
            gv_args += ["--output", args.output]
        if args.model:
            gv_args += ["--model", args.model]
        if args.image_model:
            gv_args += ["--image-model", args.image_model]
        if args.upload:
            gv_args += ["--upload"]
        if args.private:
            gv_args += ["--private"]
        sys.argv = gv_args
        gv_video()


def handle_tunnel(args, ssh_base):
    script = r"""
set -e
export FRP_BROKER_URL=$(grep -z FRP_BROKER_URL /proc/1/environ | tr '\0' '\n' | cut -d= -f2-)
export FRP_BROKER_TLS_SERVER_NAME=$(grep -z FRP_BROKER_TLS_SERVER_NAME /proc/1/environ | tr '\0' '\n' | cut -d= -f2-)
export PATH="$HOME/.local/bin:$PATH"
"""
    if args.tunnel_action == "setup":
        port = input("Port to expose (default: 8081): ").strip() or "8081"
        script += f"""
echo "=== Installing/checking rc-tunnel ==="
if ! command -v rc-tunnel &>/dev/null; then
    /var/run/secrets/frp-self-service/install
fi
rc-tunnel version
echo ""
echo "=== Exposing port {port} ==="
rc-tunnel expose --port {port}
"""
        ssh_cmd(ssh_base, script)

    elif args.tunnel_action == "status":
        ssh_cmd(ssh_base, script + "\nrc-tunnel status\n")
    elif args.tunnel_action == "stop":
        ssh_cmd(ssh_base, script + "\nrc-tunnel stop\n")
    elif args.tunnel_action == "logs":
        ssh_cmd(ssh_base, script + "\nrc-tunnel logs --lines 50\n")
    else:
        print("Usage: ahl tunnel {setup|status|stop|logs}")


# ── Download ───────────────────────────────────────────────────

def handle_download(args, ssh_base):
    variant = args.variant
    if variant == "2-dev":
        hf_model = "black-forest-labs/FLUX.2-dev"
        local_dir = args.local_dir or "/root/FLUX.2-dev"
    elif variant == "dev":
        hf_model = "black-forest-labs/FLUX.1-dev"
        local_dir = args.local_dir or "/root/FLUX.1-dev"
    else:
        hf_model = "black-forest-labs/FLUX.1-schnell"
        local_dir = args.local_dir or "/root/FLUX.1-schnell"

    token = args.token or os.environ.get("HF_TOKEN", "")
    if not token:
        print("❌ No HuggingFace token provided.")
        print("   Pass --token or set HF_TOKEN environment variable.")
        sys.exit(1)

    script = f"""set -e
source /opt/venv/bin/activate

echo "=== Logging into HuggingFace ==="
mkdir -p ~/.cache/huggingface
echo "{token}" > ~/.cache/huggingface/token
echo "Token saved"

echo ""
echo "=== Downloading {hf_model} ==="
echo "Target: {local_dir}"
echo ""

tmux kill-session -t flux-download 2>/dev/null || true

cat > /root/download_flux.sh << 'SCRIPT'
#!/bin/bash
source /opt/venv/bin/activate
export HF_ENDPOINT=https://hf-mirror.com
export HF_TOKEN={token}
echo "=== Downloading {hf_model} to {local_dir} ==="
echo "Started at: $(date)"
huggingface-cli download {hf_model} --local-dir {local_dir} --resume-download --quiet
echo ""
echo "=== Finished at: $(date) ==="
ls -lh {local_dir}/
SCRIPT

chmod +x /root/download_flux.sh
tmux new-session -d -s flux-download '/root/download_flux.sh'

echo "✅ Download started in tmux session 'flux-download'"
echo ""
echo "Monitor with:"
echo "  ahl check"
echo "  ahl shell 'du -sh {local_dir}/'"
echo ""
sleep 2
tmux capture-pane -t flux-download -p
"""
    ssh_cmd(ssh_base, script)


# ── Info ───────────────────────────────────────────────────────

def show_info(ssh_base):
    script = r"""source /opt/venv/bin/activate
echo "=== GPU ==="
rocm-smi 2>&1 | head -5
echo ""
echo "=== PyTorch ==="
python -c "import torch; print(f'Torch {torch.__version__}, CUDA: {torch.cuda.is_available()}, GPUs: {torch.cuda.device_count()}, HIP: {torch.version.hip}')" 2>&1
echo ""
echo "=== Disk ==="
df -h /
echo ""
echo "=== Memory ==="
free -h
echo ""
echo "=== CPU ==="
nproc
"""
    ssh_cmd(ssh_base, script)


# ── Check download ─────────────────────────────────────────────

def check_download(ssh_base):
    script = r"""echo "=== Download progress ==="
du -sh /root/FLUX.*/ 2>/dev/null || echo "No FLUX directories found"
echo ""
for d in /root/FLUX.*/; do
  if [ -d "$d" ]; then
    echo "--- $d ---"
    find "$d" -name "*.safetensors" -exec ls -lh {} \; 2>/dev/null
    echo ""
    inc=$(find "$d/.cache/huggingface/download/" -name "*.incomplete" 2>/dev/null)
    if [ -n "$inc" ]; then
      echo "⏳ Incomplete: $(ls -lh $inc | awk '{print $5}')"
    else
      echo "✅ No incomplete files"
    fi
    echo ""
  fi
done
echo "=== tmux ==="
tmux list-sessions 2>/dev/null || echo "no tmux sessions"
ps aux | grep huggingface | grep -v grep || echo "no download process"
"""
    ssh_cmd(ssh_base, script)


if __name__ == "__main__":
    main()
