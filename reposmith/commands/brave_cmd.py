from __future__ import annotations
from pathlib import Path
import subprocess
import sys

def _ensure_brave_py(root: Path) -> Path:
    brave_py = root / "tools" / "brave.py"
    if not brave_py.exists():
        raise FileNotFoundError(
            f"tools/brave.py not found under: {root}\n"
            "→ تأكد من إضافة ملف النظام البايثوني الجديد داخل المشروع."
        )
    return brave_py

def run_brave(args, logger) -> int:
    """
    يعادل 'reposmith brave-profile --init' لكن عبر النظام البايثوني الجديد:
    يشغّل: python tools/brave.py --root <root> init
    """
    root: Path = Path(args.root).resolve()
    brave_py = _ensure_brave_py(root)

    cmd = [sys.executable, str(brave_py), "--root", str(root), "init"]
    logger.info("Running: %s", " ".join(cmd))
    subprocess.check_call(cmd)

    logger.info("🦁 Brave Project Browser initialized (Python-only).")
    return 0
