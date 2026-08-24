#!/usr/bin/env python3
"""Generates /llms-full.txt — the single-file expansion of this site.

    python3 admin/build/gen_llms_full.py            # write it
    python3 admin/build/gen_llms_full.py --check    # fail if it has drifted (CI)

The sibling sites publish llms.txt and stop there. A reader that wants the whole
argument then has to fetch twenty pages and hope it found them all. This file is the
alternative: the index, the front page in full, and every source document, in one
fetch, with each section labelled by where it came from.

It is GENERATED rather than written for the same reason every other page here is: a
hand-maintained 50,000-word twin of a site is a stale artefact with a longer fuse. It
is assembled from llms.txt, index.md and briefs/*.md — all of which are themselves the
source of truth for something — so it cannot say anything the site does not.
"""
import sys
from pathlib import Path

from pagelib import ROOT, HOST

VERSION = (ROOT / "admin/build/version.txt").read_text().strip()
OUT = ROOT / "llms-full.txt"

HEADER = f"""# sg-compute.sgit.ai — full text

Site version: {VERSION}. Every page and every source document of https://{HOST}/ in one
file, so an agent can read the whole argument in a single fetch.

GENERATED — assembled by admin/build/gen_llms_full.py from llms.txt, index.md and
briefs/*.md, and re-checked in CI. It cannot say anything the site does not.

Structure of this file:
  PART 1  the index (llms.txt), for orientation and the stable-URL promises
  PART 2  the front page in full (index.md)
  PART 3  the {{n}} source documents this site was written from, verbatim

Editorial policy, which applies to all three parts: CODE WINS. Where the platform's
README, capabilities.json, reality document and tree disagree, the tree is right. Every
number was measured from the tree on 24 August 2026 at repo version v0.2.71, or carries
its own date. Two of the documents in PART 3 are published redacted, under their own
rule — they are the redaction list, so they named every live address the site was told
to strip; each address was replaced by the shape it is an instance of.

All content CC BY 4.0 — Dinis Cruz, with AI co-authorship (Claude, Anthropic). The
platform's own source code is Apache-2.0.

"""

RULE = "\n\n" + "=" * 78 + "\n"


def build():
    briefs = sorted((ROOT / "briefs").glob("*.md"))
    parts = [HEADER.replace("{n}", str(len(briefs)))]

    parts.append(RULE + "PART 1 — THE INDEX (source: /llms.txt)" + RULE + "\n")
    parts.append((ROOT / "llms.txt").read_text().strip())

    parts.append(RULE + "PART 2 — THE FRONT PAGE (source: /index.md)" + RULE + "\n")
    parts.append((ROOT / "index.md").read_text().strip())

    parts.append(RULE + f"PART 3 — THE {len(briefs)} SOURCE DOCUMENTS" + RULE + "\n")
    parts.append("Each is also fetchable on its own at /briefs/<filename>.\n")
    for b in briefs:
        parts.append(RULE + f"source: /briefs/{b.name}" + RULE + "\n")
        parts.append(b.read_text().strip())

    return "\n".join(parts).rstrip() + "\n"


def main():
    content = build()
    if "--check" in sys.argv:
        if not OUT.exists():
            print("gen_llms_full --check: llms-full.txt is missing", file=sys.stderr)
            sys.exit(1)
        if OUT.read_text() != content:
            print("gen_llms_full --check: llms-full.txt is out of date — re-run the generator",
                  file=sys.stderr)
            sys.exit(1)
        print(f"gen_llms_full --check: OK — {len(content.split()):,} words, in sync")
        return
    OUT.write_text(content)
    print(f"gen_llms_full: wrote llms-full.txt — {len(content.split()):,} words, "
          f"{len(content):,} bytes")


if __name__ == "__main__":
    main()
