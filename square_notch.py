import math
from pathlib import Path

import matplotlib.pyplot as plt
import trimesh
from matplotlib.patches import Polygon as MplPolygon
from shapely.geometry import Polygon

# 手描き図 (ピンク) の 2D プロファイルを Z 方向に押し出した形。
# 10mm 角の正方形の右下の角 (1/4 コーナー) を半径 5mm の弧で丸め、
# 弧の外側 (角 (10,0) 側の小片) を削り取った形。
# 弧の中心は (5,5)=正方形中心。底辺に (5,0)、右辺に (10,5) で接する四分円。

THK = 10.0  # 押し出し (Z)

# ---- 寸法 (mm) ----
SIDE = 10.0  # 正方形の一辺
R = 5.0  # 角を丸める弧の半径 (= SIDE/2 なので接点は辺の中点)

# 生成物 (png / stl) の出力先 (gitignore 対象)
OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)
NAME = Path(__file__).stem
PNG = OUT / f"{NAME}.png"
STL = OUT / f"{NAME}.stl"


def arc(center, a0, a1, r, n=48):
    """center を中心に角度 a0→a1 (deg) の円弧を返す (両端含む)。"""
    return [
        (center[0] + r * math.cos(math.radians(a)), center[1] + r * math.sin(math.radians(a)))
        for a in (a0 + (a1 - a0) * i / n for i in range(n + 1))
    ]


# ---- プロファイル (反時計回り。右下の角だけ弧で丸める) ----
P = [
    (0.0, 0.0),  # 左下
    # 底辺 → (5,0) → 弧 (中心(5,5)) → (10,5) : 右下コーナーを丸める (弧の外側=角を削除)
    *arc((SIDE / 2, SIDE / 2), 270, 360, R),  # (5,0) → (10,5)
    (SIDE, SIDE),  # 右上
    (0.0, SIDE),  # 左上
]

# ---- 画像出力 (正方形を破線で参考表示) ----
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
print("Rounded-corner square built", len(P), "pts ->", PNG)

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
