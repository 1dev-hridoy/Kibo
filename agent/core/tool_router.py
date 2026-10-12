"""Tool shortlisting — keep the 140-tool dump out of the prompt.

Kibo registers 140 tools, and injecting all of them costs roughly 2.5k
tokens before the user has said anything. That is 61% of a 4,096-token
context window, and it is 122% of FunctionGemma's 2,048-token window, so
the model never sees the user's question.

This module scores each tool against the user's message and returns a
shortlist. Scoring is lexical (TF-IDF over tool name + docstring) rather
than embedding-based, for three reasons:

  * it runs in microseconds with no model load, so it works while the
    agent is still warming up;
  * it is deterministic, which makes the agent loop reproducible and
    testable;
  * a 0.6B embedding model on CPU would cost more than it saves.

Set KIBO_TOOL_ROUTER=off to restore the old behaviour and send every
tool. That is the escape hatch if shortlisting ever hides a tool the user
actually needs.
"""

import math
import os
import re
from collections import Counter



ALWAYS_ON = (
    "get_system_info",
    "search_apps",
    "read_file",
    "brief_today",
)

_WORD_RE = re.compile(r"[a-z0-9_]+")



_STOP = frozenset("""
a an the and or of to in on for with is are be it its this that from by
use used using when do does can will you your if not no ok any all at as
tool call get set new add one more e g i
""".split())


def _enabled():
    return os.environ.get("KIBO_TOOL_ROUTER", "on").strip().lower() \
        not in ("off", "0", "false", "no")




def _tokens(text):
    return [w for w in _WORD_RE.findall((text or "").lower())
            if w not in _STOP and len(w) > 1]




class ToolRouter:
    """Scores tools against a query and returns the best few.

    Built once per tool set. Safe to call from the agent loop: `route`
    holds no mutable state.
    """

    def __init__(self, tools):
        self.names = []
        self.docs = {}
        for fn in tools:
            name = getattr(fn, "__name__", None)
            if not name:
                continue

            
            doc = (fn.__doc__ or "").strip()
            self.names.append(name)

        
            self.docs[name] = _tokens(name.replace("_", " ")) + _tokens(doc)

        self.n = len(self.names)
        self.df = Counter()
        for toks in self.docs.values():
            for term in set(toks):
                self.df[term] += 1


      
        self.idf = {
            t: math.log(1 + (self.n / (1 + c)))
            for t, c in self.df.items()
        }



    def score(self, query):
        """Return {tool_name: score} for every tool, best first."""
        qt = _tokens(query)
        if not qt or not self.n:
            return {}
        raw = (query or "").lower()
        qcount = Counter(qt)
        out = {}
        for name in self.names:
            toks = self.docs[name]
            tf = Counter(toks)
            s = 0.0
            for term, qn in qcount.items():
                f = tf.get(term, 0)
                if not f:
                    continue


             
                s += self.idf.get(term, 0.0) * (1 + math.log(f)) * qn



            bare = name.replace("_", "")
            if bare and bare in raw.replace(" ", "").replace("_", ""):
                s += 12.0
            if s > 0:
                out[name] = s
        return out



    def route(self, query, k=8):
        """Top-k tool names for a query, always-on tools first."""
        if not _enabled():
            return list(self.names)
        scored = self.score(query)
        picked = [n for n in ALWAYS_ON if n in self.docs]
        ranked = sorted(scored.items(), key=lambda kv: -kv[1])
        for name, _ in ranked:
            if len(picked) >= max(k, len(ALWAYS_ON)):
                break
            if name not in picked:
                picked.append(name)




        if not ranked and picked == [n for n in ALWAYS_ON if n in self.docs]:
            return picked
        return picked


_DEFAULT = None


def get_router(tools):
    """Cached router for a tool set (rebuilt only when the set changes)."""
    global _DEFAULT
    if _DEFAULT is None or _DEFAULT.names != [
            getattr(fn, "__name__", None) for fn in tools]:
        _DEFAULT = ToolRouter(tools)
    return _DEFAULT


def route(tools, query, k=8):
    return get_router(tools).route(query, k)
