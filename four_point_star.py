import math
from pathlib import Path

import matplotlib.pyplot as plt
import trimesh
from matplotlib.patches import Polygon as MplPolygon
from shapely.geometry import Polygon

# 手描き図 (ピンク) の 2D プロファイルを Z 方向に押し出した形。
# 10mm 角の正方形の四隅から半径 5mm の四分円を取り除いて残る、中央の
# 4方向に尖った星形 (凹カーブの菱形)。尖りは各辺の中点に来る。

THK = 10.0  # 押し出し (Z)

# ---- 寸法 (mm) ----
SIDE = 10.0  # 正方形の一辺
R = 5.0  # 四隅の円弧半径 (= SIDE/2 なので尖りは辺の中点に一致)

# 生成物 (png / stl) の出力先 (gitignore 対象)
OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)
NAME = Path(__file__).stem
PNG = OUT / f"{NAME}.png"
STL = OUT / f"{NAME}.stl"


def arc(center, a0, a1, r, n=24):
    """center を中心に角度 a0→a1 (deg) の円弧を n 分割 (終点は除く) で返す。"""
    return [
        (center[0] + r * math.cos(math.radians(a)), center[1] + r * math.sin(math.radians(a)))
        for a in (a0 + (a1 - a0) * i / n for i in range(n))
    ]


# ---- 中央の星形プロファイル (反時計回り。各辺中点を尖りとする4つの四分円) ----
# 各円弧は対応する隅を中心に、隣り合う辺中点どうしを凹カーブで結ぶ。
P = [
    *arc((SIDE, 0.0), 180, 90, R),  # 右下隅中心: (5,0) → (10,5)
    *arc((SIDE, SIDE), 270, 180, R),  # 右上隅中心: (10,5) → (5,10)
    *arc((0.0, SIDE), 0, -90, R),  # 左上隅中心: (5,10) → (0,5)
    *arc((0.0, 0.0), 90, 0, R),  # 左下隅中心: (0,5) → (5,0)
]

# ---- 画像出力 (10mm 角の正方形を破線で参考表示) ----
xs, ys = zip(*P)
fig, ax = plt.subplots(figsize=(6, 6))
ax.add_patch(MplPolygon(P, closed=True, facecolor="#f06fb0", edgecolor="#7a1444", linewidth=1.2))
ax.plot([0, SIDE, SIDE, 0, 0], [0, 0, SIDE, SIDE, 0], "--", color="#888", linewidth=0.8)
ax.set_xlim(-2, SIDE + 2)
ax.set_ylim(-2, SIDE + 2)
ax.set_aspect("equal")
ax.axis("off")
fig.savefig(PNG, dpi=150, bbox_inches="tight")
plt.close(fig)
print("Star built", len(P), "pts ->", PNG)

# ---- STL出力 (Pを厚さTHKで押し出し) ----
poly = Polygon(P)
if not poly.is_valid:
    poly = poly.buffer(0)  # 自己交差等を自動補正
mesh = trimesh.creation.extrude_polygon(poly, height=THK)
mesh.export(STL)
print(
    f"STL exported -> {STL}  watertight=",
    mesh.is_watertight,
    " volume=",
    round(mesh.volume, 1),
    "mm^3",
)
