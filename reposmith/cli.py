# -*- coding: utf-8 -*-
"""
RepoSmith CLI Entry Point
-------------------------

يتضمن:
- أمر إنشاء المشاريع (init)
- أمر Brave Profile الجديد (brave-profile --init)

Usage examples:
    reposmith init --root .
    reposmith brave-profile --init
"""

import argparse
from pathlib import Path
from .brave_profile import init_brave_profile


def build_parser():
    """إنشاء وتكوين أوامر RepoSmith"""
    parser = argparse.ArgumentParser(
        prog="reposmith",
        description="RepoSmith: Bootstrap Python projects (zero deps)",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    # -------------------------------
    # 1️⃣ أمر init لإنشاء مشروع جديد
    # -------------------------------
    sc = sub.add_parser("init", help="Initialize a new project")
    sc.add_argument("--root", type=Path, default=Path.cwd(), help="Target project folder")
    sc.add_argument("--force", action="store_true", help="Overwrite existing files if needed")
    sc.add_argument("--with-license", action="store_true", help="Include default LICENSE file")
    sc.add_argument("--with-gitignore", action="store_true", help="Include default .gitignore file")
    sc.add_argument("--with-vscode", action="store_true", help="Include VS Code settings")

    # -------------------------------
    # 2️⃣ أمر brave-profile الجديد
    # -------------------------------
    bp = sub.add_parser("brave-profile", help="Manage Brave dev profile scaffolding")
    bp.add_argument("--root", type=Path, default=Path.cwd(), help="Target project folder")
    bp.add_argument("--init", action="store_true", help="Initialize Brave dev profile in the project")

    return parser


def main():
    """نقطة التنفيذ الأساسية لأوامر RepoSmith"""
    parser = build_parser()
    args = parser.parse_args()

    # -------------------------------
    # تنفيذ الأوامر
    # -------------------------------
    if args.cmd == "init":
        # ⚙️ هنا منطق إنشاء مشروع جديد (يمكنك استدعاء أدواتك الأخرى لاحقًا)
        print(f"🚀 Initializing project at: {args.root}")
        if args.with_vscode:
            print("🧩 VS Code settings will be added.")
        if args.with_license:
            print("📜 LICENSE file will be included.")
        if args.with_gitignore:
            print("🗂️ .gitignore will be included.")
        # من هنا يمكن استدعاء وظائفك الأصلية (create_env, create_license...)
        return

    elif args.cmd == "brave-profile" and args.init:
        # 🔥 تنفيذ أمر إنشاء ملفات Brave Dev Profile
        init_brave_profile(args.root)
        print("✅ Brave Dev Profile ready to use.")
        return

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
