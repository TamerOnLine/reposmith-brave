from __future__ import annotations
from ..brave_profile import init_brave_profile

def run_brave(args, logger) -> int:
    init_brave_profile(args.root)
    logger.info("🦁 Brave Dev Profile ready to use.")
    return 0
