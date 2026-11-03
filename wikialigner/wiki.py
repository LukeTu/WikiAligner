"""MediaWiki client: search, language links, revision history and revision HTML.

Revision HTML is immutable once saved, so it is cached on disk by (language, revid, variant).
"""
from __future__ import annotations

import gzip
import re
import threading
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Iterator

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import HTML_CACHE_DIR, USER_AGENT

_LANG_RE = re.compile(r"^[a-z][a-z0-9-]{1,30}$")

# Languages whose Wikipedia converts between scripts on request.
VARIANTS: dict[str, list[str]] = {
    "zh": ["zh-hans", "zh-hant", "zh-cn", "zh-tw", "zh-hk"],
    "sr": ["sr-ec", "sr-el"],
}


class WikiError(Exception):
    """A request to Wikipedia failed in a way the user should be told about."""


@dataclass
class Revision:
    revid: int
    timestamp: str
    parentid: int = 0
    user: str = ""
    comment: str = ""
    size: int = 0
    tags: list[str] = field(default_factory=list)
    minor: bool = False

    @classmethod
    def from_api(cls, r: dict) -> "Revision":
        return cls(
            revid=r["revid"],
            timestamp=r.get("timestamp", ""),
            parentid=r.get("parentid", 0),
            user=r.get("user", ""),
            comment=r.get("comment", ""),
            size=r.get("size", 0),
            tags=list(r.get("tags", [])),
            minor=bool(r.get("minor", False)),
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PageInfo:
    lang: str
    title: str
    pageid: int
    lastrevid: int
    length: int
    qid: str
    langlinks: list[dict]  # [{"lang", "title", "autonym"}]


def check_lang(lang: str) -> str:
    lang = (lang or "").strip().lower()
    if not _LANG_RE.match(lang):
        raise WikiError(f"Invalid language code: {lang!r}")
    return lang


def page_url(lang: str, title: str, revid: int | None = None) -> str:
    base = f"https://{lang}.wikipedia.org/w/index.php"
    req = requests.Request("GET", base, params={"title": title, "oldid": revid} if revid else {"title": title})
    return req.prepare().url or base


def diff_url(lang: str, revid: int) -> str:
    return f"https://{lang}.wikipedia.org/w/index.php?diff=prev&oldid={revid}"


class WikiClient:
    def __init__(self, proxy: str = "", cache_dir: Path | None = HTML_CACHE_DIR, timeout: float = 30.0):
        self.timeout = timeout
        self.cache_dir = cache_dir
        self._local = threading.local()
        self._proxy = proxy

    @property
    def session(self) -> requests.Session:
        # requests.Session is not guaranteed thread-safe; give each worker thread its own.
        s = getattr(self._local, "session", None)
        if s is None:
            s = requests.Session()
            s.headers["User-Agent"] = USER_AGENT
            retry = Retry(total=4, backoff_factor=1.0, status_forcelist=(429, 500, 502, 503, 504),
                          allowed_methods=("GET",), respect_retry_after_header=True)
            s.mount("https://", HTTPAdapter(max_retries=retry))
            if self._proxy:
                s.proxies = {"http": self._proxy, "https": self._proxy}
            self._local.session = s
        return s

    # ------------------------------------------------------------------ low level
    def _get(self, url: str, params: dict) -> requests.Response:
        try:
            r = self.session.get(url, params=params, timeout=self.timeout)
        except requests.RequestException as e:
            raise WikiError(f"无法连接维基百科，请检查网络或代理设置。\nCould not reach Wikipedia "
                            f"({e.__class__.__name__}); check the network connection or proxy setting.") from e
        if r.status_code >= 400:
            raise WikiError(f"Wikipedia returned HTTP {r.status_code} for {r.url}")
        return r

    def api(self, lang: str, **params) -> dict:
        lang = check_lang(lang)
        params = {"format": "json", "formatversion": "2", **params}
        data = self._get(f"https://{lang}.wikipedia.org/w/api.php", params).json()
        if "error" in data:
            raise WikiError(data["error"].get("info", "Unknown API error"))
        return data

    # ------------------------------------------------------------------ pages
    def search(self, lang: str, query: str, limit: int = 10) -> list[str]:
        query = (query or "").strip()
        if not query:
            return []
        data = self.api(lang, action="opensearch", search=query, limit=limit, namespace=0, formatversion="1")
        return list(data[1]) if isinstance(data, list) else []

    def page_info(self, lang: str, title: str) -> PageInfo:
        data = self.api(lang, action="query", prop="info|langlinks|pageprops", titles=title,
                        redirects=1, lllimit="max", llprop="autonym", ppprop="wikibase_item")
        pages = data.get("query", {}).get("pages", [])
        if not pages or pages[0].get("missing") or pages[0].get("invalid"):
            raise WikiError(f"No article titled {title!r} on {lang}.wikipedia.org")
        p = pages[0]
        links = [{"lang": l["lang"], "title": l["title"], "autonym": l.get("autonym", "")}
                 for l in p.get("langlinks", [])]
        return PageInfo(lang=lang, title=p["title"], pageid=p["pageid"], lastrevid=p.get("lastrevid", 0),
                        length=p.get("length", 0), qid=p.get("pageprops", {}).get("wikibase_item", ""),
                        langlinks=links)

    # ------------------------------------------------------------------ revisions
    _RVPROP = "ids|timestamp|user|comment|size|tags|flags"

    def revisions(self, lang: str, title: str, *, limit: int = 50, start: str | None = None,
                  newer: bool = False, cont: str | None = None) -> tuple[list[Revision], str | None]:
        """One page of the revision history. Newest first unless ``newer``."""
        params = dict(action="query", prop="revisions", titles=title, redirects=1, rvprop=self._RVPROP,
                      rvlimit=min(limit, 500), rvdir="newer" if newer else "older")
        if start:
            params["rvstart"] = start
        if cont:
            params["rvcontinue"] = cont
        data = self.api(lang, **params)
        pages = data.get("query", {}).get("pages", [])
        if not pages or pages[0].get("missing"):
            raise WikiError(f"No article titled {title!r} on {lang}.wikipedia.org")
        revs = [Revision.from_api(r) for r in pages[0].get("revisions", [])]
        return revs, data.get("continue", {}).get("rvcontinue")

    def iter_revisions(self, lang: str, title: str, *, until_revid: int | None = None,
                       progress: Callable[[int], None] | None = None) -> Iterator[Revision]:
        """All revisions oldest first, stopping after ``until_revid`` when given."""
        cont = None
        seen = 0
        while True:
            revs, cont = self.revisions(lang, title, limit=500, newer=True, cont=cont)
            for r in revs:
                yield r
                seen += 1
                if until_revid is not None and r.revid == until_revid:
                    return
            if progress:
                progress(seen)
            if not cont:
                return

    def revision_at(self, lang: str, title: str, when: str) -> Revision:
        """The revision that was current at ``when`` (ISO date or timestamp)."""
        ts = normalize_timestamp(when)
        revs, _ = self.revisions(lang, title, limit=1, start=ts)
        if not revs:
            raise WikiError(f"{title!r} on {lang}.wikipedia.org did not exist yet at {ts}")
        return revs[0]

    def revision_by_id(self, lang: str, revid: int) -> tuple[str, Revision]:
        data = self.api(lang, action="query", prop="revisions", revids=revid, rvprop=self._RVPROP)
        pages = data.get("query", {}).get("pages", [])
        if not pages or not pages[0].get("revisions"):
            raise WikiError(f"Revision {revid} not found on {lang}.wikipedia.org")
        return pages[0]["title"], Revision.from_api(pages[0]["revisions"][0])

    # ------------------------------------------------------------------ content
    def fetch_html(self, lang: str, revid: int, variant: str | None = None) -> str:
        """Rendered article HTML of one revision, converted to ``variant`` if given."""
        lang = check_lang(lang)
        if variant and variant not in VARIANTS.get(lang, []):
            variant = None
        cache_file = None
        if self.cache_dir is not None:
            cache_file = self.cache_dir / lang / f"{int(revid)}-{variant or 'orig'}.html.gz"
            if cache_file.exists():
                return gzip.decompress(cache_file.read_bytes()).decode("utf-8")
        params = {"oldid": int(revid), "action": "render"}
        if variant:
            params["variant"] = variant
        html = self._get(f"https://{lang}.wikipedia.org/w/index.php", params).text
        if cache_file is not None:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            tmp = cache_file.with_suffix(".tmp")
            tmp.write_bytes(gzip.compress(html.encode("utf-8")))
            tmp.replace(cache_file)
        return html


def normalize_timestamp(when: str) -> str:
    """Accept 2015-03-01, 2015-03-01 12:00 or a full ISO timestamp; return MediaWiki UTC form."""
    when = (when or "").strip().replace(" ", "T")
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2})(?::(\d{2}))?)?Z?$", when)
    if not m:
        raise WikiError(f"Unrecognised date {when!r}; use YYYY-MM-DD")
    y, mo, d, h, mi, s = m.groups()
    if h is None:
        h, mi, s = "23", "59", "59"  # a bare date means "as of the end of that day"
    return f"{y}-{mo}-{d}T{h}:{mi}:{s or '00'}Z"


def cache_size_bytes(cache_dir: Path = HTML_CACHE_DIR) -> int:
    if not cache_dir.exists():
        return 0
    return sum(p.stat().st_size for p in cache_dir.rglob("*") if p.is_file())
