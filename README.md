# blender-models

3D モデリング用のオブジェクトを生成する Python スクリプトを保管するリポジトリです。

各スクリプトは 2D ポリゴンを定義し、matplotlib でプレビュー画像 (PNG) を描画したうえで、shapely + trimesh で押し出して STL を出力します。STL は Blender などにインポートして利用します。

## 構成

- オブジェクトごとに 1 つの Python スクリプトを作成していきます (例: `side_wagon_hook.py`)。
- `main.py` はテンプレート用のプレースホルダーです (用途は未定)。
- 生成物 (PNG / STL) は `output/` ディレクトリに `<スクリプト名>.png` / `<スクリプト名>.stl` として出力されます。`output/` は `.gitignore` 済みで、コミット対象外です。

## セットアップ

[mise](https://mise.jdx.dev/) でツール (Python 3.13 / uv) を管理します。

```bash
mise install        # Python 3.13 と uv を導入
uv venv             # .venv を作成
uv sync             # 依存関係をインストール
```

## スクリプトの実行

```bash
uv run side_wagon_hook.py
```

`output/<スクリプト名>.png` と `output/<スクリプト名>.stl` が生成されます。STL が watertight=True であれば成功です。

## 依存関係の追加

```bash
uv add <package>    # pyproject.toml と uv.lock を更新 (pip は使わない)
```

## フォーマット / Lint

[Ruff](https://docs.astral.sh/ruff/) を使用します。

```bash
uv run ruff format .    # 整形
uv run ruff check .     # Lint
```

ファイル編集時に `ruff format` を自動実行する Claude Code フックを `.claude/settings.json` に設定済みです (有効化には `/hooks` を開くか再起動が必要)。
