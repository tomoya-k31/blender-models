from pathlib import Path

import matplotlib.pyplot as plt
import trimesh
from matplotlib.patches import Polygon as MplPolygon
from shapely.affinity import translate
from shapely.geometry import Polygon, box

# side_wagon_hook.py の右フック (75-84行目) が「入る穴」を開けるための
# 差分 (ブール subtract) 用ツールオブジェクト。
# フックの突起輪郭を CLEARANCE 分だけ外側にオフセットした密着ポケットを押し出す。
# 元の側面ハンガーと同じ座標系なので、Blender で両 STL を読み込むと位置が一致する。

THK = 10.0  # フック本体の厚み (side_wagon_hook.py と同じ)
CLEARANCE = 0.4  # はめあいの隙間 (片側), FDM 標準
PLATE_THK = 1.0  # 板の幅 (破線=元フック左辺 x=19.5 からの -X)
PLATE_TOP_Y = 83.0  # 板の上端 y
# 幅・高さは変えずにオブジェクト全体を平行移動して左下を合わせる先
MOVE_TO_X = -1.0  # 移動後の最小 x
MOVE_TO_Y = 0.0  # 移動後の最小 y
Z_OVERSHOOT = 0.5  # 上下面からの突き出し量 (同一平面ブールの不具合回避 / 確実な貫通)
DEPTH = THK + 2 * Z_OVERSHOOT  # 押し出し高さ

# 生成物 (png / stl) の出力先 (gitignore 対象)
OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)
NAME = Path(__file__).stem
PNG = OUT / f"{NAME}.png"
STL = OUT / f"{NAME}.stl"

# ---- 右フックの突起輪郭 (side_wagon_hook.py の P から抽出) ----
# x=19.5 の線で本体とつながる突起部のみを閉じた単純多角形にしたもの。
# (バーブ上部 y=73 と返し下の隙間 y=70-73 はそのまま保持される)
HOOK = [
    (19.500, 70.000),  # 本体との接続 (下側)
    (22.500, 70.000),
    (22.500, 73.000),
    (23.500, 73.000),  # バーブ (返し) 上面
    (25.500, 71.000),
    (25.500, 69.000),
    (25.500, 52.000),  # 右端
    (19.500, 52.000),  # 本体との接続 (上側へ x=19.5 で閉じる)
]

# ---- 輪郭を CLEARANCE 分だけ外側にオフセット → 密着ポケット断面 ----
hook_poly = Polygon(HOOK)
if not hook_poly.is_valid:
    hook_poly = hook_poly.buffer(0)
# mitre 接合で角を保ったままフック形状に沿わせる
cutter_poly = hook_poly.buffer(CLEARANCE, join_style="mitre")

# ---- 左側に幅 PLATE_THK の板を追加 (右端は破線=元フック左辺 x=19.5) ----
minx = cutter_poly.bounds[0]
left_ys = [y for x, y in cutter_poly.exterior.coords if abs(x - minx) < 1e-6]
y0 = min(left_ys)  # 板の下端 = カッター下端
hook_left_x = min(x for x, _ in HOOK)  # 破線 (元フック) の左辺 x=19.5
plate = box(hook_left_x - PLATE_THK, y0, hook_left_x, PLATE_TOP_Y)
part = cutter_poly.union(plate)

# ---- 幅・高さはそのままにオブジェクト全体を平行移動 (左下を MOVE_TO へ) ----
dx, dy = MOVE_TO_X - part.bounds[0], MOVE_TO_Y - part.bounds[1]
part = translate(part, dx, dy)

# ---- 画像出力 ----
cx, cy = part.exterior.xy
hx, hy = zip(*[(x + dx, y + dy) for x, y in (*HOOK, HOOK[0])])  # フック輪郭も同じだけ移動
fig, ax = plt.subplots(figsize=(6, 6))
ax.add_patch(
    MplPolygon(
        list(zip(cx, cy)),
        closed=True,
        facecolor="#f0c0c0",
        edgecolor="#8c1a1a",
        linewidth=1.2,
        label=f"cutter (+{CLEARANCE}mm) +plate {PLATE_THK}mm (moved)",
    )
)
ax.plot(hx, hy, "--", color="#1a3a5c", linewidth=1.0, label="right hook (moved)")
allx, ally = list(cx) + list(hx), list(cy) + list(hy)
ax.set_xlim(min(allx) - 2, max(allx) + 2)
ax.set_ylim(min(ally) - 2, max(ally) + 2)
ax.set_aspect("equal")
ax.legend(loc="upper left", fontsize=8)
ax.axis("off")
fig.savefig(PNG, dpi=150, bbox_inches="tight")
plt.close(fig)
print("Hook cutter built", len(part.exterior.coords), "pts ->", PNG)

# ---- STL出力 (断面を DEPTH で押し出し、上下に Z_OVERSHOOT 突き出す) ----
mesh = trimesh.creation.extrude_polygon(part, height=DEPTH)
mesh.apply_translation((0.0, 0.0, -Z_OVERSHOOT))  # z: -0.5 .. THK+0.5
mesh.export(STL)
print(
    f"STL exported -> {STL}  watertight=",
    mesh.is_watertight,
    " volume=",
    round(mesh.volume, 1),
    "mm^3",
)
