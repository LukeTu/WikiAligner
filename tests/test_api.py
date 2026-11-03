"""End-to-end API tests with a fake Wikipedia and a fake embedding model (no network)."""
import time

import pytest
from fastapi.testclient import TestClient

from wikialigner.history import trace_first_appearance
from wikialigner.jobs import RunStore
from wikialigner.models import ModelManager
from wikialigner.server import create_app
from wikialigner.wiki import PageInfo, Revision, WikiError


def html(*paragraphs):
    return '<div class="mw-parser-output">' + "".join(f"<p>{p}</p>" for p in paragraphs) + "</div>"


class FakeWiki:
    """Three revisions of an English article and one of its Russian counterpart."""

    REVS = {
        ("en", 1): ("2015-02-28T10:00:00Z", html("c1 Nemtsov was killed in Moscow.")),
        ("en", 2): ("2015-03-01T10:00:00Z", html("c1 Nemtsov was killed in Moscow.", "c2 Thousands marched in his memory.")),
        ("en", 3): ("2015-03-05T10:00:00Z", html("c1 Nemtsov was killed in Moscow.", "c2 Thousands marched in his memory.",
                                                "c3 Two suspects were arrested.")),
        ("ru", 10): ("2015-02-28T12:00:00Z", html("c1 Немцов был убит в Москве.", "c3 Задержаны двое подозреваемых.")),
    }

    def page_info(self, lang, title):
        last = max(r for (l, r) in self.REVS if l == lang)
        return PageInfo(lang, title, 1, last, 100, "Q1", [{"lang": "ru" if lang == "en" else "en", "title": "X", "autonym": ""}])

    def _rev(self, lang, revid):
        ts, _ = self.REVS[(lang, revid)]
        return Revision(revid=revid, timestamp=ts, user="Editor", parentid=revid - 1)

    def revision_by_id(self, lang, revid):
        if (lang, revid) not in self.REVS:
            raise WikiError("missing")
        return "Article", self._rev(lang, revid)

    def revision_at(self, lang, title, when):
        cands = [r for (l, r), (ts, _) in self.REVS.items() if l == lang and ts <= when + "T23:59:59Z"[len(when) - 10:]]
        return self._rev(lang, max(cands))

    def iter_revisions(self, lang, title, until_revid=None, progress=None):
        for (l, r) in sorted(self.REVS):
            if l == lang and (until_revid is None or r <= until_revid):
                yield self._rev(lang, r)

    def fetch_html(self, lang, revid, variant=None):
        return self.REVS[(lang, revid)][1]

    def revisions(self, lang, title, limit=50, start=None, newer=False, cont=None):
        revs = [self._rev(l, r) for (l, r) in sorted(self.REVS, reverse=True) if l == lang]
        return revs, None

    def search(self, lang, q, limit=10):
        return ["Article"]


@pytest.fixture
def client(fake_embedder, tmp_path):
    models = ModelManager()
    models.register(fake_embedder)
    app = create_app(models=models, client=FakeWiki(), runs=RunStore(tmp_path / "runs"))
    return TestClient(app)


def wait(client, job):
    for _ in range(200):
        j = client.get(f"/api/jobs/{job['id']}").json()
        if j["status"] in ("done", "error"):
            return j
        time.sleep(0.02)
    raise AssertionError("job did not finish")


def test_crosslingual_alignment_and_saved_run(client):
    job = client.post("/api/align", json={
        "left": {"type": "wiki", "lang": "en", "title": "Article", "revid": 3},
        "right": {"type": "wiki", "lang": "ru", "title": "Article"},
        "options": {"model": "fake", "min_margin": 0.9},
    }).json()
    done = wait(client, job)
    assert done["status"] == "done", done["error"]
    r = done["result"]
    assert r["mode"] == "crosslingual"
    assert {(p["src"], p["tgt"]) for p in r["pairs"]} == {(0, 0), (2, 1)}
    assert [u["id"] for u in r["unmatched_src"]] == [1]
    runs = client.get("/api/runs").json()["runs"]
    assert runs[0]["id"] == r["id"]
    assert client.get(f"/api/runs/{r['id']}").json()["stats"]["pairs"] == 2


def test_revision_comparison_by_date(client):
    job = client.post("/api/align", json={
        "left": {"type": "wiki", "lang": "en", "title": "Article", "date": "2015-03-01"},
        "right": {"type": "wiki", "lang": "en", "title": "Article"},
        "options": {"model": "fake"},
    }).json()
    r = wait(client, job)["result"]
    assert r["mode"] == "revision"
    assert r["left"]["revision"]["revid"] == 2 and r["right"]["revision"]["revid"] == 3
    assert r["stats"]["identical"] == 2
    assert [u["id"] for u in r["unmatched_tgt"]] == [2]  # the sentence added in revision 3


def test_text_source(client):
    job = client.post("/api/align", json={
        "left": {"type": "text", "lang": "en", "text": "c1 First line\n\nc2 Second line", "name": "a.txt"},
        "right": {"type": "text", "lang": "de", "text": "c2 Zweite Zeile. c1 Erste Zeile."},
        "options": {"model": "fake", "min_margin": 0.9},
    }).json()
    r = wait(client, job)["result"]
    assert {(p["src"], p["tgt"]) for p in r["pairs"]} == {(0, 1), (1, 0)}


def test_failures_are_reported(client):
    job = client.post("/api/align", json={
        "left": {"type": "wiki", "lang": "en", "revid": 99},
        "right": {"type": "wiki", "lang": "ru", "title": "Article"},
        "options": {"model": "fake"},
    }).json()
    done = wait(client, job)
    assert done["status"] == "error" and "missing" in done["error"]
    assert client.post("/api/align", json={"left": {}, "right": {}, "options": {"granularity": "word"}}).status_code == 400


def test_trace_finds_first_revision_with_sentence():
    res = trace_first_appearance(FakeWiki(), "en", "Article", "c2 Thousands marched in his memory.", 3)
    assert res["revision"]["revid"] == 2
    assert res["previous"]["revid"] == 1
    assert not res["is_page_creation"]
    first = trace_first_appearance(FakeWiki(), "en", "Article", "c1 Nemtsov was killed in Moscow.", 3)
    assert first["is_page_creation"]


def test_trace_pair_endpoint_compares_times(client):
    job = client.post("/api/trace_pair", json={
        "left": {"lang": "en", "title": "Article", "revid": 3, "text": "c3 Two suspects were arrested."},
        "right": {"lang": "ru", "title": "Article", "revid": 10, "text": "c3 Задержаны двое подозреваемых."},
    }).json()
    r = wait(client, job)["result"]
    assert r["comparison"]["earlier"] == "right"


def test_export_formats(client, tmp_path):
    client.post("/api/settings", json={"export_dir": str(tmp_path / "out")})
    job = client.post("/api/align", json={
        "left": {"type": "wiki", "lang": "en", "title": "Article"},
        "right": {"type": "wiki", "lang": "ru", "title": "Article"}, "options": {"model": "fake"},
    }).json()
    run_id = wait(client, job)["result"]["id"]
    for fmt in ("xlsx", "csv", "json"):
        path = client.post("/api/export", json={"run_id": run_id, "format": fmt}).json()["path"]
        assert path.endswith("." + fmt)
        assert (tmp_path / "out").joinpath(path.split("/")[-1].split("\\")[-1]).exists()


def test_rejects_foreign_host_header(client):
    assert client.get("/api/health", headers={"Host": "evil.example"}).status_code == 400
