import math
from pathlib import Path

import matplotlib.pyplot as plt
import trimesh
from matplotlib.patches import Polygon as MplPolygon
from shapely.geometry import Polygon, box

# 手描き図 (ピンク) の 2D プロファイルを Z 方向に押し出した縦長バー。
# 左辺は垂直の直線 (左の角は直角)、右側は上下を 1mm ずつ控えて (上下コーナー間 57mm)
# 右の上下コーナーを r9 で丸める。上辺の平らな部分 ≈ 9.5mm。

THK = 82.0  # 押し出し (Z)

# ---- 寸法 (mm) ----
H_LEFT = 59.0  # 左辺 (縦・直線) の高さ
INSET = 1.0  # 右上・右下を内側に控える量 (上下それぞれ)
R = 9.0  # 右コーナーの丸め半径
W = 18.0  # 右コーナーの x 位置 (上辺の平ら ≈ 9.5mm になる幅)
# 右の上下コーナー間 = (H_LEFT - INSET) - INSET = 59 - 1 - 1 = 57mm

RECT_W = 9.5  # 合算する長方形の幅 (x:9.5, y:59 を左下原点で union)

# 角 (丸める前) ※ 反時計回り
BL = (0.0, 0.0)  # 左下 (直角)
BR = (W, INSET)  # 右下 (1mm 上げ) → r9 で丸める
TR = (W, H_LEFT - INSET)  # 右上 (1mm 下げ) → r9 で丸める
TL = (0.0, H_LEFT)  # 左上 (直角)

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
    theta = math.acos(max(-1.0, min(1.0, ax * bx + ay * by)))  # 2辺のなす角
    t = r / math.tan(theta / 2)  # 頂点から接点までの距離
    # 円弧中心 (角の二等分線方向に r/sin(θ/2))
    bisx, bisy = ax + bx, ay + by
    lbis = math.hypot(bisx, bisy)
    dc = r / math.sin(theta / 2)
    cx, cy = v[0] + bisx / lbis * dc, v[1] + bisy / lbis * dc
    a1 = math.atan2(v[1] + ay * t - cy, v[0] + ax * t - cx)
    a2 = math.atan2(v[1] + by * t - cy, v[0] + bx * t - cx)
    da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi  # 最短回り
    return [(cx + r * math.cos(a1 + da * i / segs), cy + r * math.sin(a1 + da * i / segs)) for i in range(segs + 1)]


# ---- プロファイル (反時計回り。右の2角だけ r9 で丸める) ----
P = [
    BL,
    *fillet(BL, BR, TR, R),  # 右下コーナー
    *fillet(BR, TR, TL, R),  # 右上コーナー
    TL,
]

# ---- ポリゴン化して x:RECT_W × y:H_LEFT の長方形を合算 (union) ----
poly = Polygon(P)
if not poly.is_valid:
    poly = poly.buffer(0)  # 自己交差等を自動補正
poly = poly.union(box(0.0, 0.0, RECT_W, H_LEFT))

# ---- 画像出力 ----
px, py = poly.exterior.xy
fig, ax = plt.subplots(figsize=(4, 10))
ax.add_patch(
    MplPolygon(list(zip(px, py)), closed=True, facecolor="#f06fb0", edgecolor="#7a1444", linewidth=1.2)
)
ax.set_xlim(min(px) - 2, max(px) + 2)
ax.set_ylim(min(py) - 2, max(py) + 2)
ax.set_aspect("equal")
ax.axis("off")
fig.savefig(PNG, dpi=150, bbox_inches="tight")
plt.close(fig)
print("Rounded bar built", len(poly.exterior.coords), "pts ->", PNG)

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
