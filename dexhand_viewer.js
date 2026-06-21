/* ============================================================================
   DexHand Atlas — 2.5D hand viewer + simulation-asset index
   ----------------------------------------------------------------------------
   Self-contained, no dependencies. Include on any page that has hand photos
   carrying class "ethumb" (or any <img data-hand="...">). The script:
     1. builds a modal turntable that gives a single 2D photo a 2.5D depth +
        rotation feel (auto-spin + drag-to-rotate + pointer parallax);
     2. attaches a per-hand panel listing publicly downloadable simulation
        assets (USD / URDF / MJCF / mesh) with verified source links.
   Asset links are vendor- / community-reported; see notes per entry.
   Bilingual: picks EN / 中文 strings from <html lang>.
   ========================================================================== */
(function () {
  "use strict";

  var ZH = (document.documentElement.lang || "").toLowerCase().indexOf("zh") === 0;

  var T = ZH ? {
    kick: "细察 · 2.5D",
    assets: "仿真资源",
    drag: "拖动旋转 · 释放回正",
    spin: "自动旋转",
    none: "暂无公开仿真资源（专有方案，或尚未发布）。",
    close: "关闭",
    tag: "2.5D 展示"
  } : {
    kick: "Inspect · 2.5D",
    assets: "Simulation assets",
    drag: "drag to rotate · release to settle",
    spin: "auto-spin",
    none: "No public simulation asset found — proprietary, or not yet released.",
    close: "Close",
    tag: "2.5D view"
  };

  /* --- asset database, keyed by image file basename ----------------------- */
  // group = one physical hand; an image may cover several (open-source bundles).
  var DB = {
    "shadow.png": {
      title: "Shadow · Allegro · PSYONIC",
      org: "the benchmark / crossover platforms",
      groups: [
        { name: "Shadow Dexterous Hand", assets: [
          { fmt: "USD", src: "NVIDIA Isaac Sim", note: "official · Robots/ShadowHand", url: "https://docs.isaacsim.omniverse.nvidia.com/5.0.0/assets/usd_assets_robots.html" },
          { fmt: "MJCF", src: "MuJoCo Menagerie", note: "official assets · Apache-2.0", url: "https://github.com/google-deepmind/mujoco_menagerie/tree/main/shadow_hand" }
        ]},
        { name: "Allegro Hand (Wonik)", assets: [
          { fmt: "USD", src: "NVIDIA Isaac Sim", note: "official · Robots/Allegro", url: "https://docs.isaacsim.omniverse.nvidia.com/5.0.0/assets/usd_assets_robots.html" },
          { fmt: "MJCF", src: "MuJoCo Menagerie", note: "Allegro v3 · BSD-2", url: "https://github.com/google-deepmind/mujoco_menagerie/tree/main/wonik_allegro" },
          { fmt: "URDF", src: "IsaacGymEnvs", note: "community", url: "https://github.com/isaac-sim/IsaacGymEnvs/tree/main/assets/urdf/kuka_allegro_description" }
        ]},
        { name: "PSYONIC Ability Hand", assets: [
          { fmt: "URDF", src: "ability-hand-api", note: "official · L+R", url: "https://github.com/psyonicinc/ability-hand-api/tree/master/URDF" },
          { fmt: "MJCF", src: "ability-hand-api", note: "official · sim touch", url: "https://github.com/psyonicinc/ability-hand-api" }
        ]}
      ]
    },
    "orca.webp": {
      title: "LEAP · ORCA · RUKA",
      org: "the open-source accessibility wave",
      groups: [
        { name: "LEAP Hand (CMU)", assets: [
          { fmt: "URDF", src: "LEAP_Hand_Sim", note: "official · MIT", url: "https://github.com/leap-hand/LEAP_Hand_Sim" },
          { fmt: "USD", src: "LEAP Isaac Lab", note: "URDF→USD on import", url: "https://github.com/leap-hand/LEAP_Hand_Isaac_Lab" },
          { fmt: "MJCF", src: "MuJoCo Menagerie", note: "16-DOF · MIT", url: "https://github.com/google-deepmind/mujoco_menagerie/tree/main/leap_hand" }
        ]},
        { name: "ORCA Hand (ETH SRL)", assets: [
          { fmt: "URDF", src: "orcahand_description", note: "official · MIT · 17-DOF", url: "https://github.com/orcahand/orcahand_description" },
          { fmt: "MJCF", src: "orca_sim", note: "official · MuJoCo", url: "https://github.com/orcahand/orca_sim" }
        ]},
        { name: "RUKA Hand (NYU)", assets: [
          { fmt: "MJCF", src: "ruka-hand/RUKA", note: "official · 15-DOF tendon", url: "https://github.com/ruka-hand/RUKA/tree/main/assets/xml" }
        ]}
      ]
    },
    "clone.jpg": {
      title: "Clone · Faive / Mimic",
      org: "the biomimetic frontier",
      groups: [
        { name: "Clone Robotics hand", assets: [] },
        { name: "Faive Hand (Mimic / ETH)", assets: [
          { fmt: "MJCF", src: "faive_gym_oss", note: "official · Apache-2.0", url: "https://github.com/srl-ethz/faive_gym_oss" },
          { fmt: "URDF", src: "faive_gym_oss", note: "official · IsaacGym", url: "https://github.com/srl-ethz/faive_gym_oss" }
        ]}
      ]
    },
    "wuji.webp": {
      title: "Wuji Hand", org: "Wuji Tech · Shenzhen",
      groups: [{ name: "Wuji Hand (20-DOF direct-drive)", assets: [
        { fmt: "USD", src: "wuji-hand-description", note: "official · MIT · native USD (L+R)", url: "https://github.com/wuji-technology/wuji-hand-description" },
        { fmt: "URDF", src: "wuji-hand-description", note: "official · MIT", url: "https://github.com/wuji-technology/wuji-hand-description" },
        { fmt: "MJCF", src: "wuji mujoco-sim", note: "official · MIT", url: "https://github.com/wuji-technology/mujoco-sim" }
      ]}]
    },
    "inspire-rh56h1.webp": {
      title: "Inspire RH56", org: "因时机器人 · Beijing",
      groups: [{ name: "Inspire RH56 series", assets: [
        { fmt: "URDF", src: "Unitree xr_teleoperate", note: "RH56DFX as shipped on G1", url: "https://github.com/unitreerobotics/xr_teleoperate/tree/main/assets/inspire_hand" },
        { fmt: "URDF", src: "dexsuite/dex-urdf", note: "community · CC BY-NC-SA (non-commercial)", url: "https://github.com/dexsuite/dex-urdf" }
      ]}]
    },
    "unitree-dex3.jpg": {
      title: "Unitree Dex3-1", org: "Unitree · Hangzhou",
      groups: [{ name: "Unitree Dex3-1", assets: [
        { fmt: "USD", src: "unitree_sim_isaaclab", note: "official · native USD (PhysX)", url: "https://github.com/unitreerobotics/unitree_sim_isaaclab" },
        { fmt: "URDF", src: "Unitree xr_teleoperate", note: "official · L/R + meshes", url: "https://github.com/unitreerobotics/xr_teleoperate/tree/main/assets/unitree_hand" }
      ]}]
    },
    "unitree-dex5.webp": {
      title: "Unitree Dex5", org: "Unitree · Hangzhou",
      groups: [{ name: "Unitree Dex5", assets: [
        { fmt: "USD", src: "unitree_sim_isaaclab", note: "official · Dex5-URDF-R.usd", url: "https://github.com/unitreerobotics/unitree_sim_isaaclab" }
      ]}]
    },
    "allegro.webp": {
      title: "Allegro Hand", org: "Wonik Robotics",
      groups: [{ name: "Allegro Hand (16-DOF)", assets: [
        { fmt: "USD", src: "NVIDIA Isaac Sim", note: "official · Robots/Allegro", url: "https://docs.isaacsim.omniverse.nvidia.com/5.0.0/assets/usd_assets_robots.html" },
        { fmt: "MJCF", src: "MuJoCo Menagerie", note: "BSD-2", url: "https://github.com/google-deepmind/mujoco_menagerie/tree/main/wonik_allegro" },
        { fmt: "URDF", src: "IsaacGymEnvs", note: "community", url: "https://github.com/isaac-sim/IsaacGymEnvs/tree/main/assets/urdf/kuka_allegro_description" }
      ]}]
    },
    "leap.webp": {
      title: "LEAP Hand", org: "CMU · Shaw, Pathak",
      groups: [{ name: "LEAP Hand (16-DOF, <$2k)", assets: [
        { fmt: "URDF", src: "LEAP_Hand_Sim", note: "official · MIT", url: "https://github.com/leap-hand/LEAP_Hand_Sim" },
        { fmt: "USD", src: "LEAP Isaac Lab", note: "URDF→USD on import", url: "https://github.com/leap-hand/LEAP_Hand_Isaac_Lab" },
        { fmt: "MJCF", src: "MuJoCo Menagerie", note: "MIT", url: "https://github.com/google-deepmind/mujoco_menagerie/tree/main/leap_hand" }
      ]}]
    },
    "psyonic.jpg": {
      title: "PSYONIC Ability Hand", org: "PSYONIC",
      groups: [{ name: "Ability Hand", assets: [
        { fmt: "URDF", src: "ability-hand-api", note: "official · L+R", url: "https://github.com/psyonicinc/ability-hand-api/tree/master/URDF" },
        { fmt: "MJCF", src: "ability-hand-api", note: "official · sim touch", url: "https://github.com/psyonicinc/ability-hand-api" }
      ]}]
    },
    "schunk.webp": {
      title: "Schunk SVH", org: "SCHUNK SE",
      groups: [{ name: "Schunk SVH (5-finger)", assets: [
        { fmt: "URDF", src: "schunk_svh_ros_driver", note: "official · GPL-3.0 · needs conversion for USD", url: "https://github.com/SCHUNK-SE-Co-KG/schunk_svh_ros_driver" }
      ]}]
    },
    "tesollo.webp": {
      title: "Tesollo DG-3F", org: "Tesollo · Delto",
      groups: [{ name: "Delto DG-3F", assets: [
        { fmt: "URDF", src: "DELTO_B_ROS2", note: "official · delto_3f_description", url: "https://github.com/Tesollo-Delto/DELTO_B_ROS2" }
      ]}]
    }
    /* Hands with no public sim asset (proprietary / unreleased) deliberately
       omitted from DB — the viewer still opens and shows T.none for them:
       sharpa, xhand1, brainco-revo2, linker-l20, agile, omnihand, daxo,
       atlas, qb-softhand2, etc. */
  };

  function basename(src) {
    return (src || "").split("/").pop().split("?")[0].split("#")[0];
  }

  /* --- build modal -------------------------------------------------------- */
  var overlay = document.createElement("div");
  overlay.className = "hv-overlay";
  overlay.setAttribute("role", "dialog");
  overlay.setAttribute("aria-modal", "true");
  overlay.innerHTML =
    '<button class="hv-close" aria-label="' + T.close + '">&times;</button>' +
    '<div class="hv-dialog">' +
      '<div class="hv-stage"><div class="hv-card">' +
        '<div class="hv-depth"></div>' +
        '<img alt="">' +
        '<div class="hv-sheen"></div><div class="hv-edge"></div>' +
      '</div></div>' +
      '<div class="hv-panel">' +
        '<div class="hv-kick">' + T.kick + '</div>' +
        '<h3></h3><div class="hv-org"></div>' +
        '<div class="hv-badges"></div>' +
        '<div class="hv-assets"><div class="hv-lbl">' + T.assets + '</div><div class="hv-links"></div></div>' +
        '<div class="hv-hint"><span>⟲</span><span>' + T.drag + '</span></div>' +
        '<button class="hv-spinbtn" type="button">' + T.spin + '</button>' +
      '</div>' +
    '</div>';
  document.body.appendChild(overlay);

  var card = overlay.querySelector(".hv-card");
  var stage = overlay.querySelector(".hv-stage");
  var vimg = overlay.querySelector(".hv-card img");
  var elTitle = overlay.querySelector(".hv-panel h3");
  var elOrg = overlay.querySelector(".hv-org");
  var elBadges = overlay.querySelector(".hv-badges");
  var elLinks = overlay.querySelector(".hv-links");
  var spinBtn = overlay.querySelector(".hv-spinbtn");

  /* --- turntable state ---------------------------------------------------- */
  var REDUCE = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var open = false, autospin = true, dragging = false;
  var t0 = 0, yaw = 0, pitch = 0, dragYaw = 0, dragPitch = 0, px = 0, py = 0, raf = 0;

  function frame(now) {
    if (!open) return;
    if (!t0) t0 = now;
    var t = (now - t0) / 1000;
    var autoYaw = autospin && !dragging && !REDUCE ? Math.sin(t * 0.7) * 22 : 0;
    var autoPitch = autospin && !dragging && !REDUCE ? Math.sin(t * 0.45) * 4 : 0;
    // ease manual drag toward 0 when released
    if (!dragging) { dragYaw *= 0.92; dragPitch *= 0.92; }
    yaw = autoYaw + dragYaw + px * 10;
    pitch = autoPitch + dragPitch - py * 8;
    var sheenX = 50 - yaw * 1.6;
    card.style.transform = "rotateY(" + yaw.toFixed(2) + "deg) rotateX(" + pitch.toFixed(2) + "deg)";
    var sheen = card.querySelector(".hv-sheen");
    if (sheen) sheen.style.backgroundPosition = sheenX + "% 50%";
    raf = requestAnimationFrame(frame);
  }

  /* --- pointer parallax + drag ------------------------------------------- */
  stage.addEventListener("pointermove", function (e) {
    var r = stage.getBoundingClientRect();
    px = (e.clientX - r.left) / r.width - 0.5;
    py = (e.clientY - r.top) / r.height - 0.5;
  });
  stage.addEventListener("pointerleave", function () { px = 0; py = 0; });
  stage.addEventListener("pointerdown", function (e) {
    dragging = true; stage.setPointerCapture(e.pointerId);
    stage.style.cursor = "grabbing";
    var sx = e.clientX, sy = e.clientY, y0 = dragYaw, p0 = dragPitch;
    function mv(ev) { dragYaw = y0 + (ev.clientX - sx) * 0.5; dragPitch = p0 - (ev.clientY - sy) * 0.35; }
    function up() {
      dragging = false; stage.style.cursor = "grab";
      stage.removeEventListener("pointermove", mv);
      window.removeEventListener("pointerup", up);
    }
    stage.addEventListener("pointermove", mv);
    window.addEventListener("pointerup", up);
  });
  stage.style.cursor = "grab";

  /* --- open / close ------------------------------------------------------- */
  function render(name) {
    var d = DB[name];
    var title = d ? d.title : (name.replace(/\.[a-z0-9]+$/i, "").replace(/[-_]/g, " "));
    elTitle.textContent = title;
    elOrg.textContent = d ? d.org : "";
    // badges: distinct formats available
    var fmts = {};
    if (d) d.groups.forEach(function (g) { g.assets.forEach(function (a) { fmts[a.fmt] = 1; }); });
    elBadges.innerHTML = Object.keys(fmts).map(function (f) {
      return '<span class="hv-fmt ' + f.toLowerCase() + '">' + f + '</span>';
    }).join("");
    elBadges.style.gap = "6px";
    // asset links
    elLinks.innerHTML = "";
    var any = false;
    if (d) d.groups.forEach(function (g) {
      if (d.groups.length > 1) {
        var h = document.createElement("div");
        h.className = "hv-lbl"; h.style.marginTop = "14px"; h.style.color = "var(--amber)";
        h.textContent = g.name;
        elLinks.appendChild(h);
      }
      if (!g.assets.length) {
        var n = document.createElement("div");
        n.className = "hv-none"; n.textContent = T.none;
        elLinks.appendChild(n);
        return;
      }
      g.assets.forEach(function (a) {
        any = true;
        var link = document.createElement("a");
        link.className = "hv-asset"; link.href = a.url;
        link.target = "_blank"; link.rel = "noopener";
        link.innerHTML =
          '<span class="hv-fmt ' + a.fmt.toLowerCase() + '">' + a.fmt + '</span>' +
          '<span class="hv-meta"><span class="hv-src">' + a.src + '</span>' +
          '<span class="hv-note">' + a.note + '</span></span>' +
          '<span class="hv-arrow">↗</span>';
        elLinks.appendChild(link);
      });
    });
    if (!d || (!any && d.groups.every(function (g) { return !g.assets.length; }))) {
      if (!elLinks.querySelector(".hv-none")) {
        var n2 = document.createElement("div");
        n2.className = "hv-none"; n2.textContent = T.none;
        elLinks.appendChild(n2);
      }
    }
  }

  function openViewer(imgEl) {
    vimg.src = imgEl.currentSrc || imgEl.src;
    vimg.alt = imgEl.alt || "";
    render(basename(imgEl.getAttribute("src") || imgEl.src));
    overlay.classList.add("open");
    document.body.style.overflow = "hidden";
    open = true; t0 = 0; dragYaw = 0; dragPitch = 0;
    cancelAnimationFrame(raf); raf = requestAnimationFrame(frame);
  }
  function closeViewer() {
    overlay.classList.remove("open");
    document.body.style.overflow = "";
    open = false; cancelAnimationFrame(raf);
  }

  overlay.querySelector(".hv-close").addEventListener("click", closeViewer);
  overlay.addEventListener("click", function (e) { if (e.target === overlay) closeViewer(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && open) closeViewer(); });
  spinBtn.addEventListener("click", function () {
    autospin = !autospin;
    spinBtn.style.borderColor = autospin ? "" : "var(--cyan)";
    spinBtn.style.color = autospin ? "" : "var(--cyan)";
  });

  /* --- wire up hand photos ----------------------------------------------- */
  function wire() {
    var imgs = document.querySelectorAll("img.ethumb, img.thumb, img[data-hand]");
    imgs.forEach(function (img) {
      if (img.dataset.hvWired) return;
      img.dataset.hvWired = "1";
      img.setAttribute("tabindex", "0");
      img.setAttribute("role", "button");
      img.style.cursor = "zoom-in";
      img.addEventListener("click", function () { openViewer(img); });
      img.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openViewer(img); }
      });
    });
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", wire);
  } else { wire(); }
})();
