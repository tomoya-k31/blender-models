import math
from pathlib import Path

import matplotlib.pyplot as plt
import trimesh
from matplotlib.patches import Polygon as MplPolygon
from shapely.geometry import Polygon

# 手描き図 (ピンク) の 2D プロファイルを Z 方向に押し出した縦長パーツ。
# 左辺は垂直の直線、上辺・下辺とも 8mm、右辺は外側に膨らむ凸カーブ (上下対称)。

THK = 82.0  # 押し出し (Z)

# ---- 寸法 (mm) ----
W_EDGE = 8.0  # 上辺・下辺の幅 (左辺 x=0 から)
H = 41.0  # 左辺 (縦・直線) の高さ
BULGE = 4.0  # 右辺の最大膨らみ (右辺の垂直線 x=W_EDGE からの右へのはみ出し)
# 最大幅 = W_EDGE + BULGE = 12mm (図の「12mm」)

# 右辺の制御点: 右下 (8,0) → 頂点 (12, H/2) → 右上 (8,41)。高さ中央で上下対称。
P_BOT = (W_EDGE, 0.0)
P_MID = (W_EDGE + BULGE, H / 2)  # (12, 20.5)
P_TOP = (W_EDGE, H)

# 生成物 (png / stl) の出力先 (gitignore 対象)
OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)
NAME = Path(__file__).stem
PNG = OUT / f"{NAME}.png"
STL = OUT / f"{NAME}.stl"


def circle_from_3pts(a, b, c):
    """3点を通る円の中心と半径を返す。"""
    (ax, ay), (bx, by), (cx, cy) = a, b, c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    a2, b2, c2 = ax**2 + ay**2, bx**2 + by**2, cx**2 + cy**2
    ux = (a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / d
    uy = (a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / d
    return (ux, uy), math.hypot(ax - ux, ay - uy)


# ---- 右辺の円弧 (P_BOT → P_MID → P_TOP を通る円弧) ----
(ux, uy), R = circle_from_3pts(P_BOT, P_MID, P_TOP)
a_bot = math.atan2(P_BOT[1] - uy, P_BOT[0] - ux)
a_top = math.atan2(P_TOP[1] - uy, P_TOP[0] - ux)
N = 24
arc = [
    (ux + R * math.cos(a), uy + R * math.sin(a))
    for a in (a_bot + (a_top - a_bot) * i / N for i in range(N + 1))
]

# ---- プロファイル (反時計回り) ----
P = [
    (0.0, 0.0),  # 左下
    *arc,  # 右下 (8,0) → 膨らみ → 右上 (12,41)
    (0.0, H),  # 左上
]

# ---- 画像出力 ----
xs, ys = zip(*P)
fig, ax = plt.subplots(figsize=(4, 10))
ax.add_patch(MplPolygon(P, closed=True, facecolor="#f06fb0", edgecolor="#7a1444", linewidth=1.2))
ax.set_xlim(min(xs) - 2, max(xs) + 2)
ax.set_ylim(min(ys) - 2, max(ys) + 2)
ax.set_aspect("equal")
ax.axis("off")
fig.savefig(PNG, dpi=150, bbox_inches="tight")
plt.close(fig)
print("Curved bar built", len(P), "pts ->", PNG, " R=", round(R, 2))

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
