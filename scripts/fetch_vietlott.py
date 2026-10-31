"""Fetch current jackpots and the latest prize table from vietlott.vn into a JSON file.

Usage: python scripts/fetch_vietlott.py data/vietlott.json

Standard library only, so it runs on a bare GitHub Actions runner. The file is rewritten only
when the data itself changes, so scheduled runs don't create empty commits.
"""
import html
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://vietlott.vn"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
GAMES = {
    "mega645": {"results": "/vi/trung-thuong/ket-qua-trung-thuong/645",
                "jackpots": {"jackpot": r"Jackpot Mega 6/45 ước tính"}},
    "power655": {"results": "/vi/trung-thuong/ket-qua-trung-thuong/655",
                 "jackpots": {"jackpot": r"Jackpot 1 Power 6/55 ước tính",
                              "jackpot2": r"Jackpot 2 Power 6/55 ước tính"}},
}


def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": UA, "Accept-Language": "vi"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read().decode("utf-8", errors="replace")


def text(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def money(s):
    digits = re.sub(r"\D", "", s)
    return int(digits) if digits else None


def parse_jackpot(page, label):
    m = re.search(label + r".*?<h3>\s*([\d.,]+)\s*</h3>", page, re.S)
    return money(m.group(1)) if m else None


def parse_results(page):
    m = re.search(r"Kỳ quay thưởng\s*<b>\s*#?(\d+)\s*</b>\s*ngày\s*<b>\s*(\d{2})/(\d{2})/(\d{4})", page)
    if not m:
        return None
    draw = {"id": m.group(1), "date": f"{m.group(4)}-{m.group(3)}-{m.group(2)}", "prizes": []}
    start = page.find("<table", m.end())
    table = re.sub(r"<!--.*?-->", "", page[start:page.find("</table>", start)], flags=re.S)
    for row in re.findall(r"<tr.*?</tr>", table, re.S):
        cells = [text(c) for c in re.findall(r"<td.*?</td>", row, re.S)]
        if len(cells) >= 4 and money(cells[3]) is not None:
            draw["prizes"].append({"name": cells[0], "winners": money(cells[2]) or 0, "value": money(cells[3])})
    return draw if draw["prizes"] else None


def main(out_path):
    out = Path(out_path)
    old = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
    home = get("/")
    data, problems = {}, []
    for game, cfg in GAMES.items():
        entry = {}
        for key, label in cfg["jackpots"].items():
            value = parse_jackpot(home, label)
            if value is None:
                problems.append(f"{game}.{key}")
            entry[key] = value
        try:
            entry["draw"] = parse_results(get(cfg["results"]))
        except OSError as e:
            entry["draw"] = None
            problems.append(f"{game}.draw ({e})")
        if entry["draw"] is None:
            problems.append(f"{game}.draw")
        # keep the last good value for anything that failed to parse this time
        prev = old.get(game, {})
        data[game] = {k: (v if v is not None else prev.get(k)) for k, v in entry.items()}

    if all(v is None for g in data.values() for v in g.values()):
        sys.exit("Nothing could be parsed from vietlott.vn - the page layout may have changed.")

    if {k: v for k, v in old.items() if k != "updated"} == data:
        print("No change.")
    else:
        data = {"updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), **data}
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Updated {out}.")
    if problems:
        print("Could not parse: " + ", ".join(problems), file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/vietlott.json")
