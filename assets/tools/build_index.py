#!/usr/bin/env python3
"""Regenerate assets/index.html + assets/manifest.json from the folder tree."""
import os, json, html
ROOT = os.path.join(os.path.dirname(__file__), "..")
META = {
 "shadow":("Shadow Dexterous Hand","Shadow Robot","MuJoCo Menagerie (Apache-2.0)"),
 "allegro":("Allegro Hand","Wonik Robotics","MuJoCo Menagerie (BSD-2)"),
 "leap":("LEAP Hand","CMU","MuJoCo Menagerie (MIT)"),
 "orca":("ORCA Hand","ETH SRL","orcahand_description v2 (MIT)"),
 "ruka":("RUKA Hand","NYU","ruka-hand/RUKA"),
 "inspire":("Inspire RH56","Inspire 因时","Unitree xr_teleoperate (RH56DFX)"),
 "ability":("PSYONIC Ability Hand","PSYONIC","ability-hand-api (URDF + MuJoCo)"),
 "unitree_dex":("Unitree Dex3-1","Unitree","Unitree xr_teleoperate"),
 "wuji":("Wuji Hand","Wuji Tech","wuji-hand-description (MIT) — native USD"),
 "faive":("Faive Hand","Mimic / ETH","faive_gym_oss (Apache-2.0)"),
 "schunk":("Schunk SVH","SCHUNK","schunk_svh_description (GPL-3.0)"),
 "barrett":("Barrett Hand","Barrett","barrett_hand_common (BSD-3)"),
 "brainco":("BrainCo Revo","BrainCo 强脑","Unitree xr_teleoperate"),
 "robotiq":("Robotiq 2F-85","Robotiq","MuJoCo Menagerie (BSD-2)"),
}
def human(n):
    for u in ["B","K","M"]:
        if n<1024: return f"{n:.0f}{u}" if u!="B" else f"{n}{u}"
        n/=1024
    return f"{n:.1f}G"
hands=sorted([d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT,d)) and d!="tools"])
manifest={}; rows=[]
for h in hands:
    base=os.path.join(ROOT,h); files=[]
    for dp,_,fns in os.walk(base):
        for fn in fns:
            p=os.path.join(dp,fn); files.append((os.path.relpath(p,base), os.path.getsize(p)))
    files.sort(); fmts=set()
    for rel,_ in files:
        e=rel.lower().rsplit(".",1)[-1]
        if e in ("usd","usda","usdc"): fmts.add("USD")
        elif e=="urdf": fmts.add("URDF")
        elif e=="xml": fmts.add("MJCF")
        elif e in ("stl","obj","dae","glb","ply"): fmts.add("MESH")
    title,vendor,src=META.get(h,(h,"",""))
    manifest[h]={"title":title,"vendor":vendor,"source":src,"formats":sorted(fmts),
                 "usd":[r for r,_ in files if r.lower().split('.')[-1] in ("usd","usda","usdc")],
                 "files":[r for r,_ in files]}
    lis=[f'<li><a href="{html.escape(h+"/"+rel)}">{html.escape(rel)}</a><span class="sz">{human(sz)}</span></li>' for rel,sz in files]
    badges="".join(f'<span class="fmt {f.lower()}">{f}</span>' for f in sorted(fmts))
    rows.append(f'''<section id="{h}" class="hand">
  <h2>{html.escape(title)} <small>{html.escape(vendor)}</small></h2>
  <p class="src">{badges} &middot; {html.escape(src)} &middot; <code>assets/{h}/</code> &middot; {len(files)} files</p>
  <ul class="files">{''.join(lis)}</ul>
</section>''')
json.dump(manifest, open(os.path.join(ROOT,"manifest.json"),"w"), indent=1, ensure_ascii=False)
page=f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DexHand Atlas — Vendored Simulation Assets</title>
<style>
body{{margin:0;background:#0c0e10;color:#e8e4dc;font:15px/1.6 'Archivo',system-ui,sans-serif}}
.wrap{{max-width:1000px;margin:0 auto;padding:48px 24px 80px}}
h1{{font:300 40px/1 'Fraunces',Georgia,serif;margin:0 0 8px}}
.lead{{color:#9aa2a8;max-width:72ch;margin-bottom:8px}}
a{{color:#6fd0c8;text-decoration:none}} a:hover{{color:#f4b96b}}
.back{{font:600 13px/1 system-ui;display:inline-block;margin-bottom:28px;color:#e0a45c}}
.toc{{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 34px}}
.toc a{{font:500 12px/1 'JetBrains Mono',monospace;border:1px solid #3a444c;border-radius:3px;padding:7px 10px;color:#e8e4dc}}
.toc a:hover{{border-color:#6fd0c8}}
.hand{{border-top:1px solid #262d33;padding:22px 0}}
.hand h2{{font:400 24px/1.1 'Fraunces',Georgia,serif;margin:0 0 4px}}
.hand h2 small{{font:400 13px/1 'JetBrains Mono',monospace;color:#8a929a;margin-left:8px}}
.src{{font:12px/1.5 'JetBrains Mono',monospace;color:#8a929a;margin:0 0 12px}}
.src code{{color:#e0a45c}}
.fmt{{display:inline-block;font:700 10px/1 'JetBrains Mono',monospace;color:#0c0e10;background:#6fd0c8;border-radius:3px;padding:3px 6px;margin-right:4px}}
.fmt.urdf{{background:#e0a45c}}.fmt.mjcf{{background:#86b06a}}.fmt.mesh{{background:#9d8fc4}}
ul.files{{list-style:none;margin:0;padding:0;columns:2;column-gap:28px}}
ul.files li{{break-inside:avoid;display:flex;justify-content:space-between;gap:10px;padding:3px 0;border-bottom:1px solid #181c20}}
ul.files li a{{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.sz{{color:#8a929a;font:11px/1.6 'JetBrains Mono',monospace;flex-shrink:0}}
@media(max-width:680px){{ul.files{{columns:1}}}}
</style></head><body><div class="wrap">
<a class="back" href="../index.html">&larr; DexHand Atlas</a>
<h1>Vendored Simulation Assets</h1>
<p class="lead">Open-source 3D sim assets organized per hand under <code>/assets/</code>. <b>Every hand has a USD</b> (Wuji ships native USD; the rest were converted from the vendored URDF/MJCF + meshes by <a href="tools/urdf_mjcf_to_usd.py">tools/urdf_mjcf_to_usd.py</a> — Z-up, meters, rest pose). Click any file to download. See <a href="../ASSETS.md">ASSETS.md</a> for upstream sources &amp; licenses.</p>
<div class="toc">{''.join(f'<a href="#{h}">{html.escape(META.get(h,(h,))[0])}</a>' for h in hands)}</div>
{''.join(rows)}
</div></body></html>'''
open(os.path.join(ROOT,"index.html"),"w").write(page)
print("regenerated index.html + manifest.json for", len(hands), "hands")
print("USD present for:", sum(1 for h in hands if manifest[h]["usd"]), "hands")
