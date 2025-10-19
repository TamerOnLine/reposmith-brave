from __future__ import annotations
import subprocess, os
from pathlib import Path
from .paths import venv_python

def post_init_dependency_setup(root: Path, prefer_uv: bool = True) -> None:
    """
    - إن وُجد requirements.txt → تثبيت (uv ثم pip fallback).
    - إن لم يوجد → إن كان prefer_uv=True شغّل uv init (إن لم يوجد pyproject.toml).
    """
    py = venv_python(root)
    if not py.exists():
        print("[INFO] No Python interpreter in .venv — skipping dependency setup.")
        return

    req = root / "requirements.txt"
    pyproject = root / "pyproject.toml"

    def run(cmd: list[str]) -> None:
        print(">", " ".join(cmd))
        subprocess.run(cmd, cwd=root, check=True)

    if req.exists() and req.stat().st_size > 0:
        if prefer_uv:
            print("[uv] requirements.txt detected → installing via uv...")
            try:
                run([str(py), "-m", "pip", "install", "--upgrade", "pip"])
                run([str(py), "-m", "uv", "pip", "install", "-r", str(req)])
                return
            except Exception:
                print("[INFO] uv not available → falling back to pip")
        print("[pip] Installing from requirements.txt...")
        run([str(py), "-m", "pip", "install", "-r", str(req)])
        return

    if prefer_uv:
        if pyproject.exists():
            print("[uv] pyproject.toml already exists — skipping uv init.")
            return
        print("[uv] No requirements.txt found → initializing pyproject.toml via uv init...")
        try:
            run([str(py), "-m", "uv", "init"])
        except Exception as e:
            print(f"[WARN] uv init failed: {e}")
    else:
        print("[INFO] No requirements.txt and prefer_uv=False — nothing to do.")
