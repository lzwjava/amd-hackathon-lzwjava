#!/usr/bin/env python3
"""
Standalone script to run FLUX inference on the remote AMD GPU server.

Usage:
    python infer_flux.py "a cute cat" --download
    python infer_flux.py "cyberpunk city" --steps 8 --width 1024 --height 1024
    python infer_flux.py --model dev "portrait" --download
"""

import argparse
import os
import subprocess
import sys
import time

# Default SSH config
HOST = "36.150.116.206"
PORT = 31005
USER = "root"

MODEL_PATHS = {
    "schnell": "/root/FLUX.1-schnell",
    "dev": "/root/FLUX.1-dev",
    "2-dev": "/root/FLUX.2-dev",
}


def ssh_cmd(ssh_base, remote_script):
    """Run a bash script on the remote server via SSH heredoc."""
    full_cmd = (
        f"""{ssh_base} 'bash -s' << 'REMOTE'\n"""
        f"""{remote_script}\n"""
        f"""REMOTE"""
    )
    print(f"🚀 Sending to remote...\n")
    result = subprocess.run(full_cmd, shell=True, text=True)
    if result.returncode != 0:
        sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(
        description="Generate images with FLUX on a remote AMD GPU server"
    )
    parser.add_argument("prompt", nargs="?", default=None, help="Text prompt")
    parser.add_argument("--model", default="schnell", choices=list(MODEL_PATHS.keys()),
                        help="FLUX variant (default: schnell)")
    parser.add_argument("--model-dir", default=None, help="Override model path on remote")
    parser.add_argument("--steps", type=int, default=4, help="Inference steps (default: 4)")
    parser.add_argument("--width", type=int, default=1024, help="Image width (default: 1024)")
    parser.add_argument("--height", type=int, default=1024, help="Image height (default: 1024)")
    parser.add_argument("--guidance", type=float, default=0.0, help="Guidance scale (default: 0.0)")
    parser.add_argument("--output", default=None, help="Output filename")
    parser.add_argument("--download", action="store_true", help="Download image to local")
    parser.add_argument("--host", default=HOST, help=f"Remote host (default: {HOST})")
    parser.add_argument("--port", type=int, default=PORT, help=f"SSH port (default: {PORT})")
    parser.add_argument("--user", default=USER, help=f"SSH user (default: {USER})")

    args = parser.parse_args()

    prompt = args.prompt
    if not prompt:
        prompt = input("Enter prompt: ").strip()
        if not prompt:
            print("❌ No prompt provided")
            sys.exit(1)

    model_dir = args.model_dir or MODEL_PATHS[args.model]
    output = args.output or f"flux_{args.model}_{int(time.time())}.png"
    remote_path = f"/root/{output}"

    ssh_base = f"ssh -o StrictHostKeyChecking=no -p {args.port} {args.user}@{args.host}"

    # Escape single quotes in the prompt for the Python string
    escaped_prompt = prompt.replace("'", "'\\''")

    remote_script = f"""set -e
source /opt/venv/bin/activate
export USE_ROCM_AITER_ROPE_BACKEND=0

python3 << 'PYEOF'
import torch
from diffusers import FluxPipeline
import time

torch.cuda.empty_cache()

pipe = FluxPipeline.from_pretrained('{model_dir}', torch_dtype=torch.bfloat16)
pipe.enable_sequential_cpu_offload()
pipe.enable_attention_slicing()

prompt = '''{escaped_prompt}'''
print(f'Prompt: {{prompt}}')
print(f'Generating {{args.width}}x{{args.height}}, {{args.steps}} steps...')
t0 = time.time()
image = pipe(
    prompt,
    num_inference_steps={args.steps},
    guidance_scale={args.guidance},
    width={args.width},
    height={args.height},
).images[0]
t1 = time.time()

image.save('{remote_path}')
print(f'Done in {{t1-t0:.1f}}s')
print(f'Saved: {remote_path} ({{image.size[0]}}x{{image.size[1]}})')
print(f'Max VRAM used: {{torch.cuda.max_memory_allocated()/1e9:.2f}} GB')
PYEOF
"""
    ssh_cmd(ssh_base, remote_script)

    if args.download:
        local_path = os.path.join(os.getcwd(), output)
        print(f"📥 Downloading to {local_path}...")
        subprocess.run([
            "scp", "-P", str(args.port), "-o", "StrictHostKeyChecking=no",
            f"{args.user}@{args.host}:{remote_path}", local_path
        ])
        print(f"✅ Saved to {local_path}")


if __name__ == "__main__":
    main()
