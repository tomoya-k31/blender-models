import math
from pathlib import Path

import matplotlib.pyplot as plt
import trimesh
from matplotlib.patches import Polygon as MplPolygon
from shapely.geometry import Polygon

# 手描き図の 2D プロファイルを Z 方向に押し出した縦長バー。
# 左辺は全高ストレート、右側だけ下部で W_STEP 内側へ段差 (内側コーナーを R フィレット)。

THK = 123.0  # 押し出し (Z)

# ---- 寸法 (mm) ----
W_LOWER = 10.0  # 下部の幅
W_STEP = 7.0  # 段差で内側に入る量 (上部幅 = 10 + 7 = 17mm)
H_TOTAL = 83.0  # 全高
H_UPPER = 50.0  # 上部右辺 (縦) の長さ
R = 7.0  # 段差の内側フィレット半径
H_LOWER = 26.0  # 下部右辺 (縦) の長さ
# 整合: H_LOWER + R + H_UPPER = 26 + 7 + 50 = 83 = H_TOTAL

W_UPPER = W_LOWER + W_STEP  # 上部の幅 17
Y_STEP = H_TOTAL - H_UPPER  # 段差水平辺の高さ 33 (= H_LOWER + R)

# 生成物 (png / stl) の出力先 (gitignore 対象)
OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)
NAME = Path(__file__).stem
PNG = OUT / f"{NAME}.png"
STL = OUT / f"{NAME}.stl"

# ---- 段差の内側フィレット (R) ----
# 中心 (W_UPPER, H_LOWER)=(17,26)。下部右辺 x=10 に (10,26) で接し、
# 段差水平辺 y=33 に (17,33) で接する四半円。θ=180°→90°。
N = 12
arc = [
    (W_UPPER + R * math.cos(math.radians(a)), H_LOWER + R * math.sin(math.radians(a)))
    for a in (180.0 - 90.0 * i / N for i in range(N + 1))
]

# ---- プロファイル (反時計回り) ----
P = [
    (0.0, 0.0),  # 左下
    (W_LOWER, 0.0),  # 右下 (下部幅 10mm)
    *arc,  # (10,26) → フィレット → (17,33)
    (W_UPPER, H_TOTAL),  # 右上 (上部幅 17mm)
    (0.0, H_TOTAL),  # 左上
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
print("Stepped bar built", len(P), "pts ->", PNG)

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
