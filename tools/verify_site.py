#!/usr/bin/env python3
"""Validate generated internal links, assets, fragments, and duplicate IDs."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://spork.sh"


@dataclass(frozen=True)
class Reference:
    attribute: str
    value: str
    line: int


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: dict[str, int] = {}
        self.references: list[Reference] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        line, _ = self.getpos()
        for name, value in attrs:
            if value is None:
                continue
            if name == "id":
                if value in self.ids:
                    raise ValueError(
                        f"duplicate HTML id {value!r} at lines {self.ids[value]} and {line}"
                    )
                self.ids[value] = line
            elif name in {"action", "href", "src"}:
                self.references.append(Reference(name, value, line))


@dataclass(frozen=True)
class GeneratedDocument:
    path: Path
    route: str
    parser: DocumentParser


def route_for(path: Path, public: Path) -> str:
    relative = path.relative_to(public).as_posix()
    if relative == "index.html":
        return "/"
    if relative.endswith("/index.html"):
        return f"/{relative[:-len('index.html')]}"
    return f"/{relative}"


def output_for(route: str, public: Path) -> Path:
    if route == "/":
        return public / "index.html"
    if route.endswith("/"):
        return public / route.removeprefix("/") / "index.html"
    return public / route.removeprefix("/")


def load_documents(public: Path) -> dict[str, GeneratedDocument]:
    documents: dict[str, GeneratedDocument] = {}
    for path in sorted(public.rglob("*.html")):
        parser = DocumentParser()
        try:
            parser.feed(path.read_text(encoding="utf-8"))
        except ValueError as error:
            raise ValueError(f"{path.relative_to(public)}: {error}") from error
        route = route_for(path, public)
        documents[route] = GeneratedDocument(path, route, parser)
    return documents


def internal_target(source: GeneratedDocument, reference: Reference) -> tuple[str, str] | None:
    parsed = urlsplit(reference.value)
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return None
    if parsed.netloc and parsed.netloc != "spork.sh":
        return None
    absolute = urlsplit(urljoin(f"{SITE_URL}{source.route}", reference.value))
    if absolute.netloc != "spork.sh":
        return None
    return unquote(absolute.path or source.route), unquote(absolute.fragment)


def validate(public: Path) -> tuple[int, int]:
    documents = load_documents(public)
    checked = 0
    for source in documents.values():
        for reference in source.parser.references:
            target = internal_target(source, reference)
            if target is None:
                continue
            route, fragment = target
            output = output_for(route, public)
            if not output.is_file():
                alternate = output_for(f"{route}/", public) if not route.endswith("/") else None
                hint = f"; canonical route is {route}/" if alternate and alternate.is_file() else ""
                raise ValueError(
                    f"{source.path.relative_to(public)}:{reference.line}: "
                    f"broken {reference.attribute}={reference.value!r}{hint}"
                )
            if fragment:
                target_document = documents.get(route)
                if target_document is None:
                    raise ValueError(
                        f"{source.path.relative_to(public)}:{reference.line}: "
                        f"fragment targets non-HTML route {route!r}"
                    )
                if fragment not in target_document.parser.ids and fragment != "main-content":
                    raise ValueError(
                        f"{source.path.relative_to(public)}:{reference.line}: "
                        f"missing fragment #{fragment} at {route}"
                    )
            checked += 1
    return len(documents), checked


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("public", nargs="?", type=Path, default=ROOT / "public")
    args = parser.parse_args()
    public = args.public.resolve()
    if not public.is_dir():
        raise SystemExit(f"site output does not exist: {public}")
    documents, references = validate(public)
    print(f"generated site verified: {documents} HTML documents, {references} internal references")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
