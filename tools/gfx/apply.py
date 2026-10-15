"""Insert the English graphics: every gfx/en/<bank>_<idx>.png (4bpp index sheet in res.py layout) is converted
back to resource bytes, recompressed chunk by chunk (mmcomp, flag 0) into free space, and the bank record's
pointer (u32 at bank + 5*idx) is repointed. Called by tools/build.py: apply(rom, alloc).
"""
import glob, os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import banks, mmcomp, res  # noqa: E402

EN = os.path.join(ROOT, "gfx", "en")


def load_sheet(path):
    im = Image.open(path)
    if im.mode != "P":
        raise ValueError(f"{path}: must be an indexed (P) PNG")
    a = np.array(im)
    if a.max() > 15:
        raise ValueError(f"{path}: index > 15")
    return a


def encode_res(data, info):
    """-> (compressed bytes, offset of each chunk inside them)"""
    csz = banks.chunk_size(info)
    n = (info >> 4) + 1
    assert len(data) == n * csz
    # info&4 chunks get a load-time add on nonzero literals; raw (add 0) data recompresses consistently
    out, starts = bytearray(), []
    for c in range(n):
        starts.append(len(out))
        out += _compress_cached(data[c * csz:(c + 1) * csz])
    return bytes(out), starts


def chunk_starts(rom, off, info):
    starts = []
    for _ in range((info >> 4) + 1):
        starts.append(off)
        _, off = banks.mmcomp.decompress(rom, off, banks.chunk_size(info))
    return starts


def _compress_cached(chunk):
    # the optimal-parse compressor is slow (~1 s/chunk); cache by content (work/ is scratch)
    import hashlib
    cdir = os.path.join(ROOT, "work", "gfx_cache")
    p = os.path.join(cdir, hashlib.sha1(chunk).hexdigest() + ".bin")
    if os.path.exists(p):
        return open(p, "rb").read()
    z = mmcomp.compress(chunk)
    os.makedirs(cdir, exist_ok=True)
    open(p, "wb").write(z)
    return z


def apply(rom, alloc):
    done = set()
    for path in sorted(glob.glob(os.path.join(EN, "*.png"))):
        name = os.path.basename(path)[:-4]
        bank_s, idx_s = name.split("_")[:2]
        bank, idx = "0x" + bank_s, int(idx_s)
        orig, info = res.decode(rom, bank, idx)
        new = res.from_sheet(load_sheet(path), info, len(orig))
        if new == orig:
            continue
        z, zst = encode_res(new, info)
        assert banks.decode_res(z + b"\0" * 8, 0, info)[0] == new, name
        off = alloc.put(z)
        # repoint this record and every alias record (any bank) that starts at one of its chunks
        # (e.g. #73-#82 are single-plate views into #72's stream, #36/#38 into #35)
        moved = {o: off + z0 for o, z0 in zip(chunk_starts(rom, res.rec(bank, idx)[0], info), zst)}
        for b, recs in res.DIRS.items():
            for i in range(len(recs)):
                slot = int(b, 16) + 5 * i
                p = int.from_bytes(rom[slot:slot + 4], "little") & 0x1FFFFFF
                if p in moved and (b, i) not in done:
                    rom[slot:slot + 4] = (0x08000000 + moved[p]).to_bytes(4, "little")
        done.add((bank, idx))