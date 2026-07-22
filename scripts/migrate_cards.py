#!/usr/bin/env python3
"""Migrate Amulet's canonical bilingual ArcanaCorpus into Astro JSON entries.

The app corpus is read-only. Run `npm run migrate:cards` after changing it,
`npm run validate:content` to validate committed JSON and SVG assets, or
`npm run validate:source` to compare committed output with the optional app checkout.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = Path(os.environ.get("AMULET_APP_ROOT", ROOT.parent / "amulet"))
CORPUS = Path(os.environ.get("AMULET_CORPUS", APP_ROOT / "Resources" / "ArcanaCorpus"))
MAJOR_IMAGES = APP_ROOT / "marketing" / "pinterest-batch-02" / "assets" / "cards"
MINOR_IMAGES = APP_ROOT / "marketing" / "pinterest-batch-05-menores" / "assets" / "cards"
CONTENT = ROOT / "src" / "content" / "cards"
PUBLIC_IMAGES = ROOT / "public" / "assets" / "cards"

MAJORS = {
    0: ("fool", "el-loco", "the-fool"),
    1: ("magician", "el-mago", "the-magician"),
    2: ("high-priestess", "la-sacerdotisa", "the-high-priestess"),
    3: ("empress", "la-emperatriz", "the-empress"),
    4: ("emperor", "el-emperador", "the-emperor"),
    5: ("hierophant", "el-sumo-sacerdote", "the-hierophant"),
    6: ("lovers", "los-enamorados", "the-lovers"),
    7: ("chariot", "el-carro", "the-chariot"),
    8: ("strength", "la-fuerza", "strength"),
    9: ("hermit", "el-ermitano", "the-hermit"),
    10: ("wheel-of-fortune", "la-rueda-de-la-fortuna", "wheel-of-fortune"),
    11: ("justice", "la-justicia", "justice"),
    12: ("hanged-man", "el-colgado", "the-hanged-man"),
    13: ("death", "la-muerte", "death"),
    14: ("temperance", "la-templanza", "temperance"),
    15: ("devil", "el-diablo", "the-devil"),
    16: ("tower", "la-torre", "the-tower"),
    17: ("star", "la-estrella", "the-star"),
    18: ("moon", "la-luna", "the-moon"),
    19: ("sun", "el-sol", "the-sun"),
    20: ("judgement", "el-juicio", "judgement"),
    21: ("world", "el-mundo", "the-world"),
}

SUITS = [
    ("cups", "copas"),
    ("pentacles", "oros"),
    ("swords", "espadas"),
    ("wands", "bastos"),
]

RANKS = {
    1: ("as", "ace"),
    2: ("dos", "two"),
    3: ("tres", "three"),
    4: ("cuatro", "four"),
    5: ("cinco", "five"),
    6: ("seis", "six"),
    7: ("siete", "seven"),
    8: ("ocho", "eight"),
    9: ("nueve", "nine"),
    10: ("diez", "ten"),
    11: ("sota", "page"),
    12: ("caballero", "knight"),
    13: ("reina", "queen"),
    14: ("rey", "king"),
}

KEYS = {"keywords", "image", "reads as", "essay", "work", "love", "self", "not"}


def parse_markdown(path: Path) -> tuple[str, dict[str, dict[str, list[str]]]]:
    if not path.is_file():
        raise ValueError(f"Missing translation source: {path}")
    title = ""
    data: dict[str, dict[str, list[str]]] = {"upright": {}, "reversed": {}}
    orientation: str | None = None
    key: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer
        if orientation and key:
            value = "\n".join(buffer).strip()
            if value:
                data[orientation][key] = [p.strip() for p in re.split(r"\n\s*\n", value) if p.strip()]
        buffer = []

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# ") and not title:
            title = line[2:].split("·")[0].strip()
        elif line.strip() in {"## upright", "## reversed"}:
            flush()
            orientation = line.strip()[3:]
            key = None
        elif line.startswith("### ") and line[4:].strip() in KEYS:
            flush()
            key = line[4:].strip()
        else:
            buffer.append(line)
    flush()

    if not title:
        raise ValueError(f"Missing card title in {path}")
    for required in ("upright", "reversed"):
        if not data[required].get("reads as") or not data[required].get("essay"):
            raise ValueError(f"Missing {required} summary or essay in {path}")
    return title, data


def localized_content(name: str, slug: str, language: str, parsed: dict[str, dict[str, list[str]]]) -> dict:
    upright = parsed["upright"]
    reversed_data = parsed["reversed"]
    summary = upright["reads as"][0]
    if language == "en":
        seo_title = f"{name} Tarot Meaning: Upright and Reversed | AMULET"
    else:
        seo_title = f"{name} en el tarot: significado al derecho e invertido | AMULET"
    seo_description = summary if len(summary) <= 158 else summary[:155].rsplit(" ", 1)[0].rstrip(" ,;:") + "…"
    return {
        "slug": slug,
        "name": name,
        "seoTitle": seo_title,
        "seoDescription": seo_description,
        "summary": summary,
        "imageDescription": upright.get("image", [None])[0],
        "upright": {
            "keywords": upright.get("keywords", []),
            "essay": upright.get("essay", []),
            "work": upright.get("work", []),
            "love": upright.get("love", []),
            "self": upright.get("self", []),
            "note": upright.get("not", []),
        },
        "reversed": {
            "summary": reversed_data["reads as"][0],
            "keywords": reversed_data.get("keywords", []),
            "essay": reversed_data.get("essay", []),
            "work": reversed_data.get("work", []),
            "love": reversed_data.get("love", []),
            "self": reversed_data.get("self", []),
            "note": reversed_data.get("not", []),
        },
    }


def image_for(card_id: str, order: int, suit: str | None, rank: int | None) -> Path:
    if suit is None:
        path = MAJOR_IMAGES / f"{order:02}-{card_id}.svg"
    else:
        assert rank is not None
        rank_en = RANKS[rank][1]
        matches = sorted(MINOR_IMAGES.glob(f"*-{suit}-{rank:02}-{rank_en}.svg"))
        if len(matches) != 1:
            raise ValueError(f"Expected one image for {card_id}; found {len(matches)}")
        path = matches[0]
    if not path.is_file():
        raise ValueError(f"Missing image: {path}")
    return path


def make_cards() -> list[tuple[dict, Path]]:
    cards: list[tuple[dict, Path]] = []
    for number, (source_slug, es_slug, en_slug) in MAJORS.items():
        translations = {}
        for lang, slug in (("en", en_slug), ("es", es_slug)):
            source = CORPUS / f"{number:02}-{source_slug}.{lang}.md"
            name, parsed = parse_markdown(source)
            translations[lang] = localized_content(name, slug, lang, parsed)
        card = {
            "id": en_slug,
            "number": number,
            "order": number,
            "arcana": "major",
            "suit": None,
            "rank": None,
            "image": f"/assets/cards/{en_slug}.svg",
            "imageWidth": 210,
            "imageHeight": 363,
            "relatedCardIds": [],
            "sourceFiles": {"en": f"{number:02}-{source_slug}.en.md", "es": f"{number:02}-{source_slug}.es.md"},
            "translations": translations,
        }
        cards.append((card, image_for(en_slug, number, None, None)))

    order = len(MAJORS)
    for suit_en, suit_es in SUITS:
        for rank, (rank_es, rank_en) in RANKS.items():
            en_slug = f"{rank_en}-of-{suit_en}"
            es_slug = f"{rank_es}-de-{suit_es}"
            translations = {}
            for lang, slug in (("en", en_slug), ("es", es_slug)):
                source = CORPUS / f"{suit_en}-{rank:02}.{lang}.md"
                name, parsed = parse_markdown(source)
                translations[lang] = localized_content(name, slug, lang, parsed)
            card = {
                "id": en_slug,
                "number": rank,
                "order": order,
                "arcana": "minor",
                "suit": suit_en,
                "rank": rank,
                "image": f"/assets/cards/{en_slug}.svg",
                "imageWidth": 210,
                "imageHeight": 363,
                "relatedCardIds": [],
                "sourceFiles": {"en": f"{suit_en}-{rank:02}.en.md", "es": f"{suit_en}-{rank:02}.es.md"},
                "translations": translations,
            }
            cards.append((card, image_for(en_slug, order, suit_en, rank)))
            order += 1
    return cards


def validate(cards: list[tuple[dict, Path]]) -> None:
    ids: set[str] = set()
    slugs = {"en": set(), "es": set()}
    for card, _ in cards:
        if not card["id"] or card["id"] in ids:
            raise ValueError(f"Missing or duplicate card id: {card['id']!r}")
        ids.add(card["id"])
        for lang in ("en", "es"):
            translation = card["translations"].get(lang)
            if not translation:
                raise ValueError(f"Missing {lang} translation for {card['id']}")
            slug = translation["slug"]
            if slug in slugs[lang]:
                raise ValueError(f"Duplicate {lang} slug: {slug}")
            slugs[lang].add(slug)
    for card, _ in cards:
        missing = set(card["relatedCardIds"]) - ids
        if missing:
            raise ValueError(f"Unknown related cards for {card['id']}: {sorted(missing)}")


def serialized(card: dict) -> str:
    return json.dumps(card, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate committed output without writing")
    parser.add_argument("--check-source", action="store_true", help="compare committed output with the app source without writing")
    parser.add_argument("--limit", type=int, help="write only the first N cards for architecture tests")
    args = parser.parse_args()
    try:
        if args.check and args.check_source:
            raise ValueError("Use either --check or --check-source, not both")
        if args.check:
            committed = [(json.loads(path.read_text(encoding="utf-8")), Path()) for path in sorted(CONTENT.glob("*.json"))]
            validate(committed)
            if not committed:
                raise ValueError("No committed card content found")
            for card, _ in committed:
                image = ROOT / "public" / card["image"].lstrip("/")
                if not image.is_file():
                    raise ValueError(f"Missing copied image: {image}")
            print(f"Validated {len(committed)} committed cards and copied images.")
            return 0
        if args.check_source and not CORPUS.is_dir():
            raise ValueError(f"Optional app source checkout not found: {CORPUS}")
        cards = make_cards()
        validate(cards)
        selected = cards[: args.limit] if args.limit else cards
        if args.check_source:
            problems = []
            expected_names = {f"{card['id']}.json" for card, _ in cards}
            actual_names = {path.name for path in CONTENT.glob("*.json")} if CONTENT.is_dir() else set()
            if expected_names != actual_names:
                problems.append(f"content files differ: missing={sorted(expected_names-actual_names)}, extra={sorted(actual_names-expected_names)}")
            for card, _ in cards:
                path = CONTENT / f"{card['id']}.json"
                if not path.is_file() or path.read_text(encoding="utf-8") != serialized(card):
                    problems.append(f"out of sync: {path}")
                image = ROOT / "public" / card["image"].lstrip("/")
                if not image.is_file():
                    problems.append(f"missing copied image: {image}")
            if problems:
                raise ValueError("Generated content is not in sync:\n- " + "\n- ".join(problems))
        else:
            CONTENT.mkdir(parents=True, exist_ok=True)
            PUBLIC_IMAGES.mkdir(parents=True, exist_ok=True)
            for card, image_source in selected:
                (CONTENT / f"{card['id']}.json").write_text(serialized(card), encoding="utf-8")
                shutil.copyfile(image_source, ROOT / "public" / card["image"].lstrip("/"))
        print(f"Validated {len(cards)} cards: {len(cards)} English and {len(cards)} Spanish translations.")
        if args.limit:
            print(f"Architecture pilot wrote {len(selected)} card records.")
        return 0
    except (OSError, ValueError, KeyError, AssertionError) as error:
        print(f"Card migration failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
