"""Fetch current jackpots and the latest prize table from vietlott.vn into a JSON file.

Usage: python scripts/fetch_vietlott.py [data/vietlott.json] [--push]

Run it from your own machine: vietlott.vn sits behind Cloudflare, which refuses requests from
cloud servers such as GitHub Actions. Standard library only. The file is rewritten only when
the data itself changes; with --push, a change is also committed and pushed so the app picks
it up from the repo.
"""
import argparse
import html
import json
import re
import subprocess
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

    if problems:
        print("Could not parse: " + ", ".join(problems), file=sys.stderr)
    if {k: v for k, v in old.items() if k != "updated"} == data:
        print("No change.")
        return False
    data = {"updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), **data}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for game in GAMES:
        g, d = data[game], data[game].get("draw") or {}
        jackpots = " / ".join(f"{v / 1e9:,.2f} tỷ" for k, v in g.items() if k.startswith("jackpot") and v)
        print(f"{game}: jackpot {jackpots} · kỳ #{d.get('id', '?')} ({d.get('date', '?')})")
    print(f"Updated {out}.")
    return True


def push(out_path):
    repo = Path(__file__).resolve().parent.parent
    path = str(Path(out_path).resolve())
    git = lambda *args: subprocess.run(["git", *args], cwd=repo, check=True)
    git("add", path)
    git("commit", "-m", f"data: update vietlott {datetime.now(timezone.utc):%Y-%m-%dT%H:%MZ}", "--", path)
    git("push")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("out", nargs="?", default=str(Path(__file__).resolve().parent.parent / "data" / "vietlott.json"))
    parser.add_argument("--push", action="store_true", help="commit and push data/vietlott.json if it changed")
    args = parser.parse_args()
    if main(args.out) and args.push:
        push(args.out)
