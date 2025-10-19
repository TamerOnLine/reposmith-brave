from __future__ import annotations
from pathlib import Path
from ..file_utils import create_app_file
from ..ci_utils import ensure_github_actions_workflow
from ..venv_utils import create_virtualenv
from ..vscode_utils import create_vscode_files
from ..gitignore_utils import create_gitignore
from ..license_utils import create_license
from ..brave_profile import init_brave_profile
from ..utils.deps import post_init_dependency_setup

def run_init(args, logger) -> int:
    root: Path = args.root
    root.mkdir(parents=True, exist_ok=True)
    logger.info("🚀 Initializing project at: %s", root)

    # --all expands
    if getattr(args, "all", False):
        args.use_uv = True
        args.with_brave = True
        args.with_vscode = True
        args.with_license = True
        args.with_gitignore = True

    entry_name = args.entry if (args.entry not in (None, "")) else "run.py"
    entry_path = root / entry_name
    no_venv = bool(getattr(args, "no_venv", False))

    venv_dir = root / ".venv"
    if not no_venv:
        create_virtualenv(venv_dir)
    else:
        logger.info("Skipping virtual environment creation (--no-venv).")

    # (2) نؤجل التثبيت إلى post_init_dependency_setup

    # (3) entry file
    create_app_file(entry_path, force=args.force)
    logger.info("[entry] %s created at: %s", entry_name, entry_path)

    # (4) optional add-ons
    if args.with_vscode:
        create_vscode_files(root, venv_dir, main_file=str(entry_path), force=args.force)
    if args.with_gitignore:
        create_gitignore(root, force=args.force)
    if args.with_license:
        create_license(root, license_type="MIT", owner_name="Tamer", force=args.force)

    # (5) CI
    ensure_github_actions_workflow(root)

    # (6) Brave
    if args.with_brave:
        init_brave_profile(root)
        logger.info("🦁 Brave Dev Profile initialized successfully.")

    # (7) deps
    try:
        post_init_dependency_setup(root, prefer_uv=bool(getattr(args, "use_uv", False)))
    except Exception as e:
        logger.warning(f"Post-init dependency setup failed: {e}")

    logger.info("✅ Project initialized successfully at: %s", root)
    return 0
