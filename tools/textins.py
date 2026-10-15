"""Text bank: dump to script/text.json, re-encode (identity), insert a translation.

Markup (jp and en fields):
  glyph characters (tbl/jp.tbl for jp, tbl/en.tbl for en); "\\n" = FE newline; the trailing FF is implicit
  [F6 05 ..] / [FA 11 04] / [FD 01] ...  control codes as hex bytes, copied verbatim
  [F9 @] / [F8 @] / [FA 08 @]            jump/call to the label of this string marked with {@}
  {@}                                    label: a table id or a jump lands here (keep it in the English)
    python -X utf8 tools/textins.py dump [--force]
    python -X utf8 tools/textins.py lint [--lang en]
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import textcodec as T  # noqa: E402

SCRIPT = os.path.join(ROOT, "script", "text.json")
LIT_BASE = [0x018100, 0x018130, 0x01816C, 0x0181C8, 0x0182E0, 0x018544, 0x01868C, 0x0188EC, 0x018924,
            0x0199A0, 0x019EA8, 0x019F10, 0x019FAC]   # literal-pool words = 0x08D723C0 (text base)


def load_tbl(name):
    m = {}
    for line in open(os.path.join(ROOT, "tbl", name), encoding="utf-8"):
        line = line.rstrip("\n")
        if line and not line.startswith("#"):
            k, v = line.split("=", 1)
            m[int(k, 16)] = v
    return m


# ---------------------------------------------------------------- dump
def _labels(rom):
    """Intra-string label offsets (bank-relative) from the id table and jump operands."""
    labs = set(T.offsets(rom))
    p = T.BASE
    while p < T.TEXT_END:
        for k, v, raw in T.tokens(rom, p):
            if k == "c" and v in (0xF8, 0xF9):
                labs.add(int.from_bytes(raw[1:4], "little"))
            if k == "c" and v == 0xFA and raw[1] == 0x08:
                labs.add(int.from_bytes(raw[2:5], "little"))
            p += len(raw)
    return labs


def segments(rom):
    out, p = [], T.BASE
    while p < T.TEXT_END:
        s = p
        for _, _, raw in T.tokens(rom, p):
            p += len(raw)
        out.append((s - T.BASE, p - T.BASE))
    return out


def decode_markup(rom, s, tbl, labs):
    """Markup for the segment starting at bank offset s (labels at intra offsets, not at 0)."""
    out, p = [], T.BASE + s
    for kind, v, raw in T.tokens(rom, p):
        off = p - T.BASE
        if off != s and off in labs:
            out.append("{@}")
        p += len(raw)
        if kind == "g":
            ch = tbl[v]
            out.append(ch)
        elif v == 0xFF:
            break
        elif v == 0xFE:
            out.append("\n")
        elif v in (0xF8, 0xF9):
            out.append("[%02X @]" % v)
        elif v == 0xFA and raw[1] == 0x08:
            out.append("[FA 08 @]")
        else:
            out.append("[" + " ".join("%02X" % b for b in raw) + "]")
    return "".join(out)


def dump(force=False):
    if os.path.exists(SCRIPT) and not force:
        sys.exit("script/text.json exists; --force would clobber English")
    from build import load_orig
    rom = load_orig()
    tbl = load_tbl("jp.tbl")
    labs = _labels(rom)
    offs = T.offsets(rom)
    seg = segments(rom)
    ents = []
    for s, e in seg:
        ids = [i for i, o in enumerate(offs) if o == s]
        inner = [i for i, o in enumerate(offs) if s < o < e]
        ents.append({"id": "t%04X" % s, "ids": ids, "inner_ids": inner,
                     "jp": decode_markup(rom, s, tbl, labs), "en": "", "notes": ""})
    os.makedirs(os.path.dirname(SCRIPT), exist_ok=True)
    with open(SCRIPT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ents, f, ensure_ascii=False, indent=1)
    print(len(ents), "strings ->", SCRIPT)


# ---------------------------------------------------------------- encode
TOK = re.compile(r"\[([0-9A-F]{2}(?: [0-9A-F]{2})*)(?: (@))?\]|\{@\}|\{[A-Z]\}|\n|.", re.S)


def encode(markup, rev):
    """-> (bytes incl. FF, list of label intra offsets, list of (pos, kind) jump operand slots)."""
    out, labels, jumps = bytearray(), [], []
    for m in TOK.finditer(markup):
        t = m.group(0)
        if t == "{@}":
            labels.append(len(out))
        elif t == "\n":
            out.append(0xFE)
        elif m.group(1):
            bs = bytes.fromhex(m.group(1))
            out += bs
            if m.group(2):
                jumps.append(len(out))
                out += b"\0\0\0"
        else:
            if t not in rev:
                raise ValueError(f"unencodable {t!r} in {markup[:40]!r}")
            c = rev[t]
            out += bytes([c]) if c < 0xF0 else bytes([0xF0 + (c >> 8), c & 0xFF])
    out.append(0xFF)
    return bytes(out), labels, jumps


def apply(rom, lang="en", marker=False, alloc=None):
    """lang None = identity (jp re-encoded in place). Otherwise insert `lang` (falling back to jp)."""
    ents = json.load(open(SCRIPT, encoding="utf-8"))
    orig = bytes(rom[T.BASE:T.TEXT_END])
    offs = T.offsets(rom)
    jp_rev = {v: k for k, v in load_tbl("jp.tbl").items()}
    if lang:
        import font_en
        en_rev = font_en.reverse_table()
    blob, starts, inner_new = bytearray(), {}, {}
    pending = []
    for e in ents:
        s = int(e["id"][1:], 16)
        if lang and (e.get("en") or marker):
            txt = e["en"] if e.get("en") else f"[{e['id']}] " + font_en.marker_text(e["jp"])
            data, labels, jumps = encode(font_en.fix_controls(txt), en_rev)
        else:
            data, labels, jumps = encode(e["jp"], jp_rev)
        base_new = len(blob)
        starts[s] = base_new
        # map original inner label offsets (in order) to new label positions
        old_inner = sorted(o for o in set(offs) | _jump_targets(orig) if s < o < s + 0x10000 and o < _seg_end(ents, e))
        if len(old_inner) != len(labels):
            raise ValueError(f"{e['id']}: {len(labels)} labels, original has {len(old_inner)}")
        for o, l in zip(old_inner, labels):
            inner_new[o] = base_new + l
        for j in jumps:
            pending.append((base_new + j, s, e))
        blob += data
    def newoff(o):
        return starts[o] if o in starts else inner_new[o]
    # jump operands: original targets in source order
    for (pos, s, e), tgt in zip(pending, _jump_operands(orig)):
        blob[pos:pos + 3] = newoff(tgt).to_bytes(3, "little")
    if lang is None:
        assert len(blob) == len(orig), (len(blob), len(orig))
        rom[T.BASE:T.TEXT_END] = blob
        for i, o in enumerate(offs):
            rom[T.TABLE + 3 * i:T.TABLE + 3 * i + 3] = newoff(o).to_bytes(3, "little")
        return
    at = alloc.put(bytes(blob))
    new_base = 0x08000000 + at
    for lit in LIT_BASE:
        assert int.from_bytes(rom[lit:lit + 4], "little") == 0x08D723C0, hex(lit)
        rom[lit:lit + 4] = new_base.to_bytes(4, "little")
    for i, o in enumerate(offs):
        rom[T.TABLE + 3 * i:T.TABLE + 3 * i + 3] = newoff(o).to_bytes(3, "little")
    font_en.install(rom, alloc)


_cache = {}


def _jump_targets(orig):
    return set(t for t in _jump_operands(orig))


def _jump_operands(orig):
    if "jo" in _cache:
        return _cache["jo"]
    res, p = [], 0
    while p < len(orig):
        for k, v, raw in T.tokens(orig, p):
            if k == "c" and v in (0xF8, 0xF9):
                res.append(int.from_bytes(raw[1:4], "little"))
            if k == "c" and v == 0xFA and raw[1] == 0x08:
                res.append(int.from_bytes(raw[2:5], "little"))
            p += len(raw)
    _cache["jo"] = res
    return res


def _seg_end(ents, e):
    i = ents.index(e)
    return int(ents[i + 1]["id"][1:], 16) if i + 1 < len(ents) else T.TEXT_END - T.BASE


# ---------------------------------------------------------------- lint
def lint(lang="en"):
    ents = json.load(open(SCRIPT, encoding="utf-8"))
    errs = 0
    jp_rev = {v: k for k, v in load_tbl("jp.tbl").items()}
    for e in ents:
        try:
            encode(e["jp"], jp_rev)
        except ValueError as x:
            print("jp", e["id"], x); errs += 1
    try:
        import font_en
    except ImportError:
        print("lint: no font_en yet; checked jp only")
        return 1 if errs else 0
    errs += font_en.lint(ents)
    for e in ents:  # untranslated glyph text would print as English-font garbage
        if not e.get("en") and re.sub(r"\[[^\]]*\]|\{@\}|\{[A-Z]\}|\s|　", "", e["jp"]):
            print(e["id"], "has text but no English"); errs += 1
    print("lint errors:", errs)
    return 1 if errs else 0


if __name__ == "__main__":
    if sys.argv[1] == "dump":
        dump("--force" in sys.argv)
    elif sys.argv[1] == "lint":
        sys.exit(lint())
