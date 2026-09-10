"""
Hashing utilities — checksum generation for files/strings
and hash algorithm identification from hash values.
"""

import hashlib
import os
import re





# ═══════════════════════════════════════════════════════════════════════
# Hash Checksum Generation
# ═══════════════════════════════════════════════════════════════════════

def generate_checksum(file_path: str, algorithms: list[str] | None = None) -> dict:
    """Generate MD5, SHA1, SHA256, and SHA512 checksums for a file.

    Args:
        file_path: Path to the file.
        algorithms: List of hash algorithms (default: all four).

    Returns dict with file info and hash values.
    """
    if not os.path.isfile(file_path):
        return {"error": f"File not found: {file_path}"}

    if algorithms is None:
        algorithms = ["md5", "sha1", "sha256", "sha512"]

    hashes = {}
    size = os.path.getsize(file_path)

    for algo in algorithms:
        try:
            h = hashlib.new(algo)
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    h.update(chunk)
            hashes[algo] = h.hexdigest()
        except ValueError as e:
            hashes[algo] = f"error: {e}"

    return {
        "file": os.path.abspath(file_path),
        "size_bytes": size,
        "hashes": hashes,
    }






def hash_string(text: str, algorithm: str = "sha256") -> dict:
    """Hash a plaintext string with the specified algorithm.

    Args:
        text: The string to hash.
        algorithm: Hash algorithm (md5, sha1, sha256, sha512, sha3_256, blake2b).

    Returns dict with the hex digest.
    """
    try:
        h = hashlib.new(algorithm)
        h.update(text.encode("utf-8"))
        return {"text": text, "algorithm": algorithm, "hash": h.hexdigest()}
    except ValueError as e:
        return {"error": f"Unknown algorithm '{algorithm}': {e}"}





# ═══════════════════════════════════════════════════════════════════════
# Hash Algorithm Identification
# ═══════════════════════════════════════════════════════════════════════

_HASH_PATTERNS = [
    (r"^[a-fA-F0-9]{32}$", "MD5"),
    (r"^[a-fA-F0-9]{40}$", "SHA1"),
    (r"^[a-fA-F0-9]{64}$", "SHA256"),
    (r"^[a-fA-F0-9]{128}$", "SHA512"),
    (r"^\$2[aby]\$\d{2}\$.{53}$", "bcrypt"),
    (r"^\$argon2(id|i|d)\$", "Argon2"),
    (r"^[a-fA-F0-9]{16}$", "CRC64 / MurmurHash64 (possible)"),
    (r"^\$pbkdf2(-hmac)?-sha\d+", "PBKDF2"),
]





def identify_hash(hash_value: str) -> dict:
    """Identify the most likely hash algorithm for a given hash string.

    Args:
        hash_value: The hash string to identify.

    Returns dict with possible algorithms and confidence.
    """
    hash_value = hash_value.strip()

    candidates = []
    for pattern, name in _HASH_PATTERNS:
        if re.match(pattern, hash_value):
            candidates.append(name)

    return {
        "hash": hash_value[:80] + ("..." if len(hash_value) > 80 else ""),
        "length": len(hash_value),
        "hex": bool(re.fullmatch(r"[a-fA-F0-9]+", hash_value)),
        "possible_algorithms": candidates,
    }
