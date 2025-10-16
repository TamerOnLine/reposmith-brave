# ⚡ RepoSmith

[![PyPI version](https://img.shields.io/pypi/v/reposmith-tol?style=flat-square)](https://pypi.org/project/reposmith-tol/)
![Python](https://img.shields.io/pypi/pyversions/reposmith-tol?style=flat-square)
![License](https://img.shields.io/github/license/liebemama/RepoSmith?style=flat-square)
![CI](https://img.shields.io/github/actions/workflow/status/liebemama/RepoSmith/ci.yml?branch=main&label=CI&logo=github&style=flat-square)
![CodeQL](https://img.shields.io/github/actions/workflow/status/liebemama/RepoSmith/codeql.yml?branch=main&label=CodeQL&logo=github&style=flat-square)
![Release](https://img.shields.io/github/actions/workflow/status/liebemama/RepoSmith/release.yml?branch=main&label=Release&logo=github&style=flat-square)
![Downloads](https://img.shields.io/pypi/dm/reposmith-tol?style=flat-square)
[![Sponsor](https://img.shields.io/badge/Sponsor-💖-pink?style=flat-square)](https://github.com/sponsors/liebemama)

> **RepoSmith** — A zero-dependency Python project bootstrapper that builds your environment, CI, and workspace in seconds.

---

## ✨ Features

- 🚀 **Zero dependencies** — built entirely on Python stdlib  
- ⚙️ **Auto virtualenv** creation (`.venv`)  
- 🧱 **Project scaffolding** — `requirements.txt`, entry file, `.gitignore`, `LICENSE`  
- 💻 **VS Code config** — `settings.json`, `launch.json`, workspace auto-setup  
- 🛡 **GitHub Actions** — generated `.github/workflows/ci.yml`  
- 🔍 **Security Analysis** via integrated **CodeQL** workflow  
- 🔧 **Idempotent** — re-runs safely, overwriting only when `--force`  
- 📢 **Release automation** — automatic GitHub Releases on tagged versions  
- 🧾 **Dependabot** — keeps CI and Python dependencies up-to-date

---

## ⚡ Quick Start

### 🧭 Option 1 — Run as Python module
```powershell
py -m reposmith init --entry run.py --with-vscode --with-ci
```

### 🧰 Option 2 — Use CLI (if installed in PATH)
```powershell
reposmith init --entry run.py --with-vscode --with-ci
```

### 🧩 Option 3 — Use the `on/` helper package
```powershell
py -m on init        # same as: py -m reposmith init
py -m on info        # show environment info
py -m on init -i     # interactive mode
```

---

## ⚙️ CLI Options

| Flag | Description |
|------|--------------|
| `--force` | Overwrite existing files (creates `.bak` backups) |
| `--no-venv` | Skip virtual environment creation |
| `--with-license` | Add `LICENSE` (MIT by default) |
| `--with-gitignore` | Add `.gitignore` preset |
| `--with-vscode` | Add VS Code config |
| `--with-ci` | Add GitHub Actions CI workflow |
| `--author`, `--year` | Customize LICENSE metadata |
| `--ci-python` | Set Python version for CI (default: 3.12) |

---

## 📦 Installation

```powershell
py -m pip install --upgrade reposmith-tol
```

If PATH is not set:
```powershell
py -m reposmith init --entry run.py
```

---

## 🧪 Development

Run tests locally:
```powershell
python -m unittest discover -s tests -v
```

---

## 🗺️ Roadmap

- [ ] Template packs (FastAPI, Django, React)
- [ ] Interactive wizard mode
- [ ] Multi-license support (MIT, Apache-2.0, GPL-3.0)
- [ ] Full release automation via GitHub Actions

> Track progress: [GitHub Projects ↗](https://github.com/orgs/liebemama/projects/2)

---

## 🧩 Repository Structure

```
RepoSmith/
├── reposmith/              # Core CLI + module
├── on/                     # Shortcut package
├── .github/                # CI, templates, discussions
│   ├── ISSUE_TEMPLATE/     # bug.yml, feature.yml, etc.
│   ├── DISCUSSION_TEMPLATE/
│   └── workflows/          # ci.yml, codeql.yml, release.yml
├── tests/                  # Unit tests
├── examples/               # Sample projects
├── pyproject.toml
└── setup.py
```

---

## 🛡 License

This project is licensed under the [MIT License](https://github.com/liebemama/RepoSmith/blob/main/LICENSE).  
© 2025 **TamerOnLine**

---

## 💬 Support & Community

- 🐞 [Report a Bug](https://github.com/liebemama/RepoSmith/issues/new?template=bug.yml)
- 💡 [Suggest a Feature](https://github.com/liebemama/RepoSmith/issues/new?template=feature.yml)
- ✅ [Create a Task](https://github.com/liebemama/RepoSmith/issues/new?template=task.yml)
- 💬 [Join Discussions](https://github.com/liebemama/RepoSmith/discussions)
- 🔐 [Security Advisory Template](https://github.com/liebemama/RepoSmith/blob/main/ADVISORY_TEMPLATE.md)
- 💖 [Sponsor the project](https://github.com/sponsors/liebemama)
- 📧 [info@tameronline.com](mailto:info@tameronline.com)

---

## 🧠 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](.github/CODE_OF_CONDUCT.md).  
Please review it to ensure a welcoming and inclusive community.
