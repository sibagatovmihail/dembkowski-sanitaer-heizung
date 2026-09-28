"""Copy the shared blocks of index.html into the service pages.

index.html is the source for every block marked
    <!-- partial:NAME --> ... <!-- /partial:NAME -->
(sprite, header, contact, footer). Each page keeps the same markers; this script
replaces what is between them, marks the page's own nav link as current and
preselects its topic in the request form.

    python3 tools/sync_partials.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = {
    # file: (nav link href, form option to preselect)
    "heizung.html": ("heizung.html", "Neue Heizung / Heizungstausch"),
    "bad-sanitaer.html": ("bad-sanitaer.html", "Badsanierung / neues Bad"),
    "kundendienst.html": ("kundendienst.html", "Reparatur / Störung"),
}
BLOCK = re.compile(r"<!-- partial:(\w+) -->.*?<!-- /partial:\1 -->", re.S)

src = (ROOT / "index.html").read_text()
blocks = {m.group(1): m.group(0) for m in BLOCK.finditer(src)}

for name, (href, topic) in PAGES.items():
    path = ROOT / name
    page = path.read_text()

    def fill(m):
        key = m.group(1)
        block = blocks[key]
        if key == "header":
            block = block.replace(
                f'<a class="navbar__link" href="{href}">',
                f'<a class="navbar__link is-current" href="{href}" aria-current="page">')
        if key == "contact":
            block = block.replace(f"<option>{topic}</option>", f"<option selected>{topic}</option>")
        return block

    new = BLOCK.sub(fill, page)
    missing = set(blocks) - set(re.findall(r"<!-- partial:(\w+) -->", page))
    path.write_text(new)
    print(f"{name}: synced" + (f" (no marker for: {', '.join(sorted(missing))})" if missing else ""))
