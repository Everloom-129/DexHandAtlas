# DexHand Atlas — Simulation Asset Index

Curated, **verified** sources for 3D simulation assets of the hands covered in
this atlas. Priority order: **USD** (OpenUSD / NVIDIA Isaac Sim) → **URDF** →
**MJCF** (MuJoCo) → mesh (STL/OBJ/glTF).

This index is surfaced interactively on the site: click any hand photo in
[`dexhand_hardware_review.html`](dexhand_hardware_review.html) or
[`dex_hand_products.html`](dex_hand_products.html) to open the **2.5D viewer**,
which rotates the hand and lists both upstream links **and** the copy vendored in
this repo. The same data lives in [`dexhand_viewer.js`](dexhand_viewer.js) (`DB`).

**Vendored copies — every hand has a USD.** The freely-licensed assets are
downloaded and organized per hand under [`/assets/`](assets/) — browse and
download via [`assets/index.html`](assets/index.html) (file tree + per-file
links; machine-readable [`assets/manifest.json`](assets/manifest.json)). ~14
hands, ~270 MB; heavy CAD (STEP/`.f3d`) and demo videos pruned; each folder keeps
its upstream `LICENSE`.

**Wuji ships native USD.** For the other 13 hands a USD was **generated from the
vendored URDF/MJCF + meshes** by [`assets/tools/urdf_mjcf_to_usd.py`](assets/tools/urdf_mjcf_to_usd.py)
(OpenUSD + trimesh): kinematic Xform hierarchy in rest pose, per-link visual
meshes baked as `UsdGeomMesh`, primitive geoms as USD shapes, **Z-up / meters**.
Output lands at `assets/<hand>/usd/<hand>.usd`. These are geometry scenes, not
physics articulations (no joint drives) — for full PhysX articulation, import the
URDF in Isaac Sim. Barrett & Schunk had only `*.urdf.xacro` with ROS `$(find)`
substitutions, so their USD is an un-posed mesh assembly (meshes at authored
origins). All 14 USD validated openable at hand scale (0.2–0.5 m).

> **Not vendored (links only):** native USD for Shadow / Allegro / Robotiq lives
> on NVIDIA Nucleus (served to Isaac Sim, not plain HTTP); Unitree Dex5 USD and
> the Inspire MJCF are likewise fetched at runtime / still in review. Open those
> in Isaac Sim or clone the linked repo. Tesollo's repo required auth at fetch
> time. Formats/licenses are vendor- or community-reported.

| Hand | Vendor | USD | URDF | MJCF | Source |
|---|---|:--:|:--:|:--:|---|
| Shadow Dexterous Hand | Shadow Robot | ✅ | – | ✅ | [Isaac Sim](https://docs.isaacsim.omniverse.nvidia.com/5.0.0/assets/usd_assets_robots.html) · [Menagerie](https://github.com/google-deepmind/mujoco_menagerie/tree/main/shadow_hand) |
| Allegro Hand | Wonik | ✅ | ✅ | ✅ | [Isaac Sim](https://docs.isaacsim.omniverse.nvidia.com/5.0.0/assets/usd_assets_robots.html) · [Menagerie](https://github.com/google-deepmind/mujoco_menagerie/tree/main/wonik_allegro) · [IsaacGymEnvs](https://github.com/isaac-sim/IsaacGymEnvs/tree/main/assets/urdf/kuka_allegro_description) |
| LEAP Hand | CMU | ✅¹ | ✅ | ✅ | [LEAP_Hand_Sim](https://github.com/leap-hand/LEAP_Hand_Sim) · [Isaac Lab](https://github.com/leap-hand/LEAP_Hand_Isaac_Lab) · [Menagerie](https://github.com/google-deepmind/mujoco_menagerie/tree/main/leap_hand) |
| ORCA Hand | ETH SRL | – | ✅ | ✅ | [orcahand_description](https://github.com/orcahand/orcahand_description) · [orca_sim](https://github.com/orcahand/orca_sim) |
| RUKA Hand | NYU | – | – | ✅ | [ruka-hand/RUKA](https://github.com/ruka-hand/RUKA/tree/main/assets/xml) |
| Inspire RH56 | Inspire (因时) | – | ✅ | (PR) | [Unitree xr_teleoperate](https://github.com/unitreerobotics/xr_teleoperate/tree/main/assets/inspire_hand) · [dex-urdf²](https://github.com/dexsuite/dex-urdf) |
| PSYONIC Ability Hand | PSYONIC | – | ✅ | ✅ | [ability-hand-api](https://github.com/psyonicinc/ability-hand-api/tree/master/URDF) |
| Unitree Dex3-1 | Unitree | ✅ | ✅ | – | [unitree_sim_isaaclab](https://github.com/unitreerobotics/unitree_sim_isaaclab) · [xr_teleoperate](https://github.com/unitreerobotics/xr_teleoperate/tree/main/assets/unitree_hand) |
| Unitree Dex5 | Unitree | ✅ | – | – | [unitree_sim_isaaclab](https://github.com/unitreerobotics/unitree_sim_isaaclab) |
| Wuji Hand | Wuji Tech | ✅ | ✅ | ✅ | [wuji-hand-description](https://github.com/wuji-technology/wuji-hand-description) · [mujoco-sim](https://github.com/wuji-technology/mujoco-sim) |
| Faive Hand | Mimic / ETH | – | ✅ | ✅ | [faive_gym_oss](https://github.com/srl-ethz/faive_gym_oss) |
| Schunk SVH | SCHUNK | – | ✅ | – | [schunk_svh_ros_driver](https://github.com/SCHUNK-SE-Co-KG/schunk_svh_ros_driver) (GPL-3.0) |
| Tesollo DG-3F | Tesollo | – | ✅ | – | [DELTO_B_ROS2](https://github.com/Tesollo-Delto/DELTO_B_ROS2) |
| Barrett Hand | Barrett | – | ✅ | – | [barrett_hand_common](https://github.com/RobotnikAutomation/barrett_hand_common) |
| Robotiq 2F-85/140 | Robotiq | ✅ | ✅ | ✅ | Isaac Sim built-in · [Menagerie](https://github.com/google-deepmind/mujoco_menagerie/tree/main/robotiq_2f85) |
| Clone Robotics hand | Clone | – | – | – | No public sim asset (proprietary myofiber) |

The **USD** column above marks *native upstream* USD. Independently, a **generated
USD is vendored for every hand in this table except Clone** (see
`assets/<hand>/usd/`) — so a USD is available even where upstream ships only
URDF/MJCF.

¹ LEAP USD is produced by `LEAP_Hand_Isaac_Lab` via URDF→USD on import (no standalone `.usd`).
² `dexsuite/dex-urdf` Inspire URDF is **CC BY-NC-SA 4.0 (non-commercial)**. Inspire MJCF is an open Menagerie PR — confirm it is merged before relying on it.

## Native USD vs. conversion-needed

- **Native USD, usable directly:** Shadow, Allegro, Robotiq (NVIDIA Isaac Sim
  Nucleus), Unitree Dex3-1 & Dex5 (official Isaac Lab repo), **Wuji** (official
  multi-format repo).
- **USD via official URDF→USD on import:** LEAP Hand.
- **URDF/MJCF only → convert for Isaac:** ORCA, RUKA, Inspire, Ability, Schunk,
  Faive, Barrett, Tesollo. MJCF-equipped ones can use the OpenUSD
  `mujoco-usd-converter`; URDF-only ones go through the Isaac URDF Importer.
- **No public asset:** Clone Robotics.

## Hands with no public asset (viewer still opens & rotates the photo)

Sharpa, RobotEra XHAND1, BrainCo Revo, Linker Hand, Agile Hand, AgiBot OmniHand,
Daxo Muscle, Boston Dynamics Atlas, qb SoftHand2 — proprietary or not yet released.
