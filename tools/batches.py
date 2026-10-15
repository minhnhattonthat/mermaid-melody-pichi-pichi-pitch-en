"""Translation batches.
    python -X utf8 tools/batches.py boxes                 assign box types in script/text.json (by id range)
    python -X utf8 tools/batches.py split                 write work/tl/<batch>.tsv + build/terms_<batch>.txt
    python -X utf8 tools/batches.py check <batch>         validate work/tl/<batch>.out.tsv (exit 1 on errors)
    python -X utf8 tools/batches.py merge <batch>         check, then copy English into script/text.json
    python -X utf8 tools/batches.py pairs <batch> OUT     reviewer pairs file (JP / EN with context)
Markup in the TSV: newline = " / " ; controls stay as [..] / {@} / {A} tokens and must be copied verbatim.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import font_en  # noqa: E402

SCRIPT = os.path.join(ROOT, "script", "text.json")
TL = os.path.join(ROOT, "work", "tl")
BATCHES = {  # name: (first id, last id) inclusive, by bank offset
    "b01": (0x0000, 0x0B1A - 1),
    "b02": (0x0B1A, 0x0EA2 - 1),
    "b03": (0x0EA2, 0x12C1 - 1),
    "b04": (0x12C1, 0xFFFF),
}
DATA = {"t0A02", "t0A59", "t0AB9", "t03EF", "t0B5C", "t0000", "t0004", "t0025", "t0026", "t0029", "t002C",
        "t0252", "t01D8", "t01FA", "t0253"}


def load():
    return json.load(open(SCRIPT, encoding="utf-8"))


def save(ents):
    with open(SCRIPT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ents, f, ensure_ascii=False, indent=1)


def off(e):
    return int(e["id"][1:], 16)


def boxes():
    ents = load()
    for e in ents:
        o = off(e)
        if e["id"] in DATA:
            e["box"] = "data"
        elif 0x04CE <= o < 0x0A02:
            e["box"] = "credits"
        elif o >= 0x0B1A and e["id"] != "t0B5C":
            e["box"] = "lyric"
        else:
            e["box"] = "fit"
    save(ents)


def to_tsv(s):
    return s.replace("\n", " / ")


def from_tsv(s):
    return s.replace(" / ", "\n")


def has_text(jp):
    return bool(re.sub(r"\[[^\]]*\]|\{@\}|\{[A-Z]\}|\s|　", "", jp))


def items(name):
    lo, hi = BATCHES[name]
    return [e for e in load() if lo <= off(e) <= hi and e["box"] != "data" and has_text(e["jp"])]


def limit(e):
    if e["box"] == "lyric":
        return "168px"
    if e["box"] == "credits":
        return "232px/line"
    return "px/line " + ",".join(str(x) for x in font_en.jp_line_px(e["jp"]))


def split():
    os.makedirs(TL, exist_ok=True)
    gl = open(os.path.join(ROOT, "glossary.md"), encoding="utf-8").read().splitlines()
    rows = [l for l in gl if l.startswith("|") and not l.startswith("|---") and not l.startswith("| JP")]
    for name in BATCHES:
        its = items(name)
        with open(os.path.join(TL, name + ".tsv"), "w", encoding="utf-8", newline="\n") as f:
            for e in its:
                f.write("\t".join([e["id"], e["box"], limit(e), to_tsv(e["jp"])]) + "\n")
        jp_all = "".join(e["jp"] for e in its)
        terms = [r for r in rows if any(k.strip() and k.strip() in jp_all
                                        for k in re.split(r"[/／]", r.split("|")[1]))]
        os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
        open(os.path.join(ROOT, "build", f"terms_{name}.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(terms) + "\n")
        print(name, len(its), "entries,", len(jp_all), "chars,", len(terms), "terms")


CTL = re.compile(r"\[[0-9A-F]{2}(?: [0-9A-F]{2})*(?: @)?\]|\{@\}|\{[A-Z]\}")


def check(name, quiet=False):
    its = {e["id"]: e for e in items(name)}
    p = os.path.join(TL, name + ".out.tsv")
    errs, seen, out = [], set(), {}
    for n, line in enumerate(open(p, encoding="utf-8-sig"), 1):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        if line.count("\t") != 1:
            errs.append(f"line {n}: need exactly one tab"); continue
        i, en = line.split("\t")
        if i not in its:
            errs.append(f"{i}: unknown id"); continue
        if i in seen:
            errs.append(f"{i}: duplicate"); continue
        seen.add(i)
        en = from_tsv(en.replace("\\n", "\n"))
        jp = its[i]["jp"]
        if sorted(CTL.findall(en)) != sorted(CTL.findall(jp)):
            errs.append(f"{i}: control codes differ: jp {CTL.findall(jp)} en {CTL.findall(en)}")
        if re.search(r"[^\x20-\x7e\n♪♥★…é×]", re.sub(CTL, "", en)):
            errs.append(f"{i}: non-ASCII/unencodable: {en!r}")
        if re.search(r"\d(st|nd|rd|th)\b", en) and "[FB" in jp:
            errs.append(f"{i}: ordinal suffix after a printed number")
        e = dict(its[i]); e["en"] = en
        bad = font_en.lint([e])
        if bad:
            errs.append(f"{i}: width/lint ({bad}) - run: python -X utf8 tools/font_en.py \"{to_tsv(en)}\"")
        out[i] = en
    for i in its:
        if i not in seen:
            errs.append(f"{i}: missing")
    for x in errs:
        print(x)
    print("OK" if not errs else f"{len(errs)} errors")
    return out if not errs else None


def merge(name):
    out = check(name)
    if out is None:
        sys.exit(1)
    ents = load()
    for e in ents:
        if e["id"] in out:
            e["en"] = out[e["id"]]
    save(ents)
    print("merged", len(out))


def pairs(name, path):
    ents = [e for e in load()]
    idx = {e["id"]: k for k, e in enumerate(ents)}
    its = items(name)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for e in its:
            k = idx[e["id"]]
            for c in ents[max(0, k - 2):k]:
                f.write(f"   {c['id']} | {to_tsv(c['jp'])} / EN: {to_tsv(c.get('en', ''))}\n")
            f.write(f">> {e['id']} | {to_tsv(e['jp'])}\n   EN: {to_tsv(e.get('en', ''))}\n\n")


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "boxes":
        boxes()
    elif c == "split":
        split()
    elif c == "check":
        sys.exit(0 if check(sys.argv[2]) is not None else 1)
    elif c == "merge":
        merge(sys.argv[2])
    elif c == "pairs":
        pairs(sys.argv[2], sys.argv[3])
