def is_strict_mode() -> bool:
    """
    Dynamic config (no import-time freeze).
    """
    import os
    return os.getenv("STRICT_MODE", "true").lower() == "true"
