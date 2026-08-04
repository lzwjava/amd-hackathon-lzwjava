---
marp: true
theme: default
paginate: true
header: "AMD AI DevMaster Hackathon — Track 1"
footer: "FluxReel · AMD Radeon GPU · ROCm"
size: 16:9
style: |
  section {
    background: linear-gradient(150deg, #0b0e15 0%, #141926 55%, #1a2130 100%);
    color: #f2f5fa;
    --color-background: #0b0e15;
    --color-foreground: #f2f5fa;
    --color-highlight: #ff5c4d;
    --color-dimmed: #93a0b3;
    --color-background-code: #131a27;
  }
  h1, h2, h3, h4, h5, h6 { color: #ffffff; }
  header, footer { color: var(--color-dimmed); }
  strong { color: #ffd57a; }
  li::marker { color: #ed1c24; }
  blockquote {
    background: rgba(255, 255, 255, 0.05);
    border-left: 0.35em solid #ed1c24;
    border-radius: 0.2em;
    color: #f2f5fa;
  }
  table th { background: #1e2637; color: #ffffff; }
  table td { border-color: #2b3446; }
  code {
    background: #131a27;
    color: #ffb86c;
  }
  pre {
    background: #0f1420;
    border: 1px solid #26304a;
  }
  a { color: #ff6a5e; }
---

<!-- _header: "" -->
<!-- _footer: "" -->
<!-- _paginate: false -->

![bg](cover.png)

---

# Problem & Opportunity

- Short video is the dominant content format (Douyin / WeChat Video Account / Reels)
- Creating an explainer video today = script + images + captions + music + editing → **hours**
- Existing tools either cost money per video (cloud APIs) or leak content to the cloud

> **FluxReel: one topic → a polished 15 s vertical video, fully local on an AMD Radeon GPU.**

- No per-video API cost
- Content stays on your machine
- Bilingual captions (EN / 中文)

---

# Pipeline Overview

```
Topic ─▶ ① LLM script      ─▶ ② Scene planner     ─▶ ③ Image generation
             (article)         5 scenes:              (AMD Radeon GPU · ROCm)
                                title / subtitle /         FLUX.1-schnell
                                image prompt               Q4_0 GGUF (4-bit)
                                                                 │
                                                                 ▼
   15 s MP4 ◀─ ⑤ ffmpeg assembly ◀─ ④ Slide composition ◀─ 5× 4:3 images
   1080×1920     H.264 · music        title bars (110px)     + captions
   30 fps        fade-out             CJK-aware fonts
```

---

# Core Capabilities

| Capability | Detail |
|---|---|
| **Topic → video** | LLM drafts article, planner makes 5 scenes (title/subtitle/prompt) |
| **Local AMD GPU inference** | FLUX.1-schnell / dev / 2-dev via PyTorch ROCm + diffusers |
| **Quantized fast path** | FLUX.1-schnell **Q4_0 GGUF** via stable-diffusion.cpp (ROCm/HIP) |
| **Caption engine** | Big readable bars, auto-shrink fonts, **CJK char-based wrapping** |
| **Job pipeline** | Async jobs, progress polling, MP4 download, optional YouTube upload |
| **Privacy** | Core generation local; no remote API required for image/video |

---

# Model Strategy

| Model | Role | Why |
|---|---|---|
| **FLUX.1-schnell** | images (default) | 12B, **4-step distilled** → ~7× faster than 28-step |
| FLUX.1-dev / 2-dev | images (quality) | 28 steps when fidelity matters |
| **FLUX.1-schnell Q4_0** | images (quantized) | **4-bit GGUF** → ~4× smaller, low-VRAM decode |
| vLLM / llama.cpp | script planning | Optional local LLM on the same Radeon GPU |

> Core multimodal inference runs **only on AMD Radeon GPU (ROCm)**.
> The LLM text step is optional and can also run locally.

---

# AMD Radeon GPU / ROCm Optimizations

1. **Distilled inference** — 4 steps instead of 28
2. **4-bit quantization** — Q4_0 GGUF (stable-diffusion.cpp), ~4× smaller
3. **VAE tiling** — decode in tiles, avoids OOM on small VRAM
4. **VRAM budget control** — `--max-vram`, stable on 12 GB-class cards
5. **Parallel scene generation** — 5 images overlapped (GPU-serialized lock)
6. **No-re-encode assembly** — per-slide H.264 segments + concat
7. **Sized resolutions** — 4:3 scenes matched to the slide area (fewer pixels = less GPU time)

---

# Demo Flow (3–5 min video)

1. `fluxreel info` — GPU / ROCm / PyTorch build check
2. `fluxreel server` → open the web UI at `:8000`
3. Type a topic (e.g. "How GPUs work" or "GPU是什么？")
4. Choose the **Local GPU** provider
5. Watch the job: script → 5× FLUX scenes on the Radeon GPU → assembly
6. Play & download the final 15 s video
7. (Optional) Quantized Q4_0 path + measured latency

---

# Results & Impact

- **15 s vertical video in minutes** — script, images, captions, music
- **Zero marginal cost** — local Radeon GPU, no API fees
- **Bilingual** — auto EN/中文 captions with proper CJK rendering
- **Private** — content never leaves the machine
- **Reusable** — REST API + CLI (`fluxreel img`, `fluxreel server`, `fluxreel download`)

---

<!-- _class: lead -->
# Thank You
## FluxReel — one topic, one AMD GPU, one video
