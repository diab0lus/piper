"""Compare the version displayed in a standalone Piper file with its public tag."""

import sys
from html.parser import HTMLParser
from pathlib import Path


class VersionLabels(HTMLParser):
    def __init__(self):
        super().__init__()
        self.labels = []
        self.in_label = False

    def handle_starttag(self, tag, attrs):
        if self.in_label:
            raise SystemExit("The version label must contain plain text.")
        classes = dict(attrs).get("class") or ""
        if tag == "span" and "brand-version" in classes.split():
            self.labels.append("")
            self.in_label = True

    def handle_data(self, data):
        if self.in_label:
            self.labels[-1] += data

    def handle_endtag(self, tag):
        if tag == "span":
            self.in_label = False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: verify-version.py RELEASE_TAG PIPER_HTML")
    tag, filename = sys.argv[1:]
    if not tag.startswith("v") or len(tag) == 1:
        raise SystemExit(f"Expected a public release tag beginning with v, got {tag!r}.")
    version = VersionLabels()
    version.feed(Path(filename).read_text(encoding="utf-8"))
    version.close()
    if version.in_label or len(version.labels) != 1:
        raise SystemExit("Expected exactly one complete version label in piper.html.")
    if version.labels[0] != tag:
        raise SystemExit(f"Release tag {tag!r} does not match piper.html version {version.labels[0]!r}.")
    print(f"Verified piper.html for {tag}.")
