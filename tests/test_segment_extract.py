from wikialigner.extract import blocks_from_plain_text, extract_blocks
from wikialigner.segment import segment_blocks, split_clauses, split_sentences

HTML = """
<div class="mw-parser-output">
  <table class="infobox"><tr><th>Born</th><td>1959</td></tr></table>
  <p>Boris Nemtsov was a Russian politician.<sup class="reference">[1]</sup> He was shot in 2015.</p>
  <div class="mw-heading mw-heading2"><h2 id="Events">Events</h2><span class="mw-editsection">[edit]</span></div>
  <figure><img src="x.jpg"><figcaption>The bridge where he was shot</figcaption></figure>
  <ul><li>First item without a full stop<ul><li>Nested item</li></ul></li></ul>
  <div class="mw-heading mw-heading2"><h2 id="References">References</h2></div>
  <ol class="references"><li>Some source</li></ol>
  <ul><li>Link list in the appendix</li></ul>
</div>
"""


def test_extract_keeps_structure_and_drops_apparatus():
    blocks = extract_blocks(HTML)
    kinds = [(b.kind, b.text) for b in blocks]
    assert ("paragraph", "Boris Nemtsov was a Russian politician. He was shot in 2015.") in kinds
    assert ("heading", "Events") in kinds
    assert ("caption", "The bridge where he was shot") in kinds
    assert ("list", "First item without a full stop") in kinds
    assert ("list", "Nested item") in kinds
    assert not any("[1]" in t or "[edit]" in t for _, t in kinds)
    assert not any("appendix" in t or "Some source" in t for _, t in kinds)
    assert not any(b.kind == "infobox" for b in blocks)
    assert blocks[-1].section == "Events"


def test_extract_optional_infobox():
    blocks = extract_blocks(HTML, include_infobox=True)
    assert any(b.kind == "infobox" and b.text == "Born | 1959" for b in blocks)


def test_chinese_keeps_last_sentence_without_punctuation():
    # The first version dropped the final segment when it had no closing punctuation.
    assert split_sentences("他创办了苹果公司。皮克斯动画工作室", "zh") == ["他创办了苹果公司。", "皮克斯动画工作室"]


def test_chinese_closing_quote_stays_with_sentence():
    assert split_sentences("他说：“我们要改变世界。”然后离开了。", "zh") == ["他说：“我们要改变世界。”", "然后离开了。"]


def test_japanese_and_thai_are_split():
    assert len(split_sentences("東京は日本の首都である。人口は約1400万人である。", "ja")) == 2
    assert len(split_sentences("กรุงเทพมหานครเป็นเมืองหลวงของประเทศไทย มีประชากรประมาณสิบล้านคน", "th")) == 2


def test_english_quote_is_not_split_inside():
    s = split_sentences('"He tried a vegan diet. He was also influenced," Dr. Smith said. It ended.', "en")
    assert s == ['"He tried a vegan diet. He was also influenced," Dr. Smith said.', "It ended."]


def test_related_language_uses_closest_rules():
    assert split_sentences("O Sr. Silva chegou. Ele disse olá.", "pt") == ["O Sr. Silva chegou.", "Ele disse olá."]


def test_clauses_merge_short_pieces():
    parts = split_clauses("He was shot near the Kremlin, walking with his girlfriend, at night; four shots were fired.", "en")
    assert parts[0].startswith("He was shot near the Kremlin,")
    assert all(len(p) >= 20 for p in parts)
    assert split_clauses("涅姆佐夫遭枪击身亡，当时他正与女友同行；凶手开了四枪。", "zh") == [
        "涅姆佐夫遭枪击身亡，", "当时他正与女友同行；", "凶手开了四枪。"]


def test_segments_mark_headings_and_trivial_text_unalignable():
    blocks = extract_blocks(HTML)
    segs = segment_blocks(blocks, "en")
    heading = next(s for s in segs if s.kind == "heading")
    assert not heading.alignable
    assert [s.id for s in segs] == list(range(len(segs)))
    trivial = segment_blocks(blocks_from_plain_text("1990\n\nA real sentence here."), "en")
    assert [s.alignable for s in trivial] == [False, True]


def test_paragraph_granularity_keeps_blocks_whole():
    segs = segment_blocks(blocks_from_plain_text("One. Two. Three.\n\nFour."), "en", "paragraph")
    assert [s.text for s in segs] == ["One. Two. Three.", "Four."]
