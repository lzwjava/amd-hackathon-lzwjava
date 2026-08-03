# Submission Package — ahl (Track 1: Multimodal Content Creation Tools)

AMD AI DevMaster Hackathon 2026-07 · **Track 1** — short-form video creation on AMD Radeon GPU + ROCm.

## What's inside

| File | Requirement | Status |
|---|---|---|
| `01_project_specification.md` | Project Specification Document (scenarios, architecture, capabilities, model & deployment plan, AMD/ROCm optimization) | ✅ |
| Source repo (`README.md`, `ahl/`, `pyproject.toml`, `fabfile.py`) | Project source code (complete repo) | ✅ |
| `02_slides.md` | PPT — Marp source (render with Marp CLI, see below) | ✅ |
| `03_demo_video.md` | Demo video script (3–5 min) | ✅ script · 🎬 video TBD |
| `demo/ahl_demo.mp4` | Final demo video file | ⏳ to be provided |

## Rendering the PPT (Marp)

```bash
# Build HTML slides
npx @marp-team/marp-cli submission/02_slides.md

# Build PPTX (PowerPoint)
npx @marp-team/marp-cli submission/02_slides.md --pptx

# Build PDF
npx @marp-team/marp-cli submission/02_slides.md --pdf
```

## Quick start (already in repo README)

```bash
pip install -e .
ahl server --port 8000        # web UI + REST API
ahl img "a cyberpunk city"     # local image via sd-cpp (FLUX Q4_0 GGUF)
ahl download flux --token hf_xxx   # fetch FLUX models to the AMD GPU host
ahl info                       # GPU / ROCm / disk check
```

## Track-fit notes

- **Core inference = AMD Radeon GPU + ROCm**: scene images via PyTorch ROCm + diffusers (FLUX.1-schnell/dev/2-dev) or stable-diffusion.cpp (FLUX.1-schnell Q4_0 GGUF, 4-bit quantization).
- Remote API (OpenRouter) is **optional** for the text planning step only; the image/video core never requires it.
- Optimizations: 4-step distilled schnell, Q4_0 quantization, VAE tiling, VRAM budget, parallel scene generation, no-re-encode assembly.
