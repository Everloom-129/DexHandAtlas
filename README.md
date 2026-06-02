# DexHand Atlas

**A field guide to the dexterous robotic hand landscape — the hardware that grasps, the market that sells it, and the benchmarks that measure it.**

### 🌐 Live site → **https://everloom-129.github.io/DexHandAtlas/**

Compiled from public vendor data, primary papers, and third-party listings.
Maintained by **Jie Wang**, GRASP Lab, University of Pennsylvania.

**Bilingual (EN / 中文).** Every page has an EN ⇄ 中文 toggle in the top-right corner. 中文入口：[index.zh.html ↗](https://everloom-129.github.io/DexHandAtlas/index.zh.html)

---

## The Atlas

| Volume | Review | Live page |
|--------|--------|-----------|
| **I · Hardware** | Dexterous Hand Hardware — Landscape Review. 20+ hands across commercial specialists, humanoid-integrated end-effectors, and the research / open-source / biomimetic frontier. Compared on DOF, actuation topology, tactile stack, and product philosophy, with photos and vendor links. | [Read ↗](https://everloom-129.github.io/DexHandAtlas/dexhand_hardware_review_standalone.html) |
| **II · Market** | Hands on the Market (灵巧手产品市场一览). 14 buyable dexterous hands with product images, finger/DOF counts, origin, and reference prices — from $2k open-source kits to $110k research benchmarks, sources linked per row. | [Browse ↗](https://everloom-129.github.io/DexHandAtlas/dex_hand_products.html) |
| **III · Benchmarks** | Dexterous Manipulation Benchmarks — A Literature Review. Simulation suites, real-world task sets, and datasets used to measure in-hand manipulation and grasping. | [Read ↗](https://everloom-129.github.io/DexHandAtlas/dexhand_benchmarks.html) · [中文 ↗](https://everloom-129.github.io/DexHandAtlas/dexhand_benchmarks.zh.html) |

---

## Repository layout

```
index.html                              # landing page (GitHub Pages entry)
dexhand_hardware_review.html            # Vol I — linked images (images/ folder)
dexhand_hardware_review_standalone.html # Vol I — single-file (images inlined)
dex_hand_products.html                  # Vol II — products table
dexhand_benchmarks.html                 # Vol III — benchmarks literature review
*.zh.html                               # Simplified-Chinese twin of every page
images/                                 # product / hand photos
```

The **`*_standalone.html`** files inline every image as base64 — open them anywhere, no folder needed. The plain `.html` versions are lighter and load images from `images/`. Each page also has a Simplified-Chinese twin (`*.zh.html`); the EN ⇄ 中文 toggle links the two.

## Notes on the data

Figures are vendor- or paper-reported and inconsistently defined (active DOF vs. total joints; fingertip vs. whole-hand force; list vs. quote-only prices). Treat single-number comparisons as approximate, and confirm anything decision-critical against the original source — every entry links back to one.

All trademarks, product names, and images belong to their respective owners; images are reproduced for reference and identification only.
