"""
Everyday utility tools — stdlib only, no extra dependencies.
"""

import ast
import base64
import binascii
import datetime
import hashlib
import math
import operator
import os
import re
import secrets
import string
import urllib.parse



import needle




def _safe_read(path, limit=400000):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read(limit)


@needle.tool
def calculate(expression: str) -> str:
    """Evaluate a maths expression and return the result.
    Supports + - * / // % ** and parentheses, plus sin/cos/tan/sqrt/
    log/exp/pi/e. Use when the user asks to compute numbers, percentages,
    a tip split, or convert maths into a value.
    Example: calculate('18*1.2 + 5') or calculate('sqrt(144)').
    """




    print(f"[Tool] calculate('{expression}')")

    ops = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }



    funcs = {
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
        "exp": math.exp, "abs": abs, "round": round, "floor": math.floor,
        "ceil": math.ceil,
    }


    names = {"pi": math.pi, "e": math.e}






    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("only numbers allowed")

        
        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            return ops[type(node.op)](_eval(node.left), _eval(node.right))
        






        if isinstance(node, ast.UnaryOp) and isinstance(node.op,
                                                        (ast.UAdd, ast.USub)):
            v = _eval(node.operand)
            return +v if isinstance(node.op, ast.UAdd) else -v
        if isinstance(node, ast.Name) and node.id in names:
            return names[node.id]
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id in funcs:
            return funcs[node.func.id](*[_eval(a) for a in node.args])
        raise ValueError("unsupported expression")




    try:
        value = _eval(ast.parse(expression, mode="eval"))
    except ZeroDivisionError:
        return "Error: division by zero."
    except (SyntaxError, ValueError, KeyError, TypeError,
            OverflowError) as e:
        return f"Error: {e}"
    if isinstance(value, float):
        if value.is_integer() and abs(value) < 1e15:
            value = int(value)
        else:
            value = round(value, 10)
    return f"{expression} = {value}"







@needle.tool
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between units of length, mass, temperature, volume, speed,
    data size and time. Use when the user asks to convert measurements,
    e.g. 'convert 5 miles to km' or '90 c to f'.
    """

    print(f"[Tool] convert_units({value}, '{from_unit}', '{to_unit}')")

    def n(u):
        return _norm_unit(u)

    





    linear = {
        "length": {
            "m": 1.0, "meter": 1.0, "meters": 1.0, "km": 1000.0,
            "kilometer": 1000.0, "kilometers": 1000.0, "cm": 0.01,
            "centimeter": 0.01, "centimeters": 0.01, "mm": 0.001,
            "mile": 1609.344, "miles": 1609.344, "mi": 1609.344,
            "yard": 0.9144, "yards": 0.9144, "yd": 0.9144,
            "foot": 0.3048, "feet": 0.3048, "ft": 0.3048,
            "inch": 0.0254, "inches": 0.0254, "in": 0.0254,
            "nautical mile": 1852.0,
        },
        "mass": {
            "kg": 1.0, "kilogram": 1.0, "kilograms": 1.0,
            "g": 0.001, "gram": 0.001, "grams": 0.001,
            "mg": 1e-6, "lb": 0.45359237, "lbs": 0.45359237,
            "pound": 0.45359237, "pounds": 0.45359237,
            "oz": 0.0283495, "ounce": 0.0283495, "ounces": 0.0283495,
            "tonne": 1000.0, "ton": 907.18474,
        },
        "volume": {
            "l": 1.0, "liter": 1.0, "liters": 1.0, "litre": 1.0,
            "litres": 1.0, "ml": 0.001, "milliliter": 0.001,
            "milliliters": 0.001, "gal": 3.785411784, "gallon": 3.785411784,
            "gallons": 3.785411784, "cup": 0.236588, "cups": 0.236588,
            "floz": 0.0295735,
        },
        "speed": {
            "mps": 1.0, "kph": 0.277778, "kmh": 0.277778,
            "km/h": 0.277778, "mph": 0.44704, "knot": 0.514444,
        },
        "data": {
            "b": 1.0, "byte": 1.0, "bytes": 1.0,
            "kb": 1024.0, "kib": 1024.0, "mb": 1048576.0,
            "mib": 1048576.0, "gb": 1073741824.0, "gib": 1073741824.0,
            "tb": 1099511627776.0, "tib": 1099511627776.0,
            "bit": 0.125, "bits": 0.125,
        },
        "time": {
            "s": 1.0, "sec": 1.0, "second": 1.0, "seconds": 1.0,
            "min": 60.0, "minute": 60.0, "minutes": 60.0,
            "h": 3600.0, "hr": 3600.0, "hour": 3600.0, "hours": 3600.0,
            "day": 86400.0, "days": 86400.0, "week": 604800.0,
            "weeks": 604800.0,
        },
    }





    temp = {"c": "c", "celsius": "c", "centigrade": "c",
            "f": "f", "fahrenheit": "f", "k": "k", "kelvin": "k"}

    f, t = n(from_unit), n(to_unit)
    for table in linear.values():
        if f in table and t in table:
            out = value * table[f] / table[t]
            return f"{value} {_norm_unit(from_unit)} = {out:.6g} {t}"

        


    if f in temp and t in temp:
        c = value if temp[f] == "c" else (
            (value - 32) * 5 / 9 if temp[f] == "f" else value - 273.15)
        if temp[t] == "c":
            out = c
        elif temp[t] == "f":
            out = c * 9 / 5 + 32
        else:
            out = c + 273.15
        return f"{value} {_norm_unit(from_unit)} = {out:.4g} {t}"
    return (f"Error: cannot convert '{from_unit}' to '{to_unit}'. "
            f"Try length, mass, temperature, volume, speed, data or time.")


def _norm_unit(u):
    u = (u or "").strip().lower()
    u = re.sub(r"[^a-z/ ]", "", u)
    return u.rstrip("s") if u not in ("in", "ft") else u


@needle.tool
def generate_password(length: int = 20, use_symbols: bool = True,
                      avoid_ambiguous: bool = True) -> str:
    """Generate a cryptographically secure random password.
    Use when the user asks for a strong password, a random string,
    an API key or a PIN.
    """

    print(f"[Tool] generate_password(length={length})")
    try:
        length = max(6, min(128, int(length)))
    except (TypeError, ValueError):
        length = 20
    pool = string.ascii_letters + string.digits
    if use_symbols:
        pool += "!@#$%^&*()-_=+[]{}?"
    if avoid_ambiguous:
        pool = "".join(c for c in pool if c not in "0O1lI")
    return "".join(secrets.choice(pool) for _ in range(length))


@needle.tool
def text_stats(text: str) -> str:
    """Count words, characters, lines and sentences in some text,
    and estimate reading time. Use when the user asks how long
    something is, word count, or reading time.
    """



    print("[Tool] text_stats()")
    words = re.findall(r"\S+", text or "")
    lines = (text or "").splitlines()
    sentences = [s for s in re.split(r"[.!?]+", text or "") if s.strip()]
    longest = max((len(w) for w in words), default=0)
    read_min = max(1, round(len(words) / 200)) if words else 0
    return (f"Words: {len(words)}\n"
            f"Characters: {len(text or '')}\n"
            f"Characters (no spaces): {len(text or '') - text.count(' ')}\n"
            f"Lines: {len(lines)}\n"
            f"Sentences: {len(sentences)}\n"
            f"Longest word: {longest}\n"
            f"Reading time: ~{read_min} min")





@needle.tool
def transform_text(text: str, operation: str) -> str:
    """Transform a piece of text: upper, lower, title, sentence, reverse,
    strip, unique lines, dedupe, base64 encode or decode, url encode
    or decode, or escape for JSON.
    Use when the user asks to reformat, capitalise, reverse, encode
    or decode some text.
    """




    print(f"[Tool] transform_text(operation='{operation}')")
    op = re.sub(r"[\s-]+", "_", (operation or "").strip().lower())
    t = text or ""


    try:
        if op in ("upper", "uppercase", "upper_case"):
            return t.upper()


        
        if op in ("lower", "lowercase", "lower_case"):
            return t.lower()
        if op in ("title", "titlecase", "title_case"):



            return t.title()
        if op in ("sentence", "sentencecase", "sentence_case"):
            out = t.lower().strip()
            return out[:1].upper() + out[1:]


        
        if op == "reverse":
            return t[::-1]
        if op == "strip":



            return t.strip()
        if op in ("unique_lines", "unique"):
            seen, out = set(), []
            for ln in t.splitlines():
                if ln not in seen:
                    seen.add(ln)
                    out.append(ln)
            return "\n".join(out)


        
        if op == "base64_encode":
            return base64.b64encode(t.encode()).decode()
        if op in ("base64_decode", "decode_base64"):
            return base64.b64decode(t.encode()).decode(errors="replace")
        if op in ("url_encode", "urlencode"):
            return urllib.parse.quote_plus(t)
        if op in ("url_decode", "urldecode"):
            return urllib.parse.unquote_plus(t)
        if op in ("json_escape", "escape"):
            return t.replace("\\", "\\\\").replace('"', '\\"')
        if op in ("md5",):
            return hashlib.md5(t.encode()).hexdigest()
        if op in ("sha256",):
            return hashlib.sha256(t.encode()).hexdigest()


        
    except (binascii.Error, ValueError, UnicodeError) as e:
        return f"Error: {e}"
    return (f"Error: unknown operation '{operation}'. Try upper, lower, "
            f"title, sentence, reverse, strip, unique_lines, base64_encode, "
            f"base64_decode, url_encode, url_decode, json_escape, md5 "
            f"or sha256.")




@needle.tool
def find_replace_in_file(path: str, find: str, replace: str,
                         dry_run: bool = False) -> str:
    """Find and replace text inside a file, optionally previewing first
    with dry_run=True. Use when the user wants a string swapped
    throughout a file, e.g. changing a hostname or a version number.
    """



    print(f"[Tool] find_replace_in_file('{path}')")
    try:
        text = _safe_read(path, limit=20_000_000)
    except OSError as e:
        return f"Error: cannot read {path}: {e}"
    count = text.count(find)



    if count == 0:
        return f"'{find}' not found in {path}. Nothing changed."
    if not find:
        return "Error: the search text is empty."

    
    if dry_run:
        return f"Would replace {count} occurrence(s) of '{find}' in {path}."
    updated = text.replace(find, replace)
    try:
        tmp = path + ".kibo.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(updated)
        os.replace(tmp, path)
    except OSError as e:
        return f"Error: cannot write {path}: {e}"
    return f"Replaced {count} occurrence(s) of '{find}' in {path}."


@needle.tool
def find_large_files(directory: str, limit: int = 10,
                     min_size_mb: float = 50.0) -> str:
    """List the largest files in a directory tree, above a size
    threshold. Use when the user asks what's eating disk space
    or where the big files are.
    """


    print(f"[Tool] find_large_files('{directory}')")
    root = os.path.expanduser(directory or os.path.expanduser("~"))
    if not os.path.isdir(root):
        return f"Error: '{root}' is not a directory."
    floor = max(0.0, float(min_size_mb)) * 1024 * 1024
    try:
        cap = max(1, min(100, int(limit)))
    except (TypeError, ValueError):
        cap = 10
    found = []


    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in
                   (".git", "node_modules", "__pycache__", ".venv", "venv")]
        for name in files:
            p = os.path.join(base, name)
            try:
                size = os.path.getsize(p)
            except OSError:
                continue
            if size >= floor:
                found.append((size, p))



    if not found:


        return (f"No files over {min_size_mb:g} MB found in {root}.")
    found.sort(reverse=True)
    lines = [f"{len(found)} file(s) over {min_size_mb:g} MB in {root}:"]
    for size, p in found[:cap]:
        lines.append(f"  {size / 1048576:9.1f} MB  {p}")
    return "\n".join(lines)




@needle.tool
def time_until(target: str) -> str:
    """Work out how long until a date or time, or how long ago it was.
    Accepts natural input like 'tomorrow', 'in 3 hours', 'friday',
    '2026-12-25' or '14:30'. Use when the user asks how long until
    something, or what the date is.
    """



    print(f"[Tool] time_until('{target}')")
    now = datetime.datetime.now()
    tgt = None
    t = (target or "").strip().lower()
    rel = re.match(r"in\s+(\d+)\s*(minute|minutes|min|hour|hours|hr|day|days|week|weeks)", t)
    if rel:
        n = int(rel.group(1))
        unit = rel.group(2).rstrip("s")
        mult = {"minute": 60, "min": 60, "hour": 3600, "hr": 3600,
                "day": 86400, "week": 604800}.get(unit, 60)
        tgt = now + datetime.timedelta(seconds=n * mult)
    elif t == "now":
        tgt = now



    else:
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d",
                    "%d/%m/%Y", "%m/%d/%Y", "%H:%M"):
            try:
                tgt = datetime.datetime.strptime((target or "").strip(), fmt)



                if fmt == "%H:%M":
                    tgt = now.replace(hour=tgt.hour, minute=tgt.minute,
                                      second=0, microsecond=0)
                    if tgt < now:
                        tgt += datetime.timedelta(days=1)
                break
            except ValueError:


                continue
        if tgt is None:
            return (f"Could not understand '{target}'. Try 'tomorrow', "
                    f"'in 2 hours', '2026-12-25' or '14:30'.")

        
    delta = tgt - now
    secs = int(abs(delta).total_seconds())
    d, rem = divmod(secs, 86400)
    h, rem = divmod(rem, 3600)

    
    m, s = divmod(rem, 60)
    span = f"{d}d {h}h {m}m" if d else (f"{h}h {m}m" if h else f"{m}m {s}s")
    word = "until" if delta.total_seconds() >= 0 else "ago"
    return (f"Now: {now.strftime('%Y-%m-%d %H:%M')}\n"
            f"Target: {tgt.strftime('%Y-%m-%d %H:%M')}\n"
            f"That is {span} {word}.")