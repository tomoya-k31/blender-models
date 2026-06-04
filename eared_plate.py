import math
from pathlib import Path

import matplotlib.pyplot as plt
import trimesh
from matplotlib.patches import Polygon as MplPolygon
from shapely.geometry import Polygon

# 手描き図 (ピンク) の 2D プロファイルを Z 方向に押し出した中実の板。
# 35mm 幅 × 50mm 高さ。上部の左右の角が 2mm 外側へ張り出す段差。
# 出隅 (先端の角) は直角、入隅 (段差の付け根) を R2 のフィレットで丸める。

THK = 4.0  # 押し出し (Z)

# ---- 寸法 (mm) ----
W = 35.0  # 本体の幅
H = 50.0  # 全高 (張り出しの先端まで)
R = 2.0  # 入隅フィレットの半径
BUMP = 2.0  # 上部左右の張り出し量 (外側へ)

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
    (W, 0.0),  # 右下 (直角)
    (W, H - R),  # 右辺を上へ → (35,48)
    *arc((W + BUMP, H - R), 180, 90, R),  # 凹R2: (35,48)→(37,50) 右上の張り出し
    (-BUMP, H),  # 上辺 (39mm): 右上先端(37,50)→左上先端(-2,50)
    *arc((-BUMP, H - R), 90, 0, R),  # 凹R2: (-2,50)→(0,48) 左上の張り出し
    # → (0,48) から左辺を下って (0,0) へ閉じる
]

# ---- 画像出力 ----
xs, ys = zip(*P)
fig, ax = plt.subplots(figsize=(5, 7))
ax.add_patch(MplPolygon(P, closed=True, facecolor="#f06fb0", edgecolor="#7a1444", linewidth=1.2))
ax.set_xlim(min(xs) - 3, max(xs) + 3)
ax.set_ylim(min(ys) - 3, max(ys) + 3)
ax.set_aspect("equal")
ax.axis("off")
fig.savefig(PNG, dpi=150, bbox_inches="tight")
plt.close(fig)
print("Eared plate built", len(P), "pts ->", PNG)

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
