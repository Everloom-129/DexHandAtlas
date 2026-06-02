# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static GitHub Pages site hosting a set of hand-authored research documents about the dexterous robotic hand landscape ("DexHand Atlas"). There is **no build system, no package manager, no tests, and no shared stylesheet** — every page is a self-contained `.html` file with its own inline `<style>` (and occasional inline `<script>`). Author/attribution: Jie Wang, GRASP Lab, University of Pennsylvania.

- Repo: `github.com/Everloom-129/DexHandAtlas`
- Live: `https://everloom-129.github.io/DexHandAtlas/` (Pages serves `main` branch root; `index.html` is the entry point)

## Preview & deploy

- **Preview locally:** open the file in a browser, or `python3 -m http.server` from the repo root and visit `http://localhost:8000/`. Use a server (not `file://`) so the relative `images/` paths resolve.
- **Deploy:** commit and push to `main`. Pages rebuilds automatically (~1–2 min). There is no CI. To check build/live status: `gh api repos/Everloom-129/DexHandAtlas/pages/builds/latest`.

## Image handling

The image-heavy reviews reference photos via `src="images/..."`. GitHub Pages serves the `images/` folder, so these resolve on the live site and under a local `http.server` (but not over `file://`).

**Gotcha — detect MIME by magic bytes, not file extension.** Several files in `images/` are mislabeled (e.g. `inspire-rh56h1.webp` is actually JPEG, `psyonic.jpg` is actually WebP). Browsers sniff content so the live pages render fine regardless, but any tool that re-encodes an image must read the leading bytes (`\xFF\xD8\xFF`=jpeg, `\x89PNG`=png, `RIFF`+`WEBP`=webp) rather than trusting the extension.

## Bilingual (EN / 中文)

Every page has an English original and a Simplified-Chinese twin named `*.zh.html` (`index.zh.html`, `dexhand_hardware_review.zh.html`, `dex_hand_products.zh.html`, `dexhand_benchmarks.zh.html`).

- A fixed top-right `.langswitch` pill (CSS block inlined identically in every page's `<style>`) links each page to its counterpart: EN→中文, 中文→EN. Keep the round-trip consistent.
- `index.html` cards link to the **EN** pages; `index.zh.html` cards link to the **`.zh`** pages.
- To (re)translate: edit the EN linked source, then write the `.zh.html` by translating **only human-readable text** — prose, headings, table prose, `alt`, `<title>`, meta. Never touch tags, CSS, JS, `data-*` attribute values (the hardware comparison table's sort/filter keys off them), image paths, hrefs (except flipping the langswitch to the EN page), or brand / paper / arXiv names. Keep terminology consistent: 灵巧手 (dexterous hand), 自由度/DOF, 腱驱动 (tendon), 直驱 (direct-drive), 触觉 (tactile), 末端执行器 (end-effector), 基准 (benchmark).

All pages also ship `prefers-reduced-motion` handling, `:focus-visible` rings, a `<noscript>` reveal fallback (where scroll-reveal is used), and AA-contrast text tokens — preserve these when editing styles.

## Documents (volumes)

- `dexhand_hardware_review.html` — Vol I, hardware landscape; per-hand entry cards carry a photo + vendor website link.
- `dex_hand_products.html` — Vol II, buyable hands with images, reference prices, sources per row.
- `dexhand_benchmarks.html` (EN) + `dexbench_survey_sonnet.html` (中文) — Vol III, manipulation benchmarks literature review.

Note `index.html` and `dexhand_hardware_review.html` share a dark editorial look (Fraunces/Archivo/JetBrains Mono, amber+cyan, film-grain overlay); the product table and benchmark surveys use a lighter system-font theme. CSS is per-file, so changing one page's look does not affect others.

## Editorial constraints (content correctness)

- All specs and prices are **vendor- or paper-reported and inconsistently defined** (active DOF vs. total joints; fingertip vs. whole-hand force; list vs. quote-only prices). Present figures as approximate reference values, and keep every entry's link back to its original source.
- When adding a hand/product, prefer a real product image you have verified loads (vendor CDN or an aggregator such as humanoid.guide), download it into `images/`, then reference it via `src="images/FILE"`. Vendor sites frequently block hotlinking and serve JS-rendered/CDN-optimized images, so download with a browser `User-Agent` and validate with `file` before committing.
- Avoid nested `<a>` tags. The clickable cards in `index.html` are themselves `<a>` elements; putting another `<a>` inside one makes the browser close the card early and break the grid layout.
