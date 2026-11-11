#!/usr/bin/env python3
"""Check the web resources served by an installed APK."""

import argparse
import hashlib
from html.parser import HTMLParser
import json
from urllib.parse import urljoin, urlsplit
from urllib.request import urlopen
import zipfile


class Resources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("src"):
            self.paths.add(attrs["src"])
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.paths.add(attrs["href"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="URL of the installed application's web page")
    parser.add_argument("apk", help="APK used to install the application")
    args = parser.parse_args()
    resources = Resources()
    with urlopen(args.url, timeout=10) as response:
        resources.feed(response.read().decode("utf-8"))
    assert resources.paths, "Page contains no scripts or stylesheets"
    results = []
    with zipfile.ZipFile(args.apk) as apk:
        for path in sorted(resources.paths):
            url = urljoin(args.url, path)
            assert urlsplit(url).netloc == urlsplit(args.url).netloc, "External page resource"
            with urlopen(url, timeout=10) as response:
                data = response.read()
                media_type = response.headers.get_content_type()
            expected = apk.read("assets/" + urlsplit(url).path.lstrip("/"))
            valid_type = media_type == "text/css" if path.endswith(".css") else "javascript" in media_type
            matches = data == expected
            results.append({"path": path, "content_type": media_type, "matches_apk": matches})
            if not valid_type or not matches:
                print(json.dumps({"status": "FAIL", "resources": results}, indent=2))
                return 1
    print(json.dumps({"status": "PASS", "resources": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
