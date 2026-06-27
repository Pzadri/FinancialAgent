"""Gestión de autenticación con hashing seguro.

La contraseña se almacena en la base de datos usando scrypt, una función de
derivación de clave "memory-hard" incluida en la librería estándar de Python.
Cada contraseña usa un salt aleatorio único, de modo que dos contraseñas
iguales producen hashes distintos y los ataques por tablas precomputadas
(rainbow tables) no son viables.

Formato almacenado:  scrypt$<n>$<r>$<p>$<salt_hex>$<hash_hex>
"""
import hashlib
import hmac
import os
import secrets
from app.database import get_db

# Parámetros de scrypt (cuanto mayores, más costoso y seguro).
_SCRYPT_N = 2 ** 15   # factor de coste de CPU/memoria (32768)
_SCRYPT_R = 8         # tamaño de bloque
_SCRYPT_P = 1         # paralelización
_SALT_BYTES = 16
_DKLEN = 32
_MAXMEM = 128 * 1024 * 1024  # 128 MB, suficiente para los parámetros anteriores

# Contraseña por defecto al inicializar (cámbiala desde la app o el endpoint).
_DEFAULT_PASSWORD = "V3l0c1rr@pt0r"

# Tokens de sesión válidos (en memoria; se reinician al reiniciar el backend).
_active_tokens: set[str] = set()


def _hash_password(password: str, salt: bytes | None = None) -> str:
    """Genera el hash scrypt de una contraseña con un salt aleatorio."""
    if salt is None:
        salt = os.urandom(_SALT_BYTES)
    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=_DKLEN,
        maxmem=_MAXMEM,
    )
    return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${salt.hex()}${derived.hex()}"


def _verify_hash(password: str, stored: str) -> bool:
    """Verifica una contraseña contra el hash almacenado, en tiempo constante."""
    try:
        algo, n, r, p, salt_hex, hash_hex = stored.split("$")
        if algo != "scrypt":
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        derived = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(expected),
            maxmem=_MAXMEM,
        )
        return hmac.compare_digest(derived, expected)
    except (ValueError, TypeError):
        return False


def init_auth():
    """Asegura que exista una contraseña en la base de datos.

    Si no hay ninguna configurada, siembra la contraseña por defecto.
    """
    with get_db() as conn:
        row = conn.execute("SELECT id FROM app_auth WHERE id = 1").fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO app_auth (id, password_hash) VALUES (1, ?)",
                (_hash_password(_DEFAULT_PASSWORD),),
            )


def is_password_set() -> bool:
    with get_db() as conn:
        row = conn.execute("SELECT password_hash FROM app_auth WHERE id = 1").fetchone()
    return bool(row and row["password_hash"])


def verify_password(password: str) -> bool:
    """Comprueba si la contraseña es correcta."""
    if not password:
        return False
    with get_db() as conn:
        row = conn.execute("SELECT password_hash FROM app_auth WHERE id = 1").fetchone()
    if not row or not row["password_hash"]:
        return False
    return _verify_hash(password, row["password_hash"])


def set_password(new_password: str):
    """Establece (o actualiza) la contraseña, almacenando su hash."""
    if not new_password or len(new_password) < 4:
        raise ValueError("La contraseña debe tener al menos 4 caracteres.")
    new_hash = _hash_password(new_password)
    with get_db() as conn:
        conn.execute(
            """INSERT INTO app_auth (id, password_hash) VALUES (1, ?)
               ON CONFLICT(id) DO UPDATE SET password_hash = excluded.password_hash""",
            (new_hash,),
        )


def create_token() -> str:
    """Genera y registra un token de sesión."""
    token = secrets.token_urlsafe(32)
    _active_tokens.add(token)
    return token


def is_token_valid(token: str) -> bool:
    return bool(token) and token in _active_tokens


def revoke_token(token: str):
    _active_tokens.discard(token)
