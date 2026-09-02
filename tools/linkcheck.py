# Every internal link on the site resolves to a file that exists.
#
#   python tools/linkcheck.py
#
# A documentation site rots by link, not by page: something is renamed, the page
# that pointed at it keeps rendering fine, and nobody notices until a reader
# does. This is the cheapest guard against that, and it runs in CI.
import io
import os
import re
import sys

SCRIPT = re.compile(r'<script[^>]*>.*?</script>', re.S | re.I)
LINK = re.compile(r'(?:href|src)="([^"]+)"')
EXTERNAL = ('http://', 'https://', 'mailto:', '#', 'data:')

root = '.'
bad = []
checked = 0

for dirpath, dirnames, filenames in os.walk(root):
    if '.git' in dirpath.split(os.sep):
        continue
    for filename in filenames:
        if not filename.endswith('.html'):
            continue
        path = os.path.join(dirpath, filename)
        page = io.open(path, encoding='utf-8', errors='replace').read()

        # Script bodies go first. They hold template literals such as
        # href="${base}/releases", which are code rather than links; counting
        # them makes the check cry wolf every run until nobody trusts it.
        page = SCRIPT.sub('', page)

        for href in LINK.findall(page):
            if href.startswith(EXTERNAL):
                continue
            target = href.split('#')[0].split('?')[0]
            if not target:
                continue
            checked += 1
            if target.startswith('/'):
                candidate = os.path.join(root, target.lstrip('/'))
            else:
                candidate = os.path.join(dirpath, target)
            # A directory URL is served by its index.html.
            if os.path.isdir(candidate):
                candidate = os.path.join(candidate, 'index.html')
            if not os.path.exists(candidate):
                bad.append('%s -> %s' % (path, href))

print('checked %d internal links' % checked)
if bad:
    print('BROKEN (%d):' % len(bad))
    for entry in sorted(set(bad)):
        print('  ' + entry)
    sys.exit(1)
print('all internal links resolve')
