"""
Utility fast-path routing — maths, units, passwords, text tools.
Placed before the shell-command routes so plain English like
"make me a password" is never executed as a shell command.
"""
import re


def _num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def util_route(t):
    t = (t or "").strip().lower()
    if not t:
        return None



   
    m = re.search(
        r"convert\s+(-?\d+(?:\.\d+)?)\s*([a-z/]+)\s+(?:in)?to\s+([a-z/]+)", t)
    if m:
        v = _num(m.group(1))
        if v is not None:
            return [("convert_units", {"value": v, "from_unit": m.group(2),
                                       "to_unit": m.group(3)})]
        





    m = re.match(r"^(?:calculate|compute|what(?:'s| is)\s+)\s*"
                 r"([-+0-9./*%()^ ]+)$", t)
    if m and any(c in m.group(1) for c in "+-*/^()"):
        return [("calculate", {"expression": m.group(1).strip()})]





    if re.search(r"\b(password|passphrase|random (?:string|secret|key)|"
                 r"api key|secret key)\b", t):
        m = re.search(r"(\d{1,3})\s*(?:char|character|digit|long)", t)
        args = {"length": int(m.group(1)) if m else 20}
        if re.search(r"\b(no|without|skip)\b.*\bsymbol", t):
            args["use_symbols"] = False
        return [("generate_password", args)]





    if re.search(r"\b(word count|count the words|how many words|"
                 r"reading time|text stats|character count)\b", t):
        m = re.search(r"(?:in|of)\s+[\"'`“](.{1,4000}?)[\"'`”]", t)
        text = m.group(1) if m else t
        return [("text_stats", {"text": text})]






    m = re.match(r"^(?:convert\s+)?(?:the\s+)?(?:text\s+)?"
                 r"(.{1,4000}?)\s+(?:to|into)\s+"
                 r"(base\s*64|url\s*(?:en|de)code|upper\s*case|lower\s*case|"
                 r"title\s*case|reverse)\s*$", t)


    
    if m:
        raw, op = m.group(1), m.group(2)
        raw = raw.strip().strip("\"'“”")
        op = op.replace(" ", "_")



        op = {"upper_case": "upper", "lower_case": "lower",
              "title_case": "title"}.get(op, op)
        op = re.sub(r"^url_(en|de)code$", r"url_\1code", op)
        op = op.replace("base64", "base64")


        return [("transform_text", {"text": raw, "operation": op})]
    if re.match(r"^reverse\s+(?:this\s+|the\s+)?(?:text\s+)?", t):
        m2 = re.search(r"[\"'`“](.{1,4000}?)[\"'`”]", t)





        if m2:
            return [("transform_text", {"text": m2.group(1),
                                        "operation": "reverse"})]





    if re.search(r"\b(how long until|how long till|time until|countdown to|"
                 r"when is|how long until)\b", t):
        m = re.search(r"(?:until|till|to|is)\s+(.+)$", t)
        if m:
            return [("time_until", {"target": m.group(1).strip()})]



        
    if re.search(r"\b(large|big|huge) files\b", t) and \
            re.search(r"\b(disk|storage|space|folder|directory|find|list|"
                      r"show|where)\b", t):
        m = re.search(r"(?:in|from)\s+(.+)$", t)
        return [("find_large_files", {"directory": m.group(1).strip()
                                      if m else ""})]


 
    m = re.search(r"replace\s+(.+?)\s+with\s+(.+?)\s+(?:in|inside)\s+"
                  r"(?:the\s+)?(?:file\s+)?(.+)$", t)
    if m:
        return [("find_replace_in_file", {
            "path": m.group(3).strip(),
            "find": m.group(1).strip().strip("\"'"),
            
            "replace": m.group(2).strip().strip("\"'"),
            "dry_run": bool(re.search(r"\b(dry run|preview|just show|check)\b", t)),
        })]

    return None