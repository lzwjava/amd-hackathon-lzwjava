# Project Specification — FluxReel: AMD GPU-Powered Short-Form Video Creation Tool

**Track:** 1 — Development of Multimodal Content Creation Tools
**Team project:** FluxReel (`fluxreel` — the CLI/package name)
**Submission date:** 2026-07

---

## 1. Application Scenarios

FluxReel turns a plain topic into a polished **15-second vertical short video**
(1080×1920, 9:16, 30 fps) fully locally on an **AMD Radeon GPU with the ROCm
software stack**. It is designed for creators who need fast, high-volume,
cost-controlled short-video output:

| Scenario | What the user gets |
|---|---|
| **New-media operations** (Douyin / WeChat Video Account) | A complete explainer video from a one-line topic — draft, scenes, images, captions, music — in minutes instead of hours |
| **Personal creation** | Custom styles (cyberpunk, infographic, dark neon) with zero design skills |
| **Commercial visual design** | Consistent brand-style scene images and captions for product explainers |
| **Education / knowledge sharing** | Teacher/student can produce an explainer video for any topic (GPU, RISC-V, AI concepts…) with bilingual (EN/中文) caption support |

Key value: the whole pipeline — script, scene images, captions and assembly —
runs **locally on the AMD Radeon GPU**. There is no per-video API cost and no
data leaves the machine, which matters for privacy-sensitive content.

---

## 2. Architecture Diagram

```
┌────────────────────────────  fluxreel pipeline (Track 1)  ────────────────────────────┐
│                                                                                  │
│  ┌──────────┐   topic    ┌──────────────────────┐   markdown   ┌──────────────┐  │
│  │  Web UI  │───────────▶│  Step 1: LLM writer  │─────────────▶│  Step 2:     │  │
│  │ (FastAPI │            │  article + 5-scene   │              │  Scene       │  │
│  │  server) │◀───────────│  script (titles,     │              │  planner     │  │
│  │ :8000    │  progress  │  subtitles, prompts) │              │  (LLM)       │  │
│  └──────────┘  /api/jobs └──────────────────────┘              └──────┬───────┘  │
│                                                                       │          │
│                                                      5 image_prompts │          │
│                                                                       ▼          │
│  ┌──────────────────────────────────  Step 3: image generation  ─────────────────┐ │
│  │                                                                              │ │
│  │   ┌─────────────────────────────┐     ┌───────────────────────────────────┐  │ │
│  │   │ Local GPU provider (core)   │     │ sd-cpp provider (quantized path)  │  │ │
│  │   │ PyTorch + diffusers on      │     │ stable-diffusion.cpp (ROCm/HIP)   │  │ │
│  │   │ AMD Radeon GPU (ROCm)       │     │ FLUX.1-schnell Q4_0 GGUF (4-bit)  │  │ │
│  │   │ FLUX.1-schnell/dev/2-dev    │     │ --vae-tiling --max-vram budget    │  │ │
│  │   └──────────────┬──────────────┘     └────────────────┬──────────────────┘  │ │
│  │                  └────────── 5× scene images (4:3) ────┘                     │ │
│  └──────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
│  ┌──────────────────────  Step 4: slide composition (CPU/PIL)  ───────────────┐  │
│  │  4:3 image centered · large title (110px) / subtitle (64px) · auto-shrink  │  │
│  │  font to fit bar · CJK-aware fonts (Noto Sans CJK) + char-based wrapping   │  │
│  └──────────────────────────────────┬─────────────────────────────────────────┘  │
│                                     ▼                                            │
│  ┌──────────────────────  Step 5: video assembly (ffmpeg)  ───────────────────┐  │
│  │  5 slides × 3 s · 1080×1920 @30fps · H.264 · background music + fade-out   │  │
│  └──────────────────────────────────┬─────────────────────────────────────────┘  │
│                                     ▼                                            │
│                      ┌───────────────────────────────┐                           │
│                      │  Final 15s vertical video     │──▶ optional YouTube       │
│                      └───────────────────────────────┘    upload (private mode) │
└──────────────────────────────────────────────────────────────────────────────────┘
```

**Inference placement (requirement: core inference on AMD Radeon GPU):**

| Stage | Where it runs |
|---|---|
| Scene image generation (**core**) | **AMD Radeon GPU via ROCm** — PyTorch/diffusers or stable-diffusion.cpp (HIP) |
| Video assembly, caption layout | Local CPU (ffmpeg, PIL) |
| Script / scene planning (LLM) | Local LLM option (vLLM / llama.cpp on ROCm); cloud LLM only as an optional convenience — never required for the core image/video pipeline |

---

## 3. Core Capabilities

1. **One-topic → 15 s video** — the user types a topic (e.g. “How GPUs work”,
   “GPU是什么？”), and gets a complete short video:
   - LLM drafts a scannable markdown article (300–500 words)
   - Scene planner splits it into exactly **5 scenes** (3 s each) with
     `title` / `subtitle` / `image_prompt` per scene, in the **same language
     as the topic** (EN/中文 auto-detected)
2. **Local multimodal generation on AMD Radeon GPU**
   - FLUX.1-schnell / FLUX.1-dev / FLUX.2-dev via PyTorch ROCm + diffusers
   - FLUX.1-schnell **Q4_0 GGUF** via stable-diffusion.cpp for a
     quantized, low-VRAM, fast path
   - 4:3 scene images that fill the slide exactly (center-crop, no distortion)
3. **Caption engine built for short video**
   - Big readable titles/subtitles with dark bars (WeChat/Douyin-safe layout)
   - Auto-shrink fonts to fit the bars; **CJK-aware fonts + character-based
     wrapping** (Chinese has no spaces — handled correctly)
4. **Job pipeline with progress** — asynchronous job queue, poll status,
   download the finished MP4, optional **YouTube upload** with auto
   title/description/tags (public/private).
5. **Style customization** — image prompts follow a consistent
   infographic/neon style; every stage is parameterized
   (`--provider`, `--steps`, `--width/height`, `--max-vram`, seeds).

---

## 4. Models & Local Deployment Plan

### 4.1 Models

| Model | Role | Params | Why this model |
|---|---|---|---|
| **FLUX.1-schnell** | scene images (primary) | 12B, **4-step distilled** | 4 steps instead of 28 → ~7× faster image gen on the Radeon GPU |
| FLUX.1-dev / FLUX.2-dev | scene images (quality mode) | 12B, 28 steps | Higher fidelity when quality matters more than speed |
| FLUX.1-schnell **Q4_0 GGUF** | scene images (quantized) | 12B → **~4-bit** | ~4× smaller on disk/VRAM; fast CPU/GPU mix (t5xxl on CPU, diffusion on GPU) |
| LLM (openrouter/auto-beta or local) | script + scene planning | 7–70B | Only text planning; optional — see 4.3 |

### 4.2 Local deployment plan (AMD Radeon GPU + ROCm)

1. **Install ROCm stack** on the AMD GPU host:
   - `amdgpu-install` (ROCm driver + runtime) or ROCm container
   - `pip install torch --index-url https://download.pytorch.org/whl/rocmX.Y`
   - `pip install diffusers transformers accelerate`
2. **Download models** (HF mirror friendly): `fluxreel download flux [schnell|dev|2-dev]`
   → stores under `/root/FLUX.*`; or GGUF files for the sd-cpp path
   (`fluxreel img` local setup with `SDCPP_BIN` / `SDCPP_MODEL_DIR`).
3. **Verify GPU**: `fluxreel info` shows GPU, PyTorch build, VRAM, disk.
4. **Start the service**: `fluxreel server --port 8000` (web UI + REST API).
5. **Optional LLM**: `vllm serve <model> --dtype auto` or llama.cpp on ROCm,
   point `MODEL` env var at it; otherwise use OpenRouter.

### 4.3 Note on LLM placement

The **core multimodal inference (image generation) always runs on the AMD
Radeon GPU**. The text script/scene planning is a small, optional step:
it can run on a local LLM served by vLLM/llama.cpp on the same Radeon GPU
(fully offline), or use an API model for convenience. Neither path affects
the GPU image-generation core.

---

## 5. Inference-Speed Optimizations on AMD Radeon GPU / ROCm

| # | Optimization | Effect | Where |
|---|---|---|---|
| 1 | **Distilled model** — FLUX.1-schnell at **4 steps** (vs 28 for dev) | ~7× fewer denoising steps per image | `MODEL_PARAMS["schnell"]` |
| 2 | **Quantization** — Q4_0 GGUF (4-bit) via stable-diffusion.cpp | ~4× smaller weights → lower VRAM, faster memory-bound decode; diffusion runs on GPU (`backend=diffusion=cuda,clip=cpu,vae=cuda,t5xxl=cpu`) | sd-cpp provider |
| 3 | **VAE tiling** (`--vae-tiling`) | Decodes large latents in tiles → avoids OOM, allows larger images on small VRAM | sd-cpp provider |
| 4 | **VRAM budget control** (`--max-vram`) | Keeps GPU headroom for desktop use; stable on 12 GB Radeon-class cards | sd-cpp provider |
| 5 | **Parallel scene generation** — 5 scenes generated concurrently (`ThreadPoolExecutor`) with a lock serializing GPU runs | Overlaps LLM/CPU work with GPU; total latency ≈ 1 image + scheduling, not 5 | `video.py` Step 2 |
| 6 | **Early encoding** — each slide encoded to H.264 segment right after composition, then **concat without re-encode** | Fast, deterministic 30 fps timeline; no full-video re-encode | `video.py` Step 4 |
| 7 | **Resolution discipline** — 4:3 scene images (960×720 / 1024×768) sized for the 1080×810 slide area | Minimum pixels for the target, less GPU time per image | providers |
| 8 | **Optional ROCm LLM serving** (vLLM with continuous batching / llama.cpp) | Low-latency local script generation on the same GPU | deployment |

### Measured characteristics

- One scene image: **~2–15 s** depending on variant (4-step schnell ≈ seconds;
  28-step dev slower), single Radeon GPU, resolution 960×720…1024×768.
- Full 15 s video (5 slides, H.264 1080×1920@30): assembly is CPU/ffmpeg-bound
  (~10–30 s) and independent of GPU steps.
- Working set: FLUX.1-schnell Q4_0 GGUF fits comfortably in 12 GB-class VRAM
  with `--max-vram 10` + VAE tiling.

---

## 6. Submission Package Index

| File | Requirement |
|---|---|
| `01_project_specification.md` | This document (§1–§5) |
| Source repo (`README.md`, `fluxreel/`, `pyproject.toml`, `fabfile.py`) | Requirement 2 — source code, README with env config/startup guide/dependencies |
| `02_slides.md` → Marp PPT | Requirement 4 — PPT (Marp) |
| `03_demo_video.md` | Requirement 3 — 3–5 min demo video script (video file to be provided) |
