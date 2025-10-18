# reposmith/logging_utils.py
from __future__ import annotations

import logging
import os
from typing import Optional

from .console import enable_utf8_console, sanitize_text, maybe_strip_emoji


class SafeStreamHandler(logging.StreamHandler):
    """
    معالج يضمن عدم انفجار الإخراج بسبب محارف غير قابلة للترميز.
    يمرّر الرسالة عبر maybe_strip_emoji + sanitize_text قبل الكتابة.
    """
    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            msg = maybe_strip_emoji(msg)
            msg = sanitize_text(msg)
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)


def _level_from_str(level: str) -> int:
    level = (level or "INFO").upper()
    return getattr(logging, level, logging.INFO)


def setup_logging(level: str = "INFO", no_emoji: bool = False, logger_name: Optional[str] = None) -> logging.Logger:
    """
    تهيئة logging للاستخدام في CLI:
      - UTF-8 آمن دائمًا عبر enable_utf8_console()
      - استبدال محارف غير مدعومة بدل الانهيار
      - دعم تعطيل الإيموجي عبر no_emoji/متغيّر البيئة
    """
    enable_utf8_console()
    if no_emoji:
        os.environ["REPOSMITH_NO_EMOJI"] = "1"

    logger = logging.getLogger(logger_name or "reposmith")
    logger.setLevel(_level_from_str(level))
    logger.propagate = False  # منع تمرير السجلات للـ root

    # منع تكرار المعالجات عند استدعاء setup_logging أكثر من مرة (مثلاً في الاختبارات)
    for h in list(logger.handlers):
        logger.removeHandler(h)

    handler = SafeStreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(handler)

    # حصر ضجيج مكتبات أخرى
    logging.getLogger().setLevel(logging.WARNING)
    return logger
