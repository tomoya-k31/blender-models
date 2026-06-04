import math
from pathlib import Path

import matplotlib.pyplot as plt
import trimesh
from matplotlib.patches import Polygon as MplPolygon
from shapely.geometry import Polygon, box

# rounded_bar.py の外形を全周 1mm 外側にオフセットしたパーツ。
# 角は丸く (各頂点を中心とする半径 OFFSET の円弧 = 頂点から 1mm)。Z は変更なし。

THK = 82.0  # 押し出し (Z) ※ rounded_bar と同じ
OFFSET = 1.0  # 外形を外側に厚くする量 (角の丸み半径も 1mm)

# ---- 寸法 (mm) ---- ※ rounded_bar.py と同一
H_LEFT = 59.0  # 左辺 (縦・直線) の高さ
INSET = 1.0  # 右上・右下を内側に控える量 (上下それぞれ)
R = 9.0  # 右コーナーの丸め半径
W = 18.0  # 右コーナーの x 位置
RECT_W = 9.5  # 合算する長方形の幅 (x:9.5, y:59)

# 角 (丸める前) ※ 反時計回り
BL = (0.0, 0.0)
BR = (W, INSET)
TR = (W, H_LEFT - INSET)
TL = (0.0, H_LEFT)

# 生成物 (png / stl) の出力先 (gitignore 対象)
OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)
NAME = Path(__file__).stem
PNG = OUT / f"{NAME}.png"
STL = OUT / f"{NAME}.stl"


def fillet(prev, v, nxt, r, segs=20):
    """頂点 v (前 prev / 後 nxt) を半径 r で丸めた円弧の点列 (接点 T1→T2) を返す。"""
    ax, ay = prev[0] - v[0], prev[1] - v[1]
    bx, by = nxt[0] - v[0], nxt[1] - v[1]
    la, lb = math.hypot(ax, ay), math.hypot(bx, by)
    ax, ay, bx, by = ax / la, ay / la, bx / lb, by / lb
    theta = math.acos(max(-1.0, min(1.0, ax * bx + ay * by)))
    t = r / math.tan(theta / 2)
    bisx, bisy = ax + bx, ay + by
    lbis = math.hypot(bisx, bisy)
    dc = r / math.sin(theta / 2)
    cx, cy = v[0] + bisx / lbis * dc, v[1] + bisy / lbis * dc
    a1 = math.atan2(v[1] + ay * t - cy, v[0] + ax * t - cx)
    a2 = math.atan2(v[1] + by * t - cy, v[0] + bx * t - cx)
    da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
    return [(cx + r * math.cos(a1 + da * i / segs), cy + r * math.sin(a1 + da * i / segs)) for i in range(segs + 1)]


# ---- 元プロファイル (右の2角を r9 で丸め、x:9.5 × y:59 の長方形を合算) ----
P = [BL, *fillet(BL, BR, TR, R), *fillet(BR, TR, TL, R), TL]
poly = Polygon(P)
if not poly.is_valid:
    poly = poly.buffer(0)
poly = poly.union(box(0.0, 0.0, RECT_W, H_LEFT))

# ---- 外形を OFFSET だけ外側に拡張 (角は round = 頂点から 1mm の円弧) ----
outer = poly.buffer(OFFSET, join_style="round")

# ---- 画像出力 (元輪郭=破線, オフセット後=塗り) ----
ox, oy = outer.exterior.xy
ix, iy = poly.exterior.xy
fig, ax = plt.subplots(figsize=(4, 10))
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
ax.set_xlim(min(ox) - 2, max(ox) + 2)
ax.set_ylim(min(oy) - 2, max(oy) + 2)
ax.set_aspect("equal")
ax.legend(loc="upper left", fontsize=8)
ax.axis("off")
fig.savefig(PNG, dpi=150, bbox_inches="tight")
plt.close(fig)
print("Offset bar built", len(outer.exterior.coords), "pts ->", PNG)

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
