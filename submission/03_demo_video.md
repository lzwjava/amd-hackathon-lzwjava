# Demo Video Script (3–5 min) — to be recorded

**Format:** 1080×1920 or 1920×1080 screen recording with voice-over (English or 中文).
**Goal:** demonstrate the real flow on the AMD Radeon GPU, from command line / GUI to final result.

---

## Timeline

### 0:00 – 0:25 · Intro
- Project name: **FluxReel** — AMD GPU short-form video creation tool (Track 1)
- Hook: "One topic → a complete 15-second vertical video, fully local on an AMD Radeon GPU"
- Show the web UI at `http://localhost:8000`

### 0:25 – 0:55 · Environment check
- Terminal: `fluxreel info` → show GPU name (AMD Radeon), ROCm/PyTorch build, VRAM, disk
- Terminal: `fluxreel --help` or brief repo tree

### 0:55 – 1:40 · Web UI — generate a video (default OpenRouter images is optional; use Local GPU for the AMD path)
- Type topic: **"How GPUs work"** (English) — later also show a Chinese topic **"GPU是什么？"**
- Click **Generate ✨** → article appears in the content editor
- Review scenes → choose **🖥️ Local GPU** provider
- Click **🎬 Generate Video**

### 1:40 – 3:00 · Job progress on AMD GPU
- Show the polling status: `pending → processing`
- (While waiting) narrate the pipeline: LLM script → 5 scene prompts → FLUX.1-schnell on Radeon GPU → slide composition → ffmpeg assembly
- Optional: show terminal/server log lines of the generation (`Generating image (local GPU, schnell, 4 steps)`)

### 3:00 – 3:50 · Result
- Job completes → play the **15 s video** in the page
- Download MP4; open in a player; point out layout: 4:3 centered image, big title/subtitle bars
- Optional: show a **Chinese** topic video to demonstrate CJK captions

### 3:50 – 4:30 · Performance & optimization
- `fluxreel img "..." --provider sdcpp` quantized path (Q4_0 GGUF) — show wall-clock time per image
- Compare/mention: 4-step schnell vs 28-step dev, Q4_0 4-bit quantization, VAE tiling, VRAM budget
- Show `nvidia-smi`-equivalent (AMD: `rocm-smi`) during generation

### 4:30 – 5:00 · Close
- Summary slide/overlay: local AMD Radeon GPU + ROCm, zero API cost, bilingual, private
- Thank you + team

---

## Recording tips

- Close chat apps to free VRAM if using the sd-cpp path on a shared desktop GPU.
- Pre-warm the model once before recording so the demo run is smooth (first load downloads/caches).
- Use a topic you know generates well (e.g. "How GPUs work", "What is RISC-V", "Attention Mechanism").
- Show **real timestamps** from the job log for authenticity.
- Keep video ≤ 5 minutes.
