#!/usr/bin/env python3
"""Render the study notes in this repo to print-ready PDFs.

Produces one PDF per Markdown file plus a single combined guide, then verifies
that every line of source text is present in each PDF's text layer.

    python3 tools/md_to_pdf.py              # render everything into pdf/ and verify
    python3 tools/md_to_pdf.py --no-verify  # render only
    python3 tools/md_to_pdf.py --verify-only

Requires Google Chrome (or Chromium) on PATH; Markdown is rendered locally with
markdown-it-py and printed through Chrome's DevTools Protocol.

    pip install markdown-it-py mdit-py-plugins pygments websocket-client pypdf
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = REPO_ROOT / "tools"
OUT_DIR = REPO_ROOT / "pdf"

# Study order: overview first, then the domain files, then the review material.
DOC_ORDER = [
    "README.md",
    "exam_sections.md",
    "1_agents_and_workflows.md",
    "2_applications_and_integration.md",
    "3_claude_code_tools_mcp.md",
    "4_model_selection_prompting_context.md",
    "5_eval_debugging_security.md",
    "study_topic_summaries.md",
    "study_cheat_sheet.md",
    "study_flashcards.md",
    "study_practice_questions.md",
]

COMBINED_NAME = "CCDV-F_complete_study_notes.pdf"
COMBINED_TITLE = "Claude Certified Developer – Foundations (CCDV-F) — Complete Study Notes"

CHROME_CANDIDATES = [
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "chrome",
]


# --------------------------------------------------------------------------- #
# Markdown -> HTML
# --------------------------------------------------------------------------- #


def build_markdown():
    from markdown_it import MarkdownIt
    from mdit_py_plugins.anchors import anchors_plugin
    from mdit_py_plugins.deflist import deflist_plugin
    from mdit_py_plugins.footnote import footnote_plugin
    from mdit_py_plugins.tasklists import tasklists_plugin

    md = (
        MarkdownIt(
            "commonmark",
            {
                # Raw HTML stays escaped, so anything that looks like a tag in the
                # notes (`<span style="color:white">` in the prompt-injection
                # example) prints as visible source text instead of vanishing.
                "html": False,
                # linkify off on purpose: the notes mention filenames such as
                # CLAUDE.md and settings.json in prose, and `.md` is a real TLD,
                # so autolinking turns plain filenames into bogus hyperlinks.
                "linkify": False,
                # No smart quotes/dashes: printed text stays byte-faithful.
                "typographer": False,
                "breaks": False,
                "highlight": highlight_code,
            },
        )
        .enable(["table", "strikethrough"])
        .use(footnote_plugin)
        .use(deflist_plugin)
        .use(tasklists_plugin, enabled=True)
        # GitHub-style heading ids, so the notes' own `#section` links resolve
        # inside the PDF the way they do on GitHub.
        .use(anchors_plugin, max_level=6, slug_func=github_slug, permalink=False)
    )
    install_link_renderer(md)
    return md


def github_slug(heading_text: str) -> str:
    slug = unicodedata.normalize("NFKD", heading_text).lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    return re.sub(r"\s+", "-", slug.strip())


def highlight_code(code: str, lang: str, _attrs: str) -> str:
    """Return a full <pre> block; falls back to plain escaped text."""
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_by_name
    from pygments.util import ClassNotFound

    if lang:
        try:
            lexer = get_lexer_by_name(lang, stripnl=False, ensurenl=False)
        except ClassNotFound:
            lexer = None
        if lexer is not None:
            formatter = HtmlFormatter(nowrap=True, classprefix="hl-")
            inner = highlight(code, lexer, formatter)
            return f'<pre><code class="lang-{escape_attr(lang)}">{inner}</code></pre>'
    return f"<pre><code>{escape_html(code)}</code></pre>"


DOC_LINK_MARKER = "@@DOCLINK@@"


def install_link_renderer(md) -> None:
    """Rewrite links for print (see `resolve_link`) and keep their targets legible."""
    default_open = md.renderer.rules.get("link_open")
    default_close = md.renderer.rules.get("link_close")

    def render_token(tokens, idx, options, env):
        return md.renderer.renderToken(tokens, idx, options, env)

    def link_open(tokens, idx, options, env):
        token = tokens[idx]
        href = token.attrGet("href") or ""
        target, trailer = resolve_link(href, link_label(tokens, idx), env.get("link_mode", "pdf"))
        env.setdefault("_link_stack", []).append((target is not None, trailer))
        if target is None:
            return '<span class="local-ref">'
        token.attrSet("href", target)
        return (default_open or render_token)(tokens, idx, options, env)

    def link_close(tokens, idx, options, env):
        stack = env.get("_link_stack") or []
        was_link, trailer = stack.pop() if stack else (True, None)
        if was_link:
            out = (default_close or render_token)(tokens, idx, options, env)
        else:
            out = "</span>"
        if trailer:
            out += f'<span class="url-print"> ({escape_html(trailer)})</span>'
        return out

    md.renderer.rules["link_open"] = link_open
    md.renderer.rules["link_close"] = link_close


def link_label(tokens, idx: int) -> str:
    """Concatenate the visible text of the link opened at `idx`."""
    depth = 0
    parts: list[str] = []
    for token in tokens[idx + 1 :]:
        if token.type == "link_open":
            depth += 1
        elif token.type == "link_close":
            if depth == 0:
                break
            depth -= 1
        elif token.type in ("text", "code_inline"):
            parts.append(token.content)
    return "".join(parts)


def resolve_link(href: str, label: str, link_mode: str) -> tuple[str | None, str | None]:
    """Decide the printed form of one link.

    Returns (href to use, or None to drop the hyperlink and keep plain text),
    and a parenthesised trailer to print after the label, or None.

    External links keep their href and print the URL, since a printed page can't
    be clicked. Same-document anchors keep working inside the PDF. Links to other
    files in the repo lose their hyperlink: Chrome resolves a relative href
    against the source HTML's own directory and bakes that absolute path into the
    PDF, which would point at a path that only existed while rendering.
    """
    if is_external(href):
        return href, href
    if href.startswith("#"):
        return href, None
    if link_mode == "internal" and href.lower().endswith(".md"):
        return f"{DOC_LINK_MARKER}{slugify(href.rsplit('/', 1)[-1][:-3])}", None
    display = href[:-3] + ".pdf" if href.lower().endswith(".md") else href
    return None, None if label_names_target(label, href, display) else f"see {display}"


def label_names_target(label: str, href: str, display: str) -> bool:
    """True when the link text already tells the reader which file it points at."""
    seen = normalize(label)
    base = href.rsplit("/", 1)[-1]
    return seen in {normalize(href), normalize(display), normalize(base),
                    normalize(base.rsplit(".", 1)[0])}


def is_external(href: str) -> bool:
    return href.startswith(("http://", "https://", "mailto:", "ftp://"))


def escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def escape_attr(text: str) -> str:
    return escape_html(text).replace("'", "&#39;")


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def render_document(md, path: Path, link_mode: str) -> str:
    doc_id = f"doc-{slugify(path.stem)}"
    body = md.render(path.read_text(encoding="utf-8"), {"link_mode": link_mode})
    if link_mode == "internal":
        body = namespace_anchors(body, doc_id)
    body = body.replace(f'href="{DOC_LINK_MARKER}', 'href="#doc-')
    return (
        f'<section class="doc" id="{doc_id}">\n'
        f'<p class="doc-source">{escape_html(path.name)}</p>\n'
        f"{body}\n</section>\n"
    )


def namespace_anchors(body: str, doc_id: str) -> str:
    """Prefix heading ids and same-document links so the combined PDF's anchors
    stay unique when several documents share a heading name."""
    body = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{doc_id}--{m.group(1)}"', body)
    return re.sub(
        r'\bhref="#([^"]+)"', lambda m: f'href="#{doc_id}--{m.group(1)}"', body
    )


def build_page(title: str, sections: str) -> str:
    css = (TOOLS_DIR / "print.css").read_text(encoding="utf-8")
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        f"<title>{escape_html(title)}</title>\n"
        f"<style>\n{css}\n</style>\n</head>\n<body>\n{sections}</body>\n</html>\n"
    )


# --------------------------------------------------------------------------- #
# HTML -> PDF (Chrome DevTools Protocol)
# --------------------------------------------------------------------------- #

FOOTER_TEMPLATE = """
<div style="width:100%;padding:0 12mm;font-family:'Noto Sans',sans-serif;
            font-size:7pt;color:#8a9099;display:flex;justify-content:space-between;">
  <span class="title" style="overflow:hidden;white-space:nowrap;max-width:70%;"></span>
  <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
</div>
"""

PRINT_OPTIONS = {
    "printBackground": True,
    "preferCSSPageSize": False,
    "paperWidth": 8.27,  # A4
    "paperHeight": 11.69,
    "marginTop": 0.5,
    "marginBottom": 0.55,
    "marginLeft": 0.5,
    "marginRight": 0.5,
    "displayHeaderFooter": True,
    "headerTemplate": "<div></div>",
    "footerTemplate": FOOTER_TEMPLATE,
    "transferMode": "ReturnAsBase64",
}


class ChromePrinter:
    """Minimal CDP client: one browser process, one target per document."""

    def __init__(self) -> None:
        self.binary = self._find_chrome()
        self.profile = Path(tempfile.mkdtemp(prefix="md2pdf-chrome-"))
        self.port = self._free_port()
        self.process = None
        self.ws = None
        self._msg_id = 0

    @staticmethod
    def _find_chrome() -> str:
        for name in CHROME_CANDIDATES:
            found = shutil.which(name)
            if found:
                return found
        raise SystemExit(
            "No Chrome/Chromium binary found on PATH (looked for: "
            + ", ".join(CHROME_CANDIDATES)
            + ")"
        )

    @staticmethod
    def _free_port() -> int:
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            return sock.getsockname()[1]

    def __enter__(self) -> "ChromePrinter":
        import websocket

        self.process = subprocess.Popen(
            [
                self.binary,
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--hide-scrollbars",
                "--no-first-run",
                "--no-default-browser-check",
                "--force-device-scale-factor=1",
                "--remote-allow-origins=*",
                "--font-render-hinting=none",
                f"--remote-debugging-port={self.port}",
                f"--user-data-dir={self.profile}",
                "about:blank",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        endpoint = self._wait_for_endpoint()
        self.ws = websocket.create_connection(endpoint, timeout=180, max_size=None)
        return self

    def __exit__(self, *_exc) -> None:
        if self.ws is not None:
            try:
                self.ws.close()
            except Exception:
                pass
        if self.process is not None:
            self.process.terminate()
            try:
                self.process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                self.process.kill()
        shutil.rmtree(self.profile, ignore_errors=True)

    def _wait_for_endpoint(self, timeout: float = 60.0) -> str:
        url = f"http://127.0.0.1:{self.port}/json/version"
        deadline = time.time() + timeout
        last_error = None
        while time.time() < deadline:
            if self.process.poll() is not None:
                raise SystemExit(
                    f"Chrome exited with code {self.process.returncode} before "
                    "the DevTools endpoint came up"
                )
            try:
                with urllib.request.urlopen(url, timeout=2) as response:
                    return json.load(response)["webSocketDebuggerUrl"]
            except (urllib.error.URLError, socket.timeout, KeyError, OSError) as exc:
                last_error = exc
                time.sleep(0.2)
        raise SystemExit(f"Chrome DevTools endpoint never became ready: {last_error}")

    def _send(self, method: str, params: dict | None = None, session_id: str | None = None):
        self._msg_id += 1
        message = {"id": self._msg_id, "method": method, "params": params or {}}
        if session_id:
            message["sessionId"] = session_id
        self.ws.send(json.dumps(message))
        return self._await_result(self._msg_id)

    def _await_result(self, msg_id: int):
        while True:
            payload = json.loads(self.ws.recv())
            if payload.get("id") != msg_id:
                continue  # event or another command's reply
            if "error" in payload:
                raise RuntimeError(f"CDP error: {payload['error']}")
            return payload.get("result", {})

    def _wait_for_event(self, method: str, session_id: str, timeout: float = 180.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            payload = json.loads(self.ws.recv())
            if payload.get("method") == method and payload.get("sessionId") == session_id:
                return payload.get("params", {})
        raise RuntimeError(f"Timed out waiting for {method}")

    def print_to_pdf(self, html_path: Path, out_path: Path, title: str) -> None:
        target = self._send("Target.createTarget", {"url": "about:blank"})
        target_id = target["targetId"]
        session_id = self._send(
            "Target.attachToTarget", {"targetId": target_id, "flatten": True}
        )["sessionId"]
        try:
            self._send("Page.enable", session_id=session_id)
            self._send(
                "Emulation.setEmulatedMedia",
                {"media": "print"},
                session_id=session_id,
            )
            self._send(
                "Page.navigate",
                {"url": html_path.resolve().as_uri()},
                session_id=session_id,
            )
            self._wait_for_event("Page.loadEventFired", session_id)
            self._send(
                "Runtime.evaluate",
                {"expression": "document.fonts.ready.then(() => true)", "awaitPromise": True},
                session_id=session_id,
            )
            options = dict(PRINT_OPTIONS)
            options["footerTemplate"] = FOOTER_TEMPLATE.replace(
                '<span class="title" style="overflow:hidden;white-space:nowrap;max-width:70%;"></span>',
                f'<span style="overflow:hidden;white-space:nowrap;max-width:70%;">{escape_html(title)}</span>',
            )
            result = self._send("Page.printToPDF", options, session_id=session_id)
            out_path.write_bytes(base64.b64decode(result["data"]))
        finally:
            self._send("Target.closeTarget", {"targetId": target_id})


# --------------------------------------------------------------------------- #
# Verification: every source line must exist in the PDF text layer
# --------------------------------------------------------------------------- #

FENCE_RE = re.compile(r"^\s*(```|~~~)")
TABLE_DIVIDER_RE = re.compile(r"^\s*\|?[\s:|-]+\|[\s:|-]*$")
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
# Below this length a matched fragment is treated as coincidence rather than
# evidence that the source text really made it onto the page.
MIN_FRAGMENT = 12


def normalize(text: str) -> str:
    """Reduce text to lowercase alphanumerics.

    Punctuation, whitespace and Markdown syntax are dropped so a source line can
    be matched against the PDF text layer regardless of how the renderer wrapped
    it or which markup characters it consumed.
    """
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text.lower() if ch.isalnum())


def expand_links(text: str) -> str:
    """Mirror what the renderer puts on the page for a Markdown link, so the
    check compares against printed text rather than Markdown source."""

    def repl(match: re.Match) -> str:
        label, href = match.group(1), match.group(2)
        _, trailer = resolve_link(href, label, "pdf")
        return f"{label} {trailer}" if trailer else label

    return LINK_RE.sub(repl, text)


def source_segments(md_text: str) -> list[tuple[int, str]]:
    """Split Markdown into (line number, comparable text) chunks.

    Table rows are split per cell so that a missing cell cannot hide inside a
    long row match.
    """
    segments: list[tuple[int, str]] = []
    in_fence = False
    for lineno, raw in enumerate(md_text.splitlines(), start=1):
        if FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        line = raw.strip()
        if not line:
            continue
        if in_fence:
            segments.append((lineno, line))
            continue
        if TABLE_DIVIDER_RE.match(line) and line.count("-") >= 3:
            continue
        line = expand_links(line)
        if line.startswith("|"):
            for cell in line.strip("|").split("|"):
                if cell.strip():
                    segments.append((lineno, cell.strip()))
            continue
        segments.append((lineno, line))
    return segments


def coverage(needle: str, haystack: str) -> list[int] | None:
    """Greedily cover `needle` with the longest possible slices of `haystack`.

    Returns the fragment lengths used, or None if some part of the needle is
    absent from the haystack. More than one fragment means the text is present
    but interrupted — normally a table cell or paragraph split across a page
    boundary, where the PDF text layer reads other cells in between.
    """
    fragments: list[int] = []
    pos = 0
    while pos < len(needle):
        lo, hi, best = 1, len(needle) - pos, 0
        while lo <= hi:
            mid = (lo + hi) // 2
            if haystack.find(needle[pos : pos + mid]) != -1:
                best, lo = mid, mid + 1
            else:
                hi = mid - 1
        if best == 0:
            return None
        fragments.append(best)
        pos += best
    return fragments


def pdf_text(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def verify(md_paths: list[Path], pdf_path: Path) -> tuple[list[str], int, int]:
    """Check a PDF against its sources.

    Returns (problems, segments checked, segments present but split across a
    page boundary). An empty problem list means every source line is on paper.
    """
    haystack = normalize(pdf_text(pdf_path))
    problems: list[str] = []
    checked = 0
    split = 0
    for md_path in md_paths:
        for lineno, segment in source_segments(md_path.read_text(encoding="utf-8")):
            needle = normalize(segment)
            if not needle:
                continue
            checked += 1
            if needle in haystack:
                continue
            fragments = coverage(needle, haystack)
            preview = segment if len(segment) <= 90 else segment[:87] + "..."
            if fragments is None or min(fragments) < MIN_FRAGMENT:
                problems.append(f"{md_path.name}:{lineno}: missing -> {preview}")
            else:
                split += 1
    return problems, checked, split


def page_count(path: Path) -> int:
    from pypdf import PdfReader

    return len(PdfReader(str(path)).pages)


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #


def discover_docs() -> list[Path]:
    found = sorted(p for p in REPO_ROOT.glob("*.md") if p.is_file())
    ordered = [REPO_ROOT / name for name in DOC_ORDER if (REPO_ROOT / name).exists()]
    extras = [p for p in found if p not in ordered]
    if extras:
        print("Note: rendering files absent from DOC_ORDER: "
              + ", ".join(p.name for p in extras))
    return ordered + extras


def title_for(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-verify", action="store_true", help="skip text verification")
    parser.add_argument("--verify-only", action="store_true", help="verify existing PDFs")
    parser.add_argument("--no-combined", action="store_true", help="skip the combined PDF")
    args = parser.parse_args()

    docs = discover_docs()
    if not docs:
        print("No Markdown files found.")
        return 1
    OUT_DIR.mkdir(exist_ok=True)

    targets: list[tuple[list[Path], Path]] = [
        ([doc], OUT_DIR / f"{doc.stem}.pdf") for doc in docs
    ]
    if not args.no_combined:
        targets.append((docs, OUT_DIR / COMBINED_NAME))

    if not args.verify_only:
        md = build_markdown()
        work_dir = Path(tempfile.mkdtemp(prefix="md2pdf-html-"))
        try:
            with ChromePrinter() as printer:
                for sources, out_path in targets:
                    combined = len(sources) > 1
                    link_mode = "internal" if combined else "pdf"
                    title = COMBINED_TITLE if combined else title_for(sources[0])
                    sections = "".join(
                        render_document(md, src, link_mode) for src in sources
                    )
                    html_path = work_dir / f"{out_path.stem}.html"
                    html_path.write_text(build_page(title, sections), encoding="utf-8")
                    printer.print_to_pdf(html_path, out_path, title)
                    print(
                        f"  rendered {out_path.relative_to(REPO_ROOT)} "
                        f"({page_count(out_path)} pages, "
                        f"{out_path.stat().st_size / 1024:.0f} KB)"
                    )
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    if args.no_verify:
        return 0

    print("Verifying that every source line appears in the PDF text layer...")
    failures = 0
    for sources, out_path in targets:
        if not out_path.exists():
            print(f"  MISSING {out_path.relative_to(REPO_ROOT)}")
            failures += 1
            continue
        problems, checked, split = verify(sources, out_path)
        if problems:
            failures += 1
            print(f"  FAIL {out_path.name}: {len(problems)}/{checked} segments missing")
            for problem in problems[:15]:
                print(f"       {problem}")
            if len(problems) > 15:
                print(f"       ... and {len(problems) - 15} more")
        else:
            note = f" ({split} continue across a page break)" if split else ""
            print(f"  OK   {out_path.name}: {checked} segments verified{note}")
    if failures:
        print(f"{failures} file(s) failed verification.")
        return 1
    print("All PDFs contain every line of their source Markdown.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
