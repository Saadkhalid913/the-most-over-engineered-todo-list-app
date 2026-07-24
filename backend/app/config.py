import os

_INSECURE_DEFAULT = "dev-only-change-me"
JWT_SECRET = os.environ.get("JWT_SECRET", "").strip()
if not JWT_SECRET or JWT_SECRET == _INSECURE_DEFAULT:
    raise RuntimeError(
        "JWT_SECRET must be set to a strong non-default value. "
        "Run via ./dev/start.sh (generates .env) or export JWT_SECRET."
    )

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", str(60 * 24)))
