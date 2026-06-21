#!/usr/bin/env python3
"""Bake a hand's vendored URDF or MJCF (+ meshes) into a single USD file.

Produces a real, openable .usd: kinematic Xform hierarchy in rest pose,
per-link visual meshes baked as UsdGeomMesh, Z-up / meters. Not a physics
articulation (no joint drives) but a valid USD scene of the hand."""
import os, sys, glob, math, re
import numpy as np
import xml.etree.ElementTree as ET
import trimesh
from pxr import Usd, UsdGeom, Gf, Vt

def rpy_to_quat(r, p, y):
    cr, sr = math.cos(r/2), math.sin(r/2)
    cp, sp = math.cos(p/2), math.sin(p/2)
    cy, sy = math.cos(y/2), math.sin(y/2)
    # URDF: R = Rz(y) Ry(p) Rx(r)
    w = cr*cp*cy + sr*sp*sy
    x = sr*cp*cy - cr*sp*sy
    yq = cr*sp*cy + sr*cp*sy
    z = cr*cp*sy - sr*sp*cy
    return (w, x, yq, z)

def euler_to_quat(a, b, c, seq="xyz"):
    # intrinsic, applied in given order
    def axq(ax, ang):
        h = ang/2; s = math.sin(h)
        v = {"x": (s,0,0), "y": (0,s,0), "z": (0,0,s)}[ax]
        return (math.cos(h),) + v
    def mul(q1, q2):
        w1,x1,y1,z1 = q1; w2,x2,y2,z2 = q2
        return (w1*w2-x1*x2-y1*y2-z1*z2,
                w1*x2+x1*w2+y1*z2-z1*y2,
                w1*y2-x1*z2+y1*w2+z1*x2,
                w1*z2+x1*y2-y1*x2+z1*w2)
    q = (1,0,0,0)
    for ax, ang in zip(seq, (a,b,c)):
        q = mul(q, axq(ax, ang))
    return q

def sanitize(name):
    n = re.sub(r'[^A-Za-z0-9_]', '_', name or "node")
    if n and n[0].isdigit():
        n = "_" + n
    return n or "node"

class MeshIndex:
    """Resolve a referenced mesh path to an actual file under the hand folder."""
    def __init__(self, root):
        self.root = root
        self.by_base = {}
        for ext in ("stl","STL","obj","OBJ","dae","DAE","ply","PLY","msh"):
            for p in glob.glob(os.path.join(root, "**", "*."+ext), recursive=True):
                self.by_base.setdefault(os.path.basename(p).lower(), []).append(p)
    def resolve(self, ref, hint_dir=None):
        ref = ref.split("package://", 1)[-1]
        base = os.path.basename(ref).lower()
        cands = self.by_base.get(base, [])
        if not cands:
            return None
        if len(cands) == 1:
            return cands[0]
        # disambiguate by shared path tokens (e.g. left/right)
        want = set(re.split(r'[\\/_.-]', ref.lower()))
        if hint_dir:
            want |= set(re.split(r'[\\/_.-]', hint_dir.lower()))
        best, bestscore = cands[0], -1
        for c in cands:
            toks = set(re.split(r'[\\/_.-]', c.lower()))
            s = len(want & toks)
            if s > bestscore:
                best, bestscore = c, s
        return best

def load_mesh(path, scale):
    m = trimesh.load(path, force='mesh', process=False)
    if m is None or not hasattr(m, "vertices") or len(m.vertices) == 0:
        return None
    v = np.asarray(m.vertices, dtype=np.float64)
    if scale is not None:
        v = v * np.asarray(scale, dtype=np.float64)
    f = np.asarray(m.faces, dtype=np.int64)
    return v, f

# ---------------- USD builders ----------------
def add_xform(stage, path, xyz, quat):
    xf = UsdGeom.Xform.Define(stage, path)
    if xyz is not None and any(abs(c) > 1e-12 for c in xyz):
        xf.AddTranslateOp().Set(Gf.Vec3d(float(xyz[0]), float(xyz[1]), float(xyz[2])))
    if quat is not None:
        w,x,y,z = quat
        if abs(w-1) > 1e-9 or abs(x)+abs(y)+abs(z) > 1e-9:
            xf.AddOrientOp().Set(Gf.Quatf(float(w), Gf.Vec3f(float(x), float(y), float(z))))
    return xf

def add_mesh(stage, path, verts, faces):
    m = UsdGeom.Mesh.Define(stage, path)
    m.CreatePointsAttr(Vt.Vec3fArray([Gf.Vec3f(*map(float, v)) for v in verts]))
    m.CreateFaceVertexCountsAttr(Vt.IntArray([3]*len(faces)))
    m.CreateFaceVertexIndicesAttr(Vt.IntArray(faces.reshape(-1).tolist()))
    m.CreateSubdivisionSchemeAttr().Set(UsdGeom.Tokens.none)
    return m

# ---------------- URDF ----------------
def parse_urdf(path):
    root = ET.parse(path).getroot()
    links = {}   # name -> list of (meshfile, scale, origin_xyz, origin_quat)
    for link in root.findall("link"):
        vis = []
        for v in link.findall("visual"):
            o = v.find("origin")
            xyz = [0,0,0]; quat = (1,0,0,0)
            if o is not None:
                xyz = [float(t) for t in (o.get("xyz","0 0 0")).split()]
                r,p,y = [float(t) for t in (o.get("rpy","0 0 0")).split()]
                quat = rpy_to_quat(r,p,y)
            geo = v.find("geometry")
            mesh = geo.find("mesh") if geo is not None else None
            if mesh is None:
                continue
            sc = mesh.get("scale")
            scale = [float(t) for t in sc.split()] if sc else None
            vis.append((mesh.get("filename"), scale, xyz, quat))
        links[link.get("name")] = vis
    joints = []  # (parent, child, xyz, quat)
    children = set()
    for j in root.findall("joint"):
        p = j.find("parent"); c = j.find("child")
        if p is None or c is None: continue
        o = j.find("origin")
        xyz = [0,0,0]; quat = (1,0,0,0)
        if o is not None:
            xyz = [float(t) for t in (o.get("xyz","0 0 0")).split()]
            r,pp,y = [float(t) for t in (o.get("rpy","0 0 0")).split()]
            quat = rpy_to_quat(r,pp,y)
        joints.append((p.get("link"), c.get("link"), xyz, quat))
        children.add(c.get("link"))
    roots = [l for l in links if l not in children] or list(links)[:1]
    cmap = {}
    for par,ch,xyz,q in joints:
        cmap.setdefault(par, []).append((ch,xyz,q))
    return links, cmap, roots

def build_from_urdf(stage, parent_path, link, links, cmap, midx, urdf_dir, depth=0):
    for mi,(mf, scale, oxyz, oq) in enumerate(links.get(link, [])):
        real = midx.resolve(mf, urdf_dir)
        if not real: continue
        try:
            res = load_mesh(real, scale)
        except Exception:
            res = None
        if not res: continue
        vp = parent_path + "/" + sanitize(link) + "_vis%d" % mi
        add_xform(stage, vp, oxyz, oq)
        add_mesh(stage, vp + "/mesh", res[0], res[1])
    for ch, xyz, q in cmap.get(link, []):
        cp = parent_path + "/" + sanitize(ch)
        add_xform(stage, cp, xyz, q)
        build_from_urdf(stage, cp, ch, links, cmap, midx, urdf_dir, depth+1)

# ---------------- MJCF ----------------
def mjcf_root(path, _depth=0):
    """Parse an MJCF file, inlining <include file=...> recursively (merge)."""
    root = ET.parse(path).getroot()
    base = os.path.dirname(path)
    if _depth > 8:
        return root
    def inline(elem):
        newchildren = []
        for child in list(elem):
            if child.tag == "include":
                f = child.get("file")
                tgt = os.path.join(base, f) if f else None
                if tgt and os.path.exists(tgt):
                    inc = mjcf_root(tgt, _depth+1)
                    newchildren.extend(list(inc))
                # drop the include element itself
            else:
                inline(child)
                newchildren.append(child)
        elem[:] = newchildren
    inline(root)
    return root

def parse_compiler(root):
    comp = root.find("compiler")
    meshdir = "."; angle = "degree"
    if comp is not None:
        meshdir = comp.get("meshdir", comp.get("assetdir", "."))
        angle = comp.get("angle", "degree")
    return meshdir, angle

def default_mesh_scales(root):
    """class name -> mesh scale, from <default> blocks (MuJoCo inheritance)."""
    scales = {}
    def walk(elem, inherited):
        cls = elem.get("class")
        cur = inherited
        mesh = elem.find("mesh")
        if mesh is not None and mesh.get("scale"):
            cur = [float(t) for t in mesh.get("scale").split()]
            if cls:
                scales[cls] = cur
            else:
                scales["__global__"] = cur
        for d in elem.findall("default"):
            walk(d, cur)
    for d in root.findall("default"):
        walk(d, None)
    return scales

def collect_geom_defaults(root):
    """class -> resolved <geom> default attrs (with MuJoCo inheritance)."""
    gd = {}
    def walk(elem, inh, inh_cls):
        cls = elem.get("class") or inh_cls
        g = dict(inh)
        ge = elem.find("geom")
        if ge is not None:
            g.update(ge.attrib)
        gd[cls if cls else "__global__"] = g
        for d in elem.findall("default"):
            walk(d, g, cls)
    for d in root.findall("default"):
        walk(d, {}, None)
    return gd

def gattr(geom, name, childclass, gd):
    v = geom.get(name)
    if v is not None:
        return v
    cls = geom.get("class") or childclass
    if cls and cls in gd and name in gd[cls]:
        return gd[cls][name]
    if "__global__" in gd and name in gd["__global__"]:
        return gd["__global__"][name]
    return None

def mjcf_assets(root):
    """mesh-name -> (file, explicit_scale, class). Name defaults to file stem."""
    assets = {}
    for asset in root.findall("asset"):
        for a in asset.findall("mesh"):
            f = a.get("file")
            if not f and not a.get("name"):
                continue
            name = a.get("name") or os.path.splitext(os.path.basename(f))[0]
            sc = a.get("scale")
            scale = [float(t) for t in sc.split()] if sc else None
            assets[name] = (f, scale, a.get("class"))
    return assets

def body_transform(elem, angle):
    pos = [float(t) for t in (elem.get("pos","0 0 0")).split()]
    quat = (1,0,0,0)
    if elem.get("quat"):
        q = [float(t) for t in elem.get("quat").split()]
        quat = (q[0], q[1], q[2], q[3])
    elif elem.get("euler"):
        e = [float(t) for t in elem.get("euler").split()]
        if angle == "degree": e = [math.radians(v) for v in e]
        quat = euler_to_quat(e[0], e[1], e[2])
    return pos, quat

def build_from_mjcf_body(stage, parent_path, body, assets, midx, angle, dscales, gd, childclass=None, idx=0):
    name = sanitize(body.get("name") or ("body%d" % idx))
    pos, quat = body_transform(body, angle)
    bp = parent_path + "/" + name
    add_xform(stage, bp, pos, quat)
    cc = body.get("childclass") or childclass
    gi = 0
    for geom in body.findall("geom"):
        cls = (geom.get("class") or cc or "")
        if "collision" in cls.lower():
            continue
        mref = gattr(geom, "mesh", cc, gd)
        gtype = gattr(geom, "type", cc, gd) or ("mesh" if mref else "sphere")
        gpos, gquat = body_transform(geom, angle)
        if gtype == "mesh":
            mname = mref
            if not mname or mname not in assets:
                continue
            f, scale, mcls = assets[mname]
            if scale is None:
                scale = dscales.get(mcls) or dscales.get("__global__")
            real = midx.resolve(f) if f else midx.resolve(mname)
            if not real: continue
            try:
                res = load_mesh(real, scale)
            except Exception:
                res = None
            if not res: continue
            gp = bp + "/geom%d" % gi; gi += 1
            add_xform(stage, gp, gpos, gquat)
            add_mesh(stage, gp + "/mesh", res[0], res[1])
        elif gtype in ("box", "sphere", "cylinder", "capsule", "ellipsoid"):
            szs = gattr(geom, "size", cc, gd)
            sz = [float(t) for t in (szs or "0").split()]
            if not sz or geom.get("fromto"):  # fromto primitives unsupported
                continue
            gp = bp + "/geom%d" % gi; gi += 1
            xf = add_xform(stage, gp, gpos, gquat)
            if gtype == "box":
                while len(sz) < 3: sz.append(sz[-1])
                c = UsdGeom.Cube.Define(stage, gp + "/prim"); c.CreateSizeAttr(1.0)
                UsdGeom.Xform(c).AddScaleOp().Set(Gf.Vec3f(2*sz[0], 2*sz[1], 2*sz[2]))
            elif gtype == "sphere":
                s = UsdGeom.Sphere.Define(stage, gp + "/prim"); s.CreateRadiusAttr(float(sz[0]))
            elif gtype == "ellipsoid":
                while len(sz) < 3: sz.append(sz[-1])
                s = UsdGeom.Sphere.Define(stage, gp + "/prim"); s.CreateRadiusAttr(1.0)
                UsdGeom.Xform(s).AddScaleOp().Set(Gf.Vec3f(sz[0], sz[1], sz[2]))
            else:  # cylinder / capsule -> cylinder approx (axis Z)
                r = float(sz[0]); hh = float(sz[1]) if len(sz) > 1 else r
                cy = UsdGeom.Cylinder.Define(stage, gp + "/prim")
                cy.CreateRadiusAttr(r); cy.CreateHeightAttr(2*hh)
                cy.CreateAxisAttr(UsdGeom.Tokens.z)
    for ci, child in enumerate(body.findall("body")):
        build_from_mjcf_body(stage, bp, child, assets, midx, angle, dscales, gd, cc, ci)

# ---------------- driver ----------------
JUNK = re.compile(r'(sphere|cube|stair|block|prism|pyr|dodec|tetra|hex|'
                  r'object|book|scene|floor|table|simple_|clutter|ball|'
                  r'transmission|gazebo|\.materials)', re.I)

def _score(path, folder):
    p = path.lower(); base = os.path.basename(folder).lower()
    s = 0
    if "right" in p: s += 5
    if "left" in p: s -= 4
    if "collision" in p: s -= 3
    if "hand" in p: s += 2
    if base in p: s += 2
    if "standalone" in p or "alone" in p: s += 2
    s -= len(path) * 0.001
    return s

def expand_xacro(path):
    import xacro
    try:
        doc = xacro.process_file(path, mappings={})
        return doc.toprettyxml(indent='  ')
    except Exception:
        return None

def pick_source(folder):
    urdfs = [p for p in glob.glob(os.path.join(folder, "**", "*.urdf"), recursive=True)
             if not JUNK.search(p)]
    if urdfs:
        urdfs.sort(key=lambda p: -_score(p, folder))
        # verify it actually has mesh visuals
        for u in urdfs:
            try:
                links, _, _ = parse_urdf(u)
                if any(links.values()):
                    return ("urdf", u)
            except Exception:
                continue
    # MJCF
    mjcfs = []
    for x in glob.glob(os.path.join(folder, "**", "*.xml"), recursive=True):
        if JUNK.search(x): continue
        try:
            r = mjcf_root(x)
        except Exception:
            continue
        if r.tag != "mujoco": continue
        wb = r.find("worldbody")
        if wb is not None and wb.find("body") is not None:
            mjcfs.append(x)
    if mjcfs:
        mjcfs.sort(key=lambda p: -_score(p, folder))
        return ("mjcf", mjcfs[0])
    # xacro fallback (barrett, schunk)
    xac = [p for p in glob.glob(os.path.join(folder, "**", "*.urdf.xacro"), recursive=True)
           if not JUNK.search(p)]
    xac += [p for p in glob.glob(os.path.join(folder, "**", "*.xacro"), recursive=True)
            if not JUNK.search(p) and p not in xac]
    if xac:
        xac.sort(key=lambda p: -_score(p, folder))
        for x in xac:
            txt = expand_xacro(x)
            if not txt: continue
            tmp = os.path.join(folder, "usd", "_expanded.urdf")
            os.makedirs(os.path.dirname(tmp), exist_ok=True)
            with open(tmp, "w") as fh: fh.write(txt)
            try:
                links, _, _ = parse_urdf(tmp)
                if any(links.values()):
                    return ("urdf", tmp)
            except Exception:
                pass
            os.remove(tmp)
    return (None, None)

def mesh_dump(folder, hand):
    """Last resort: assemble all visual meshes in the folder into one USD at
    their authored origins. No kinematic posing, but a valid USD of the parts."""
    out_dir = os.path.join(folder, "usd"); os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, hand + ".usd")
    if os.path.exists(out): os.remove(out)
    # prefer visual meshes (skip *_collision, *convex*)
    files = []
    for ext in ("stl","STL","obj","OBJ","dae","DAE","ply","PLY"):
        files += glob.glob(os.path.join(folder, "**", "*."+ext), recursive=True)
    files = [f for f in files if not re.search(r'(collision|convex|_col\b)', f, re.I)]
    # de-dup by basename
    seen = {}
    for f in files:
        seen.setdefault(os.path.basename(f).lower(), f)
    files = list(seen.values())
    if not files:
        return None
    stage = Usd.Stage.CreateNew(out)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    root = UsdGeom.Xform.Define(stage, "/" + sanitize(hand))
    stage.SetDefaultPrim(root.GetPrim())
    n = 0
    for f in sorted(files):
        try:
            res = load_mesh(f, None)
        except Exception:
            res = None
        if not res: continue
        add_mesh(stage, "/" + sanitize(hand) + "/" + sanitize(os.path.splitext(os.path.basename(f))[0]), res[0], res[1])
        n += 1
    if n == 0:
        os.remove(out); return None
    stage.GetRootLayer().Save()
    print(f"  [{hand}] mesh-dump (no kinematics) -> usd/{hand}.usd  ({n} meshes, {os.path.getsize(out)/1e6:.1f} MB)")
    return out

def convert(folder, hand):
    kind, src = pick_source(folder)
    if not src:
        r = mesh_dump(folder, hand)
        if not r:
            print(f"  [{hand}] no URDF/MJCF/mesh found — skip")
        return r
    midx = MeshIndex(folder)
    out_dir = os.path.join(folder, "usd")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, hand + ".usd")
    if os.path.exists(out): os.remove(out)
    stage = Usd.Stage.CreateNew(out)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    rootname = sanitize(hand)
    root_path = "/" + rootname
    rootxf = UsdGeom.Xform.Define(stage, root_path)
    stage.SetDefaultPrim(rootxf.GetPrim())
    try:
        if kind == "urdf":
            links, cmap, roots = parse_urdf(src)
            for rl in roots:
                rp = root_path + "/" + sanitize(rl)
                UsdGeom.Xform.Define(stage, rp)
                build_from_urdf(stage, rp, rl, links, cmap, midx, os.path.dirname(src))
        else:
            r = mjcf_root(src)
            meshdir, angle = parse_compiler(r)
            assets = mjcf_assets(r)
            dscales = default_mesh_scales(r)
            gd = collect_geom_defaults(r)
            wb = r.find("worldbody")
            for bi, b in enumerate(wb.findall("body")):
                build_from_mjcf_body(stage, root_path, b, assets, midx, angle, dscales, gd, None, bi)
    except Exception as e:
        print(f"  [{hand}] ERROR during build: {e}")
        return None
    nmesh = sum(1 for p in stage.Traverse() if p.GetTypeName() == "Mesh")
    if nmesh == 0:
        print(f"  [{hand}] built 0 meshes from {os.path.relpath(src, folder)} — skip")
        os.remove(out)
        return None
    stage.GetRootLayer().Save()
    tmp = os.path.join(out_dir, "_expanded.urdf")
    if os.path.exists(tmp):
        os.remove(tmp)
    sz = os.path.getsize(out)
    print(f"  [{hand}] {kind} {os.path.relpath(src, folder)} -> usd/{hand}.usd  ({nmesh} meshes, {sz/1e6:.1f} MB)")
    return out

if __name__ == "__main__":
    assets_root = sys.argv[1] if len(sys.argv) > 1 else "assets"
    skip = {"wuji"}  # ships native USD
    hands = sorted(d for d in os.listdir(assets_root)
                   if os.path.isdir(os.path.join(assets_root, d)))
    ok = 0
    for h in hands:
        if h in skip:
            print(f"  [{h}] native USD already present — keep")
            continue
        if convert(os.path.join(assets_root, h), h):
            ok += 1
    print(f"\nConverted {ok} hands to USD.")
