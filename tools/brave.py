# tools/brave.py
from __future__ import annotations
import argparse
import os
import sys
import json
import subprocess
from pathlib import Path
from shutil import which

# ---------------------------
# إعدادات وملفات المشروع
# ---------------------------
DEFAULT_PORTS = (8000, 5173)
PORTS_FILE = ".brave-ports.conf"
URLS_FILE = ".brave-profile.conf"
PROFILE_DIRNAME = ".brave-profile"

README_TXT = (
    "Per-project Brave/Chromium profile.\n"
    "Launched with --user-data-dir pointing here.\n"
)
DEFAULT_PREFS = {"homepage": "about:blank", "first_run_tabs": []}

DEFAULT_URLS_CONF = """# Lines starting with # are ignored.
# Add URLs to open automatically (one per line)
# http://localhost:8000
# http://localhost:5173
""".rstrip() + "\n"

DEFAULT_PORTS_CONF = """# Ports for this project (one per line)
8000
5173
""".rstrip() + "\n"

# ---------------------------
# Utilities
# ---------------------------
def read_ports(root: Path) -> list[int]:
    p = root / PORTS_FILE
    ports: list[int] = []
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s.isdigit():
                ports.append(int(s))
    return ports or list(DEFAULT_PORTS)

def read_extra_urls(root: Path) -> list[str]:
    p = root / URLS_FILE
    urls: list[str] = []
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s and not s.startswith("#"):
                urls.append(s)
    return urls

def build_urls(ports: list[int], extra: list[str]) -> list[str]:
    urls = [f"http://localhost:{port}" for port in ports]
    for u in extra:
        if u not in urls:
            urls.append(u)
    return urls

def find_chromium_like() -> list[str] | None:
    # Windows
    if os.name == "nt":
        candidates = [
            os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
            os.path.expandvars(r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\BraveSoftware\Brave-Browser\Application\brave.exe"),
        ]
        for c in candidates:
            if Path(c).exists():
                return [c]
        for c in ("chrome.exe", "msedge.exe", "chromium.exe"):
            p = which(c)
            if p:
                return [p]
        return None

    # macOS
    if sys.platform == "darwin":
        app_bins = [
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
        for c in app_bins:
            if Path(c).exists():
                return [c]
        for c in ("brave-browser", "brave", "google-chrome", "chromium", "edge"):
            p = which(c)
            if p:
                return [p]
        return None

    # Linux
    for c in ("brave-browser", "brave", "google-chrome", "chromium", "chromium-browser"):
        p = which(c)
        if p:
            return [p]
    return None

def interactive_select(urls: list[str]) -> list[str]:
    print("Available URLs:")
    for i, u in enumerate(urls):
        print(f"[{i}] {u}")
    s = input("Enter comma-separated indices or press Enter for ALL: ").strip()
    if not s:
        return urls
    out: list[str] = []
    for tok in s.replace(" ", "").split(","):
        if tok.isdigit():
            ix = int(tok)
            if 0 <= ix < len(urls):
                out.append(urls[ix])
    return out or urls

def run_popen(args: list[str]) -> None:
    # لا نستخدم shell=True لضمان أمان الـ quoting عبر الأنظمة
    subprocess.Popen(args)  # noqa: S603,S607

# ---------------------------
# Commands
# ---------------------------
def cmd_init(root: Path) -> None:
    prof = root / PROFILE_DIRNAME
    tools = root / "tools"
    prof.mkdir(parents=True, exist_ok=True)
    tools.mkdir(parents=True, exist_ok=True)

    (prof / "README.txt").write_text(README_TXT, encoding="utf-8")
    (prof / "prefs.json").write_text(json.dumps(DEFAULT_PREFS, indent=2), encoding="utf-8")

    if not (root / URLS_FILE).exists():
        (root / URLS_FILE).write_text(DEFAULT_URLS_CONF, encoding="utf-8")
    if not (root / PORTS_FILE).exists():
        (root / PORTS_FILE).write_text(DEFAULT_PORTS_CONF, encoding="utf-8")

    # نصّا اختياريان لتشغيل سريع (Windows .cmd / POSIX .sh)
    (tools / "brave-launch.cmd").write_text(
        f'@echo off\r\npython "%~dp0brave.py" --auto\r\n', encoding="utf-8"
    )
    (tools / "brave-launch.sh").write_text(
        '#!/usr/bin/env bash\npython "$(dirname "$0")/brave.py" --auto\n', encoding="utf-8"
    )
    try:
        os.chmod(tools / "brave-launch.sh", 0o755)
    except Exception:
        pass

    print(f"[ok] Initialized at: {root}")

def cmd_launch(root: Path, auto: bool, no_tabs: bool, select: bool) -> None:
    ports = read_ports(root)
    extra = read_extra_urls(root)
    urls = build_urls(ports, extra)

    if no_tabs:
        chosen: list[str] = []
    elif select and urls:
        chosen = interactive_select(urls)
    elif auto:
        chosen = urls
    else:
        chosen = urls  # السلوك الافتراضي

    browser = find_chromium_like()
    profile_dir = root / PROFILE_DIRNAME

    if not browser:
        # fallback: افتح بالمتصفح الافتراضي (بدون بروفايل معزول)
        import webbrowser
        for u in chosen:
            webbrowser.open_new_tab(u)
        print("[warn] No Brave/Chromium found. Opened with default browser (no isolated profile).")
        return

    profile_dir.mkdir(parents=True, exist_ok=True)
    args = browser + [f"--user-data-dir={str(profile_dir)}"]
    for u in chosen:
        args += ["--new-tab", u]
    run_popen(args)
    print(f"[ok] Launched {' '.join(browser)} with profile: {profile_dir}")
    if chosen:
        print("Opened tabs:\n - " + "\n - ".join(chosen))

def cmd_cleanup(root: Path) -> None:
    prof = root / PROFILE_DIRNAME
    if prof.exists():
        # حذف آمن للمجلد
        import shutil
        shutil.rmtree(prof, ignore_errors=True)
        print(f"[ok] Removed {prof}")
    else:
        print(f"[info] Nothing to remove at {prof}")

def cmd_shortcut(root: Path) -> None:
    """
    ينشئ لانشر مناسب للنظام:
    - Windows: ملف .cmd جاهز (موجود) + محاولة إنشاء .lnk عبر PowerShell (إن توفر).
    - macOS: ملف .command قابل للنقر.
    - Linux: ملف .desktop داخل المشروع + .sh.
    """
    tools = root / "tools"
    tools.mkdir(parents=True, exist_ok=True)

    # Windows .cmd (موجود بالفعل من init)
    win_cmd = tools / "brave-launch.cmd"

    # macOS .command
    mac_cmd = tools / "Brave Launch.command"
    mac_cmd.write_text('#!/usr/bin/env bash\npython "$(dirname "$0")/brave.py" --auto\n', encoding="utf-8")
    try:
        os.chmod(mac_cmd, 0o755)
    except Exception:
        pass

    # Linux .desktop
    desktop = root / "Brave-Project.desktop"
    desktop.write_text(
        "\n".join([
            "[Desktop Entry]",
            "Type=Application",
            "Name=Brave Project",
            f"Exec=python {tools.as_posix()}/brave.py --auto",
            f"Path={root.as_posix()}",
            "Terminal=false",
            "Categories=Development;",
        ]) + "\n",
        encoding="utf-8",
    )

    # Windows .lnk عبر PowerShell (اختياري إن توفر pwsh)
    if os.name == "nt":
        ps = which("pwsh") or which("powershell")
        if ps:
            ps_script = r"""
$WScriptShell = New-Object -ComObject WScript.Shell
$Desktop = [Environment]::GetFolderPath("Desktop")
$Shortcut = $WScriptShell.CreateShortcut("$Desktop\Brave Project.lnk")
$Shortcut.TargetPath = "cmd.exe"
$Shortcut.Arguments = "/c """ + str(win_cmd) + r""""
$Shortcut.WorkingDirectory = """ + str(root) + r"""
$Shortcut.Save()
"""
            try:
                subprocess.run([ps, "-NoProfile", "-Command", ps_script], check=True)  # noqa: S603
                print("[ok] Windows .lnk created on Desktop.")
            except Exception as e:
                print(f"[warn] could not create .lnk: {e}")

    print("[ok] Shortcut files generated.")

# ---------------------------
# CLI
# ---------------------------
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(prog="brave", description="Cross-platform Brave/Chromium project launcher.")
    ap.add_argument("--root", type=Path, default=Path.cwd(), help="project root (contains .conf files)")

    sub = ap.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("init", help="create profile dir, default confs and helper launchers")
    s1.set_defaults(func=lambda a: cmd_init(a.root))

    s2 = sub.add_parser("launch", help="launch browser with isolated profile")
    s2.add_argument("--auto", action="store_true", help="open all urls (ports + .conf)")
    s2.add_argument("--no-tabs", action="store_true", help="launch profile only (no tabs)")
    s2.add_argument("--select", action="store_true", help="interactive selection of urls")
    s2.set_defaults(func=lambda a: cmd_launch(a.root, a.auto, a.no_tabs, a.select))

    s3 = sub.add_parser("cleanup", help="remove the profile directory")
    s3.set_defaults(func=lambda a: cmd_cleanup(a.root))

    s4 = sub.add_parser("shortcut", help="create clickable launchers for the OS")
    s4.set_defaults(func=lambda a: cmd_shortcut(a.root))

    return ap.parse_args(argv)

def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        args.func(args)  # type: ignore[attr-defined]
        return 0
    except KeyboardInterrupt:
        return 130

if __name__ == "__main__":
    raise SystemExit(main())
