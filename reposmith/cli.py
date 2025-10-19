# -*- coding: utf-8 -*-
"""
RepoSmith CLI Entry Point
-------------------------

Includes:
- Project initialization command (init)
- Brave Profile command (brave-profile --init)

Usage examples:
    reposmith init --root . --use-uv --with-brave
    reposmith brave-profile --init
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError

from .file_utils import create_app_file
from .ci_utils import ensure_github_actions_workflow
from .venv_utils import create_virtualenv, install_requirements
from .vscode_utils import create_vscode_files
from .gitignore_utils import create_gitignore
from .license_utils import create_license
from .env_manager import install_deps_with_uv
from .brave_profile import init_brave_profile
from .logging_utils import setup_logging

def build_parser() -> argparse.ArgumentParser:
    """Create and configure RepoSmith CLI commands.

    Returns:
        argparse.ArgumentParser: Configured argument parser for CLI.
    """
    parser = argparse.ArgumentParser(
        prog="reposmith",
        description="RepoSmith: Bootstrap Python projects (venv + uv + Brave)",
    )

    try:
        ver = version("reposmith-tol")
    except PackageNotFoundError:
        ver = "0.0.0"

    parser.add_argument("--version", action="version", version=f"RepoSmith-tol {ver}")
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: INFO",
    )
    parser.add_argument(
        "--no-emoji",
        action="store_true",
        help="Disable emojis in console output for maximum portability.",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    # Init command
    sc = sub.add_parser("init", help="Initialize a new project")
    sc.add_argument("--root", type=Path, default=Path.cwd(), help="Target project folder")
    sc.add_argument("--force", action="store_true", help="Overwrite existing files if needed")

    # Optional flags
    sc.add_argument("--with-license", action="store_true", help="Include default LICENSE file")
    sc.add_argument("--with-gitignore", action="store_true", help="Include default .gitignore file")
    sc.add_argument("--with-vscode", action="store_true", help="Include VS Code settings")
    sc.add_argument("--use-uv", action="store_true", help="Install dependencies using uv (faster)")
    sc.add_argument(
        "--with-brave",
        action="store_true",
        help="Initialize Brave project profile after scaffolding",
    )

    # Brave profile command (standalone)
    bp = sub.add_parser("brave-profile", help="Manage Brave dev profile scaffolding")
    bp.add_argument("--root", type=Path, default=Path.cwd(), help="Target project folder")
    bp.add_argument("--init", action="store_true", help="Initialize Brave dev profile in the project")

    return parser

def main() -> None:
    """Main entry point for RepoSmith CLI."""
    parser = build_parser()
    args = parser.parse_args()

    logger = setup_logging(
        level=getattr(args, "log_level", "INFO"),
        no_emoji=getattr(args, "no_emoji", False),
    )

    if args.cmd == "init":
        root: Path = args.root
        root.mkdir(parents=True, exist_ok=True)
        logger.info("🚀 Initializing project at: %s", root)

        # 1) Create virtual environment
        venv_dir = root / ".venv"
        create_virtualenv(venv_dir)

        # 2) Install dependencies (uv or pip)
        req = root / "requirements.txt"
        if args.use_uv:
            install_deps_with_uv(root)
        else:
            if req.exists() and req.stat().st_size > 0:
                install_requirements(venv_dir, str(req))
            else:
                logger.debug("No requirements.txt found (or empty) — skipping install.")

        # 3) Create main.py file
        main_file = root / "main.py"
        create_app_file(main_file, force=args.force)
        logger.info("[entry] main.py created at: %s", main_file)

        # 4) Optional add-ons
        if args.with_vscode:
            create_vscode_files(root, venv_dir, main_file=str(main_file), force=args.force)

        if args.with_gitignore:
            create_gitignore(root, force=args.force)

        if args.with_license:
            create_license(root, license_type="MIT", owner_name="Tamer", force=args.force)

        # 5) CI workflow
        ensure_github_actions_workflow(root)

        # 6) Brave integration
        if args.with_brave:
            init_brave_profile(root)
            logger.info("🦁 Brave Dev Profile initialized successfully.")

        logger.info("✅ Project initialized successfully at: %s", root)

    elif args.cmd == "brave-profile" and args.init:
        init_brave_profile(args.root)
        logger.info("🦁 Brave Dev Profile ready to use.")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
