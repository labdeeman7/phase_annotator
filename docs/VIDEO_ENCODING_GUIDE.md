# A Fundamentals Guide to Video Compression & Encoding (H.264)

This guide explains how digital video compression works, the difference between lossy and lossless methods, and why these concepts matter for surgical computer vision research and video annotation tools.

---

## 1. Why Video Needs Heavy Compression

Imagine storing raw uncompressed 1080p video at 30 frames per second (FPS):

$$\text{1 Frame} = 1920 \times 1080 \times 3 \text{ bytes (RGB)} = 6.22 \text{ MB}$$
$$\text{1 Second (30 FPS)} = 6.22 \text{ MB} \times 30 = 186.6 \text{ MB/sec}$$
$$\text{1 Minute} \approx 11.2 \text{ GB}$$
$$\text{1 Hour Operation} \approx 670 \text{ GB}$$

Without compression, a single 1-hour laparoscopic surgery recording would take **670 Gigabytes** of disk space!

---

## 2. Spatial vs. Temporal Redundancy

To reduce file size by 99% without losing visible quality, video encoders exploit two types of redundancy:

### A. Spatial Redundancy (Within a single frame)
In a surgical frame, large regions of pixels (like background liver tissue or dark abdominal cavity) are nearly identical. Instead of storing every pixel individually, spatial compression (like JPEG) compresses continuous regions of similar color.

### B. Temporal Redundancy (Across time)
In a surgical video at 30 FPS, the organ background changes very little between frame $t$ and frame $t+1$. Only the surgical tool (grasper, cautery hook) moves slightly. 
Instead of saving 30 full pictures every second, the encoder stores **one full picture** and then records only **motion vectors** (how pixel blocks moved) for subsequent frames!

---

## 3. The GOP Structure: I-Frames, P-Frames, and B-Frames

Modern codecs like H.264, H.265 (HEVC), and VP9 organize video into a **Group of Pictures (GOP)**:

```
[ I-Frame ] ───▶ [ P-Frame ] ───▶ [ B-Frame ] ───▶ [ P-Frame ] ───▶ [ I-Frame ]
 (Keyframe)       (Predicts from     (Predicts from     (Predicts from     (Keyframe)
  Full Image       previous frame)    past & future)     previous frame)    Full Image
```

1. **I-Frame (Intra-coded / Keyframe)**:
   * A complete, self-contained standalone image (similar to a high-quality JPEG).
   * Does NOT depend on any other frames.
   * **Crucial for seeking**: When you jump to a new timestamp in a video player, the player must jump to the nearest I-Frame first!
2. **P-Frame (Predicted frame)**:
   * Stores only the differences/changes relative to the *previous* frame using motion vectors.
   * Requires 50–80% less data than an I-frame.
3. **B-Frame (Bi-directional predicted frame)**:
   * Looks at both the *previous* frame AND the *future* frame to interpolate movement.
   * Offers the highest compression ratio.

---

## 4. Lossy vs. Lossless Compression

| Feature | Lossless Compression | Lossy Compression |
| :--- | :--- | :--- |
| **How it works** | Reversible math algorithms (like ZIP, HuffYUV, ProRes 4444 XQ). | Discards high-frequency visual details human eyes rarely notice (Discrete Cosine Transform + Quantization). |
| **Pixel Accuracy** | 100% exact mathematical match to raw camera sensor. | Approximated pixels (imperceptible to human eye at high bitrates). |
| **File Size** | Large (~50–100 GB/hour). | Small (~1–3 GB/hour). |
| **Common Codecs** | PNG sequences, HuffYUV, FFV1. | **H.264 (AVC)**, **H.265 (HEVC)**, VP9, AV1. |

---

## 5. Why Video Encoding Matters for Surgical AI & Annotators

1. **Frame Seeking Performance**:
   * If a video player seeks to Frame 1547, and Frame 1547 is a **P-frame**, the video player engine must decode the I-frame at Frame 1500 and rapidly step forward through 47 P-frames to render Frame 1547.
   * This is why video seeking can feel slightly laggy if keyframes (I-frames) are placed too far apart (e.g. every 10 seconds).
2. **Constant (CFR) vs. Variable Frame Rate (VFR)**:
   * **Constant Frame Rate (CFR)**: Exactly 30.000 frames every second. (Ideal for AI models like ResNet / Transformers).
   * **Variable Frame Rate (VFR)**: Frame rate fluctuates (e.g., drops to 22 FPS when OR camera lags).
   * Our domain utilities (`ms_to_frame`, `frame_to_ms`) rely on millisecond timecodes to ensure annotations remain frame-accurate even across VFR or CFR recordings!
