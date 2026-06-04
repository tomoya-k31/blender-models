import math
from pathlib import Path

import matplotlib.pyplot as plt
import trimesh
from matplotlib.patches import Polygon as MplPolygon
from shapely.geometry import Polygon

# rounded_panel.py の外形を全周 1mm 外側にオフセットしたパーツ。
# 角は丸く (各頂点を中心とする半径 OFFSET の円弧 = 頂点から 1mm)。Z は変更なし。

THK = 82.0  # 押し出し (Z) ※ rounded_panel と同じ
OFFSET = 1.0  # 外形を外側に厚くする量 (角の丸み半径も 1mm)

# ---- 寸法 (mm) ---- ※ rounded_panel.py と同一
LEFT_H = 49.0  # 左辺 (縦・直線) の高さ
TOP_W = 26.0  # 上辺/下辺の直線部の幅
RIGHT_H = 31.0  # 右辺 (縦・直線) の高さ
R = 9.0  # 右の2角の丸め半径
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


# ---- 元プロファイル (左の2角は直角、右の2角を R9) ----
P = [
    (0.0, 0.0),
    (TOP_W, 0.0),
    *arc((TOP_W, R), 270, 360, R),  # 右下 R9: (26,0)→(35,9)
    (RX, R + RIGHT_H),  # 右辺 31mm → (35,40)
    *arc((TOP_W, R + RIGHT_H), 0, 90, R),  # 右上 R9: (35,40)→(26,49)
    (0.0, LEFT_H),  # 上辺 → 左上
]
poly = Polygon(P)
if not poly.is_valid:
    poly = poly.buffer(0)

# ---- 外形を OFFSET だけ外側に拡張 (角は round = 頂点から 1mm の円弧) ----
outer = poly.buffer(OFFSET, join_style="round")

# ---- 画像出力 (元輪郭=破線, オフセット後=塗り) ----
ox, oy = outer.exterior.xy
ix, iy = poly.exterior.xy
fig, ax = plt.subplots(figsize=(5, 8))
ax.add_patch(
    MplPolygon(
        list(zip(ox, oy)),
        closed=True,
        facecolor="#f06fb0",
        edgecolor="#7a1444",
        linewidth=1.2,
        label=f"+{OFFSET}mm (round)",
    )
)
ax.plot(ix, iy, "--", color="#4a4a4a", linewidth=1.0, label="original")
ax.set_xlim(min(ox) - 3, max(ox) + 3)
ax.set_ylim(min(oy) - 3, max(oy) + 3)
ax.set_aspect("equal")
ax.legend(loc="upper left", fontsize=8)
ax.axis("off")
fig.savefig(PNG, dpi=150, bbox_inches="tight")
plt.close(fig)
print("Offset panel built", len(outer.exterior.coords), "pts ->", PNG)

# ---- STL出力 (拡張後の外形を厚さTHKで押し出し) ----
mesh = trimesh.creation.extrude_polygon(outer, height=THK)
mesh.export(STL)
print(
    f"STL exported -> {STL}  watertight=",
    mesh.is_watertight,
    " volume=",
    round(mesh.volume, 1),
    "mm^3",
)
