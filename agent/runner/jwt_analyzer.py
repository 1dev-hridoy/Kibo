"""
JWT (JSON Web Token) decoder and security auditor.
"""

import base64
import datetime
import json


def _b64url_decode(data: str) -> bytes:
    """Decode a base64url-encoded string."""
    data += "=" * (4 - len(data) % 4)
    return base64.urlsafe_b64decode(data)


def decode_jwt(token: str) -> dict:
    """Decode a JWT token and audit its security.

    Args:
        token: The full JWT string (header.payload.signature).

    Returns dict with decoded header, payload, signature, and security warnings.
    """
    warnings = []

    parts = token.split(".")
    if len(parts) != 3:
        return {"error": "Invalid JWT format (expected 3 dot-separated parts)"}

    try:
        header = json.loads(_b64url_decode(parts[0]))
    except Exception as e:
        return {"error": f"Failed to decode header: {e}"}

    try:
        payload = json.loads(_b64url_decode(parts[1]))
    except Exception as e:
        return {"error": f"Failed to decode payload: {e}"}




    # security checks
    alg = header.get("alg", "").upper()
    if alg == "NONE":
        warnings.append("CRITICAL: 'none' algorithm — token is forged, no signature verification")

    if alg in ("HS256", "HS384", "HS512"):
        warnings.append("INFO: Symmetric algorithm — signing key must remain secret")

    if alg.startswith("RS") or alg.startswith("ES") or alg.startswith("PS"):
        warnings.append("INFO: Asymmetric algorithm — public key safe to expose")

    if payload.get("exp"):
        try:
            exp = datetime.datetime.utcfromtimestamp(payload["exp"])
            if exp < datetime.datetime.utcnow():
                warnings.append("EXPIRED: Token has expired")
        except (OSError, OverflowError):
            pass

    if payload.get("iat"):
        try:
            iat = datetime.datetime.utcfromtimestamp(payload["iat"])
            now = datetime.datetime.utcnow()
            age_days = (now - iat).days
            if age_days > 365:
                warnings.append(f"AGE: Token was issued {age_days} days ago")
        except (OSError, OverflowError):
            pass



    return {
        "header": header,
        "payload": payload,
        "signature": parts[2][:40] + "..." if len(parts[2]) > 40 else parts[2],
        "warnings": warnings,
    }
