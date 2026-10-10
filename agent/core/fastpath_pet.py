"""
Pet / widget / reminder / briefing fast-path routing.
Split out of fastpath.py to keep modules within the line cap.
"""
import re


def pet_route(t):
    _pet_any = ("fireworks", "firework", "boom", "cracker", "blast",
                "sparkle", "sparkles", "shiny", "twinkle", "glitter",
                "orbit", "satellite", "halo", "rainbow", "pride", "colors",
                "music", "sing", "song", "melody", "tune", "humming",
                "giggle", "teehee", "laugh", "dance", "celebrate", "party",
                "yay", "hooray", "clap", "zoomies", "zoom",
                "heartrain", "heart rain", "hearts rain", "falling hearts",
                "shower", "love", "hearts", "heart", "hug", "kiss", "cuddle",
                "sleepy", "yawn", "nap", "bedtime", "go to sleep",
                "mochi", "pixel", "showcase", "parade", "play all", "show all",
                "flip", "backflip", "frontflip", "somersault", "tumble",
                "airflip", "spin me", "coinflip", "coin flip", "flip a coin",
                "toss a coin", "heads or tails", "coin")


    
    _pet_distinct = ("fireworks", "firework", "boom", "cracker", "blast",
                     "sparkle", "sparkles", "shiny", "twinkle", "glitter",
                     "orbit", "satellite", "halo", "rainbow", "pride",
                     "music", "sing", "song", "melody", "tune",
                     "giggle", "teehee", "laugh", "dance", "celebrate",
                     "party", "yay", "hooray", "zoomies", "zoom",
                     "heartrain", "heart rain", "shower", "love", "hearts",
"hug", "kiss", "cuddle", "sleepy", "yawn", "nap", "bedtime",
                     "go to sleep", "mochi", "pixel", "showcase", "parade", "play all", "show all",
                     "flip", "backflip", "somersault", "tumble", "spin me",
                     "coinflip", "coin flip", "flip a coin", "toss a coin",
                     "heads or tails", "coin")
    if re.search(r"\b(pet|kibo|mochi)\b", t) and any(w in t for w in _pet_any):
        return [("pet_animate", {"action": t})]



  
    if re.search(r"\bhistory\b", t) or re.match(
            r"^(?:list|read|what\s+(?:were|are))(?:\s+the)?\s+"
            r"(?:all\s+|my\s+|saved\s+)?messages$", t):
        return [("pet_message_history", {})]
    if re.match(r"^(?:(?:show|play|replay|display|scroll)\s+(?:me\s+)?"
                r"(?:(?:all|every|my|the|past|old|previous|saved|widget|chat|pet)"
                r"\s+)*messages?"
                r"|(?:all|every|my)\s+messages)$", t):
        return [("pet_show_all", {})]

    if re.search(r"\bi love you\b", t):
        return [("pet_love", {})]
    if len(t.split()) <= 3 and not re.search(r"\d", t) and \
            any(w in t for w in _pet_distinct):
        return [("pet_animate", {"action": t})]


    m = re.match(r"^pet\s+show\s+(.+)$", t)
    if m:
        return [("pet_show", {"text": m.group(1).strip()})]
    m = re.match(r"^pet\s+send\s+(.+)$", t)
    if m:
        return [("pet_send", {"text": m.group(1).strip()})]
    m = re.match(r"^(?:kibo\s+message\s+set|set\s+(?:kibo\s+|widget\s+)?message"
                 r"|set\s+(?:kibo|widget)|widget\s+(?:show|set)"
                 r"(?:\s+(?:message|text))?"
                 r"|show\s+(?:on\s+)?(?:the\s+)?widget)\s+(.+)$", t)
    if m and not re.search(r"\b(volume|brightness|sound|model)\b", m.group(1)):
        return [("widget_set_message", {"message": m.group(1).strip()})]
    if re.match(r"^(?:clear|reset|hide)\s+(?:the\s+)?widget(?:\s+message|\s+text)?$|^(?:widget|pet|weight|wedget|wiget)\s+(?:clear|reset|hide|free)$", t):
        return [("widget_clear", {})]
    if re.search(r"\bwidget\b.*\bfree\b|\bfree\b.*\bwidget\b", t):
        return [("widget_clear", {})]
    if re.search(r"\bdrink\b.*\bwater\b|\bwater\b.*\bdrink\b|\bhydrate\b|\bglass of water\b", t):
        return [("remind_water", {})]
    if re.search(r"\btouch grass\b|\bgo outside\b|\bfresh air\b", t):
        return [("remind_grass", {})]
    if re.match(r"^(?:time to |go |come on,? )?(?:stretch|do some stretching)(?:\s+(?:a bit|now|please))?$", t):
        return [("remind_stretch", {})]
    if re.search(r"\b(?:rest|give).*eyes\b|\beye break\b|\bblink\b.*\bbreak\b|\b20-20-20\b", t):
        return [("remind_eyes", {})]
    if re.search(r"\bposture\b|\bsit (?:up )?straight\b|\bstraighten.*back\b|\bsit tall\b", t):
        return [("remind_posture", {})]
    if re.match(r"^(?:turn\s+)?reminders?\s+on$|^(?:enable|start)\s+reminders?$", t):
        return [("reminders_on", {})]
    if re.match(r"^(?:turn\s+)?reminders?\s+off$|^(?:disable|stop|pause)\s+reminders?$", t):
        return [("reminders_off", {})]
    if re.match(r"^reminders?(?:\s+status)?$", t):
        return [("reminders_status", {})]
    if re.match(r"^(?:(?:brief|breaf|breif|brif)(?:\s+(?:me|today|the\s+day))?|daily\s+brief(?:ing)?|morning\s+brief(?:ing)?|today'?s\s+brief(?:ing)?|what'?s\s+(?:up|on)\s+today)$", t):
        return [("brief_today", {})]
    if re.match(r"^(?:turn\s+)?briefing\s+on$|^(?:enable|start)\s+(?:daily\s+)?briefing$", t):
        return [("briefing_on", {})]
    if re.match(r"^(?:turn\s+)?briefing\s+off$|^(?:disable|stop)\s+(?:daily\s+)?briefing$", t):
        return [("briefing_off", {})]
    if re.match(r"^briefing(?:\s+status)?$", t):
        return [("briefing_status", {})]
    if re.search(r"\bbrief(?:ing|_today)?\b", t):
        return [("brief_today", {})]
    if re.match(r"^(?:live(?:\s+(?:screen|view))?|show\s+(?:live|my)\s+screen)$", t):
        return [("take_screenshot_now", {})]

    return None
