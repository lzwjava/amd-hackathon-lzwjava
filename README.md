# ahl — AMD Hackathon Launcher

CLI tool to manage an AMD GPU remote server: tunnel setup, model downloads, and system info.
Also generates images locally with the FLUX.1-schnell Q4_0 stable-diffusion.cpp setup
(`ahl img` / `--provider sdcpp`).

## Install

```bash
pip install -e .
```

## Usage

### 🖼️ Local image generation — sd-cpp FLUX (this machine, no server needed)

```bash
# Generate an image locally with FLUX.1-schnell Q4_0 via stable-diffusion.cpp
ahl img "a cyberpunk city at night, neon reflections"
ahl img "a dragon on a castle tower" --width 1024 --height 1024   # needs free VRAM
ahl img "cat" --steps 4 --output cat.png --seed 7
```

Defaults to 768×768 (the desktop holds ~2.9 GB of the 12 GB RTX 4070, so
1024×1024 needs Chromium/Slack closed). Overrides: `--width`, `--height`,
`--steps`, `--max-vram`, `--seed`, `--bin`, `--model-dir`, or env vars
`SDCPP_BIN`, `SDCPP_MODEL_DIR`, `SDCPP_WIDTH`, `SDCPP_HEIGHT`, `SDCPP_STEPS`.

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
