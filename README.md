# ahl — AMD Hackathon Launcher

CLI tool to manage an AMD GPU remote server: tunnel setup, model downloads, and system info.

## Install

```bash
pip install -e .
```

## Usage

### 🔌 Tunnel — Expose a local port to the internet

```bash
# Set up the rc-tunnel (expose port 8081)
ahl tunnel setup

# Check tunnel status
ahl tunnel status

# View tunnel logs
ahl tunnel logs

# Stop the tunnel
ahl tunnel stop
```

### 📥 Download models

```bash
# Download FLUX.1-schnell (default, ~58 GB)
ahl download flux --token hf_xxxxx

# Download FLUX.1-dev (~69 GB)
ahl download flux dev --token hf_xxxxx

# Download FLUX.2-dev (~177 GB)
ahl download flux 2-dev --token hf_xxxxx

# Or set env var instead of --token
export HF_TOKEN=hf_xxxxx
ahl download flux
```

### ℹ️ System Info

```bash
# Show GPU, PyTorch, disk, memory
ahl info

# Check download progress
ahl check

# Run any command on the remote server
ahl shell nvidia-smi
# or
ahl shell "df -h && free -h"

# Open interactive SSH session
ahl ssh
```

## Defaults

| Setting | Default |
|---------|---------|
| Host | `36.150.116.206` |
| Port | `31005` |
| User | `root` |

Override with `--host`, `-p`/`--port`, `--user`.

## How it works

- **Tunnel**: Uses the platform's `rc-tunnel` (FRP-based) to expose a local port via a public URL `rc-<random>.radeon.firstdg.ai`
- **Download**: Uses `hf-mirror.com` (HuggingFace mirror accessible from China) with `tmux` for background downloads
- **All commands** SSH into the remote server and execute the necessary steps
