# DexHand Atlas — Simulation Asset Index

Curated, **verified** sources for 3D simulation assets of the hands covered in
this atlas. Priority order: **USD** (OpenUSD / NVIDIA Isaac Sim) → **URDF** →
**MJCF** (MuJoCo) → mesh (STL/OBJ/glTF).

This index is surfaced interactively on the site: click any hand photo in
[`dexhand_hardware_review.html`](dexhand_hardware_review.html) or
[`dex_hand_products.html`](dex_hand_products.html) to open the **2.5D viewer**,
which rotates the hand and lists its downloadable assets. The same data lives in
[`dexhand_viewer.js`](dexhand_viewer.js) (`DB` object).

> **Why links, not vendored binaries.** Most native USD lives on NVIDIA Nucleus
> (served to Isaac Sim, not plain HTTP), and the URDF/MJCF packages are whole git
> repos with mesh trees. Bundling them would blow past GitHub Pages' size budget
> and duplicate upstream licensing. Clone the linked repo (or open it in Isaac
> Sim) to get the actual files. Formats/licenses are vendor- or community-reported.

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
