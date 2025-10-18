# reposmith/console.py
from __future__ import annotations

import io
import locale
import os
import sys
from typing import TextIO


def _try_reconfigure(stream: TextIO, *, encoding: str = "utf-8", errors: str = "replace") -> bool:
    """
    جرّب إعادة تهيئة كائن TextIO الحالي بترميز جديد (Python 3.7+).
    يعيد True إن نجح، وإلا False.
    """
    if hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding=encoding, errors=errors)  # type: ignore[attr-defined]
            return True
        except Exception:
            return False
    return False


def _wrap_buffer(stream: TextIO, *, encoding: str = "utf-8", errors: str = "replace") -> bool:
    """
    إذا فشلت reconfigure أو لم تكن متاحة، لفّ الـ buffer بـ TextIOWrapper
    مع الترميز المطلوب، ثم استبدِل sys.stdout/sys.stderr.
    """
    buf = getattr(stream, "buffer", None)
    if buf is None:
        return False
    try:
        wrapper = io.TextIOWrapper(buf, encoding=encoding, errors=errors, line_buffering=True)
        if stream is sys.stdout:
            sys.stdout = wrapper  # type: ignore[assignment]
        elif stream is sys.stderr:
            sys.stderr = wrapper  # type: ignore[assignment]
        else:
            return False
        return True
    except Exception:
        return False


def enable_utf8_console() -> bool:
    """
    يضمن أن stdout/stderr لن ينهارا عند وجود رموز غير مدعومة (مثل الإيموجي).
    يفضّل UTF-8 ويهبط إلى 'replace' بدل UnicodeEncodeError.
    """
    preferred = (locale.getpreferredencoding(False) or "").lower()
    target_enc = "utf-8" if "utf" in preferred else (os.environ.get("PYTHONIOENCODING") or "utf-8")

    ok_out = _try_reconfigure(sys.stdout, encoding=target_enc, errors="replace") or \
             _wrap_buffer(sys.stdout, encoding=target_enc, errors="replace")
    ok_err = _try_reconfigure(sys.stderr, encoding=target_enc, errors="replace") or \
             _wrap_buffer(sys.stderr, encoding=target_enc, errors="replace")

    return ok_out and ok_err


def sanitize_text(s: str) -> str:
    """
    يضمن قابلية الطباعة على الترميز الحالي دون رمي UnicodeEncodeError.
    """
    enc = getattr(sys.stdout, "encoding", None) or locale.getpreferredencoding(False) or "utf-8"
    try:
        s.encode(enc)
        return s
    except UnicodeEncodeError:
        return s.encode(enc, errors="replace").decode(enc, errors="replace")


def maybe_strip_emoji(s: str) -> str:
    """
    يسمح بتعطيل الإيموجي عبر:
      - متغيّر البيئة REPOSMITH_NO_EMOJI=1
    الفكرة: إن طُلِب ذلك، نحافظ على ASCII قدر الإمكان.
    """
    if os.environ.get("REPOSMITH_NO_EMOJI") == "1":
        return s.encode("ascii", "replace").decode("ascii")
    return s
