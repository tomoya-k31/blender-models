from pathlib import Path

import matplotlib.pyplot as plt
import trimesh
from matplotlib.patches import Polygon as MplPolygon
from shapely.geometry import box

# 手描き図 (ピンク) の 2D プロファイルを Z 方向に押し出した、中実の長方形。
# 外形 35mm × 5mm、上の2角のみ R2 (下の2角は直角)。上辺の直線部 = 35 - 2*R = 31mm。

THK = 3.0  # 押し出し (Z)

# ---- 寸法 (mm) ----
W = 35.0  # 外形の幅
H = 5.0  # 外形の高さ
R = 2.0  # 四隅の丸め半径 (上辺直線部 = W - 2R = 31mm)

# 生成物 (png / stl) の出力先 (gitignore 対象)
OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)
NAME = Path(__file__).stem
PNG = OUT / f"{NAME}.png"
STL = OUT / f"{NAME}.stl"

# ---- 角丸長方形 (内側の箱を R だけ膨らませる) → 下端を全幅矩形で埋めて下の角を直角に ----
poly = box(R, R, W - R, H - R).buffer(R, join_style="round", quad_segs=32)
poly = poly.union(box(0.0, 0.0, W, R))

# ---- 画像出力 ----
px, py = poly.exterior.xy
fig, ax = plt.subplots(figsize=(10, 3))
ax.add_patch(
    MplPolygon(list(zip(px, py)), closed=True, facecolor="#f06fb0", edgecolor="#7a1444", linewidth=1.2)
)
ax.set_xlim(-2, W + 2)
ax.set_ylim(-2, H + 2)
ax.set_aspect("equal")
ax.axis("off")
fig.savefig(PNG, dpi=150, bbox_inches="tight")
plt.close(fig)
print("Rounded rect built", len(poly.exterior.coords), "pts ->", PNG)

# ---- STL出力 (Pを厚さTHKで押し出し) ----
mesh = trimesh.creation.extrude_polygon(poly, height=THK)
mesh.export(STL)
print(
    f"STL exported -> {STL}  watertight=",
    mesh.is_watertight,
    " volume=",
    round(mesh.volume, 1),
    "mm^3",
)
