from datetime import datetime
from pathlib import Path


def create_license(root, license_type="MIT", owner_name="Tamer", force=False):
    """Create a LICENSE file with optional owner name."""
    year = datetime.now().year
    target = Path(root) / "LICENSE"

    if target.exists() and not force:
        print("ℹ️ LICENSE already exists (use --force to overwrite).")
        return

    mit_license = f"""MIT License

Copyright (c) {year} {owner_name}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    target.write_text(mit_license, encoding="utf-8")
    print(f"📜 LICENSE file created for {owner_name} ({license_type}).")
