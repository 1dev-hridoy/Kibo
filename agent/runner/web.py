"""
Web utilities — DuckDuckGo search with RAG content extraction,
URL fetching with HTML-to-text conversion.
"""

import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser







class _HTMLTextExtractor(HTMLParser):
    """Strip HTML tags and extract readable text content."""

    _SKIP_TAGS = {"script", "style", "noscript", "head", "meta", "link"}
    _INLINE_TAGS = {"br", "hr", "p", "div", "h1", "h2", "h3", "h4", "h5", "h6",
                    "li", "tr", "blockquote", "pre", "section", "article"}




    def __init__(self):
        super().__init__()
        self._result = []
        self._skip_depth = 0

        

    def handle_starttag(self, tag, attrs):
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1
        elif tag in self._INLINE_TAGS:
            self._result.append("\n")

    def handle_endtag(self, tag):
        if tag in self._SKIP_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
        elif tag in self._INLINE_TAGS:
            self._result.append("\n")

    def handle_data(self, data):
        if self._skip_depth == 0:
            self._result.append(data)

    def get_text(self):
        text = "".join(self._result)
        # Collapse whitespace
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def html_to_text(html: str) -> str:
    """Convert HTML content to clean readable text."""
    extractor = _HTMLTextExtractor()
    try:
        extractor.feed(html)
    except Exception:
        pass
    return extractor.get_text()







def fetch_url_text(url: str, max_chars: int = 8000) -> str:
    """Fetch a URL and return its clean text content (HTML stripped).

    Args:
        url: The URL to fetch.
        max_chars: Maximum characters to return.

    Returns:
        Clean text content or error message.
    """
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; Kibo/1.0)",
            "Accept": "text/html,application/xhtml+xml",
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read(max_chars * 3)  # read extra for HTML overhead
            # Try utf-8 first, fall back to latin-1
            try:
                html = raw.decode("utf-8")
            except UnicodeDecodeError:
                html = raw.decode("latin-1", errors="replace")

        if "text/html" in content_type or "html" in url.lower():
            text = html_to_text(html)
        else:
            text = html

        if len(text) > max_chars:
            text = text[:max_chars] + "\n... [truncated]"

        return text

    except urllib.error.HTTPError as e:
        return f"HTTP Error {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return f"URL Error: {e.reason}"
    except Exception as e:
        return f"Error fetching URL: {e}"









def duckduckgo_search(query: str, max_results: int = 5) -> list[dict]:
    """Search DuckDuckGo HTML and extract result titles, URLs, and snippets.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return.

    Returns:
        List of dicts with 'title', 'url', 'snippet' keys.
    """
    try:
        encoded = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        results = []



        links = re.findall(
            r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            html, re.DOTALL
        )

        for raw_url, title_html in links[:max_results]:
            title = re.sub(r"<[^>]+>", "", title_html).strip()





            result_url = ""
            uddg = re.search(r"uddg=([^&]+)", raw_url)
            if uddg:
                result_url = urllib.parse.unquote(uddg.group(1))
            elif raw_url.startswith("http"):
                result_url = raw_url
            elif raw_url.startswith("//"):
                result_url = "https:" + raw_url




            snippet = ""
            snippet_match = re.search(
                r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
                html[html.find(raw_url):], re.DOTALL
            )
            if snippet_match:
                snippet = re.sub(r"<[^>]+>", "", snippet_match.group(1)).strip()

            if title or result_url:
                results.append({
                    "title": title,
                    "url": result_url,
                    "snippet": snippet,
                })

        return results

    except Exception:

        return []
    


def web_search_and_extract(query: str, max_results: int = 3, fetch_top: int = 1) -> str:
    """Search DuckDuckGo and optionally fetch content from top results (RAG).

    Args:
        query: Search query.
        max_results: Number of search results to return.
        fetch_top: Number of top results to fetch full text from.

    Returns:
        Formatted string with search results and extracted content.
    """
    results = duckduckgo_search(query, max_results)

    if not results:
        return f"No search results found for '{query}'."

    lines = [f"Search results for '{query}':\n"]

    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['title']}")
        lines.append(f"   URL: {r['url']}")
        if r["snippet"]:
            lines.append(f"   {r['snippet']}")
        lines.append("")




    if fetch_top > 0 and results:
        lines.append("--- Fetched Content ---\n")
        for r in results[:fetch_top]:
            if r["url"]:
                lines.append(f"Content from: {r['title']} ({r['url']})")
                content = fetch_url_text(r["url"], max_chars=4000)
                lines.append(content)
                lines.append("\n---\n")



    return "\n".join(lines)
