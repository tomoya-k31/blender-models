import math
from pathlib import Path

import matplotlib.pyplot as plt
import trimesh
from matplotlib.patches import Polygon as MplPolygon
from shapely.geometry import Polygon

# 手描き図 (ピンク) の 2D プロファイルを Z 方向に押し出した中実の板。
# 左の2角は直角、右の2角を R9 で丸める。
# 左辺 49mm = R9 + 右辺直線31mm + R9。上辺/下辺の直線部 26mm。右辺 x = 26+9 = 35。

THK = 82.0  # 押し出し (Z)

# ---- 寸法 (mm) ----
LEFT_H = 49.0  # 左辺 (縦・直線) の高さ
TOP_W = 26.0  # 上辺/下辺の直線部の幅
RIGHT_H = 31.0  # 右辺 (縦・直線) の高さ
R = 9.0  # 右の2角の丸め半径 (9 + 31 + 9 = 49)

RX = TOP_W + R  # 右辺の x 位置 = 35

# 生成物 (png / stl) の出力先 (gitignore 対象)
OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)
NAME = Path(__file__).stem
PNG = OUT / f"{NAME}.png"
STL = OUT / f"{NAME}.stl"


def arc(c, a0, a1, r, n=24):
    return [
        (c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a)))
        for a in (a0 + (a1 - a0) * i / n for i in range(n + 1))
    ]


# ---- プロファイル (反時計回り) ----
P = [
    (0.0, 0.0),  # 左下 (直角)
    (TOP_W, 0.0),  # 下辺 (26mm) → (26,0)
    *arc((TOP_W, R), 270, 360, R),  # 右下を R9: (26,0)→(35,9)
    (RX, R + RIGHT_H),  # 右辺を上へ (31mm) → (35,40)
    *arc((TOP_W, R + RIGHT_H), 0, 90, R),  # 右上を R9: (35,40)→(26,49)
    (0.0, LEFT_H),  # 上辺 (26mm) → 左上 (0,49) (直角)
]

# ---- 画像出力 ----
xs, ys = zip(*P)
fig, ax = plt.subplots(figsize=(5, 8))
ax.add_patch(MplPolygon(P, closed=True, facecolor="#f06fb0", edgecolor="#7a1444", linewidth=1.2))
ax.set_xlim(min(xs) - 3, max(xs) + 3)
ax.set_ylim(min(ys) - 3, max(ys) + 3)
ax.set_aspect("equal")
ax.axis("off")
fig.savefig(PNG, dpi=150, bbox_inches="tight")
plt.close(fig)
print("Rounded panel built", len(P), "pts ->", PNG)

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
