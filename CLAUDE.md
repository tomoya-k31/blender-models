# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Python scripts that build 3D-printable / Blender models. Each script defines a 2D polygon, renders a PNG preview with matplotlib, then extrudes it to a watertight STL via shapely + trimesh.

## Environment & commands

- Python 3.13, managed by **mise**; the venv lives at `.venv` (created with `uv venv`).
- Run a script: `uv run <script.py>` (uses the project venv — do not call bare `python`).
- Add a dependency: `uv add <pkg>` (updates `pyproject.toml` + `uv.lock`); never `pip install`.
- Lint / format with Ruff: `uv run ruff check .` and `uv run ruff format .` (config in `pyproject.toml`: line-length 100, lint rules E/F/I/UP). A `PostToolUse` hook auto-runs `ruff format` on edited `.py` files.
- `mapbox-earcut` is a required runtime dep: trimesh's `extrude_polygon` needs it for triangulation. Don't remove it even though nothing imports it directly.

## Script pattern

One Python script per object (see `side_wagon_hook.py`); a script typically:
1. Defines a polygon as a list of `(x, y)` points `P` and a thickness `THK`.
2. Renders a preview with matplotlib (`MplPolygon`) → PNG.
3. Builds `shapely.geometry.Polygon(P)`, repairs it with `.buffer(0)` if `not poly.is_valid`, then `trimesh.creation.extrude_polygon(poly, height=THK)` → STL.
4. Prints whether the mesh `is_watertight` — a watertight result is the success signal.

Generated artifacts go to `output/<script-stem>.png` and `output/<script-stem>.stl`. `output/` is gitignored — never commit PNG/STL files.
