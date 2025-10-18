# -*- coding: utf-8 -*-
"""
RepoSmith CLI Entry Point
-------------------------

Includes:
- Project initialization command (init)
- New Brave Profile command (brave-profile --init)

Usage examples:
    reposmith init --root .
    reposmith brave-profile --init
"""

import argparse
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError

from .file_utils import create_app_file
from .ci_utils import ensure_github_actions_workflow
from .brave_profile import init_brave_profile
from .venv_utils import create_virtualenv, install_requirements
from .vscode_utils import create_vscode_files
from .gitignore_utils import create_gitignore
from .license_utils import create_license

def build_parser():
    """
    Create and configure RepoSmith CLI commands.

    Returns:
        argparse.ArgumentParser: Configured argument parser for CLI.
    """
    parser = argparse.ArgumentParser(
        prog="reposmith",
        description="RepoSmith: Bootstrap Python projects (zero deps)"
    )

    try:
        ver = version("reposmith-tol")
    except PackageNotFoundError:
        ver = "0.0.0"

    parser.add_argument("--version", action="version", version=f"RepoSmith-tol {ver}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # Init command
    sc = sub.add_parser("init", help="Initialize a new project")
    sc.add_argument("--root", type=Path, default=Path.cwd(), help="Target project folder")
    sc.add_argument("--force", action="store_true", help="Overwrite existing files if needed")
    sc.add_argument("--with-license", action="store_true", help="Include default LICENSE file")
    sc.add_argument("--with-gitignore", action="store_true", help="Include default .gitignore file")
    sc.add_argument("--with-vscode", action="store_true", help="Include VS Code settings")

    # Brave profile command
    bp = sub.add_parser("brave-profile", help="Manage Brave dev profile scaffolding")
    bp.add_argument("--root", type=Path, default=Path.cwd(), help="Target project folder")
    bp.add_argument("--init", action="store_true", help="Initialize Brave dev profile in the project")

    return parser

def main():
    """
    Main entry point for RepoSmith CLI.
    """
    parser = build_parser()
    args = parser.parse_args()

    if args.cmd == "init":
        root = args.root
        root.mkdir(parents=True, exist_ok=True)
        print(f"Initializing project at: {root}")

        venv_dir = root / ".venv"
        create_virtualenv(venv_dir)

        req = root / "requirements.txt"
        if req.exists() and req.stat().st_size > 0:
            install_requirements(venv_dir, str(req))
        else:
            print("No requirements.txt found (or empty) — skipping install.")

        try:
            create_app_file(root, force=args.force)
        except NameError:
            pass

        if args.with_vscode:
            create_vscode_files(root, venv_dir, main_file="main.py", force=args.force)

        if args.with_gitignore:
            create_gitignore(root, force=args.force)

        if args.with_license:
            create_license(root, license_type="MIT", owner_name="Tamer", force=args.force)

        try:
            ensure_github_actions_workflow(root)
        except NameError:
            pass

        print(f"Project initialized successfully at: {root}")

    elif args.cmd == "brave-profile" and args.init:
        init_brave_profile(args.root)
        print("Brave Dev Profile ready to use.")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()