import math
from pathlib import Path

import matplotlib.pyplot as plt
import trimesh
from matplotlib.patches import Polygon as MplPolygon
from shapely.geometry import Polygon

# 手描き図 (ピンク) の 2D プロファイルを Z 方向に押し出した中実形状。
# 本体は幅8mm・高さ32mm。左の2角は直角。
# 右下は R2 で丸め (下辺 6mm = 8-2)。右上は x=10 まで 2mm 突起 (上辺 10mm)、
# 突起の付け根を凹 R2 (左右反転) で本体右辺 (x=8) につなぐ。右辺直線部 28mm。

THK = 60.0  # 押し出し (Z)

# ---- 寸法 (mm) ----
W = 8.0  # 本体の幅 (左辺 x=0 〜 右辺 x=8)
H = 32.0  # 高さ
R = 2.0  # 丸め半径
BUMP = 2.0  # 右上の突起量 (右へ) → 上辺は W+BUMP = 10mm

# 生成物 (png / stl) の出力先 (gitignore 対象)
OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)
NAME = Path(__file__).stem
PNG = OUT / f"{NAME}.png"
STL = OUT / f"{NAME}.stl"


def arc(c, a0, a1, r, n=16):
    return [
        (c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a)))
        for a in (a0 + (a1 - a0) * i / n for i in range(n + 1))
    ]


# ---- プロファイル (反時計回り) ----
P = [
    (0.0, 0.0),  # 左下 (直角)
    (W - R, 0.0),  # 下辺 (6mm) → (6,0)
    *arc((W - R, R), 270, 360, R),  # 右下を R2 で丸め: (6,0)→(8,2)
    (W, H - R),  # 右辺 (x=8) を上へ → (8,30) ※直線部 28mm
    *arc((W + BUMP, H - R), 180, 90, R),  # 凹 R2 で突起へ: (8,30)→(10,32)
    (0.0, H),  # 上辺 (10mm) → 左上 (直角)
]

# ---- 画像出力 ----
xs, ys = zip(*P)
fig, ax = plt.subplots(figsize=(4, 10))
ax.add_patch(MplPolygon(P, closed=True, facecolor="#f06fb0", edgecolor="#7a1444", linewidth=1.2))
ax.set_xlim(-2, W + BUMP + 2)
ax.set_ylim(-2, H + 2)
ax.set_aspect("equal")
ax.axis("off")
fig.savefig(PNG, dpi=150, bbox_inches="tight")
plt.close(fig)
print("Shape built", len(P), "pts ->", PNG)

# ---- STL出力 (Pを厚さTHKで押し出し) ----
poly = Polygon(P)
if not poly.is_valid:
    poly = poly.buffer(0)
mesh = trimesh.creation.extrude_polygon(poly, height=THK)
mesh.export(STL)
print(
    f"STL exported -> {STL}  watertight=",
    mesh.is_watertight,
    " volume=",
    round(mesh.volume, 1),
    "mm^3",
)
