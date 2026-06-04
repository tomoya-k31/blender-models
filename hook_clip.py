import math
from pathlib import Path

import matplotlib.pyplot as plt
import trimesh
from matplotlib.patches import Polygon as MplPolygon
from shapely.geometry import Polygon

# 手描き図 (ピンク) の 2D プロファイルを Z 方向に押し出した「下が開いたフック」。
# 右に縦脚 (3x8mm)、上で左へ橋渡し、左腕が R2 で丸まり下端に足(返し)。
# 左腕と右脚の間の空洞が下に開く。足と右脚の間の口 (開口) は 1mm。

THK = 10.0  # 押し出し (Z)

# ---- 寸法 (mm) ----
R = 2.0  # 左コーナーの丸め半径
# 右脚 x[5,8] (幅3), 高さ y[0,8]
# 縦構成: 足 y[0,2](高2) / 空洞 y[2,5](高3) / 橋 y[5,8]
# 空洞 x[2,5](幅3, 高3) / 足 x[2,3](幅1, 高2) / 口(開口) x[3,5]

# 生成物 (png / stl) の出力先 (gitignore 対象)
OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)
NAME = Path(__file__).stem
PNG = OUT / f"{NAME}.png"
STL = OUT / f"{NAME}.stl"


def arc(c, a0, a1, r, n=16):
    """中心 c、半径 r、角度 a0→a1(deg) の円弧 (両端含む)。"""
    return [
        (c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a)))
        for a in (a0 + (a1 - a0) * i / n for i in range(n + 1))
    ]


# ---- プロファイル (反時計回り) ----
P = [
    (5.0, 0.0),  # 右脚 左下 (口の右側)
    (8.0, 0.0),  # 右脚 右下
    (8.0, 8.0),  # 右脚 右上
    *arc((2.0, 6.0), 90, 180, R),  # 上辺→ 左上を R2 で丸め: (2,8)→(0,6)
    *arc((2.0, 3.0), 180, 270, R),  # 左辺→ 左下を R2 で丸め: (0,2)→(2,0)
    (3.0, 1.0),  # 足の底 (右へ 1mm)
    (3.0, 3.0),  # 足の右側 (上へ 2mm)
    (2.0, 3.0),  # 足の上面 (左へ戻る)
    (2.0, 6.0),  # 左腕 内側 (空洞の天井 y=5 まで)
    (5.0, 6.0),  # 空洞の天井 (橋の下面, 高さ3mm)
    (5.0, 0.0),  # 右脚 内側 (下へ) → 口 (x3-5) が下に開く
]

# ---- 画像出力 ----
xs, ys = zip(*P)
fig, ax = plt.subplots(figsize=(5, 6))
ax.add_patch(MplPolygon(P, closed=True, facecolor="#f06fb0", edgecolor="#7a1444", linewidth=1.2))
ax.set_xlim(min(xs) - 1, max(xs) + 1)
ax.set_ylim(min(ys) - 1, max(ys) + 1)
ax.set_aspect("equal")
ax.axis("off")
fig.savefig(PNG, dpi=150, bbox_inches="tight")
plt.close(fig)
print("Hook built", len(P), "pts ->", PNG)

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
