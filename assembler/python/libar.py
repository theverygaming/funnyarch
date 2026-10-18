import re

# reference: https://en.wikipedia.org/w/index.php?title=Ar_(Unix)&oldid=1371159693

def detect_ar_header(b):
    return b[:8] == b"!<arch>\n"

def read_ar(b):
    if not detect_ar_header(b):
        raise Exception("not a valid archive")
    def try_int(s, base):
        try:
            return int(s, base)
        except ValueError:
            return None
    idx = 8
    indexdata = None
    while idx < len(b):
        fname = b[idx:idx+16].decode("ascii").strip(); idx += 16
        fmodts = try_int(b[idx:idx+12].decode("ascii"), 10); idx += 12
        uid = try_int(b[idx:idx+6].decode("ascii"), 10); idx += 6
        gid = try_int(b[idx:idx+6].decode("ascii"), 10); idx += 6
        fmode = try_int(b[idx:idx+8].decode("ascii"), 8); idx += 8
        fsize = int(b[idx:idx+10].decode("ascii"), 10); idx += 10
        if b[idx:idx+2] != b"`\n":
            raise Exception(f"invalid ar file header {b[idx:idx+2]}")
        idx += 2
        fcontent = b[idx:idx+fsize]; idx += fsize
        # alignment
        if (fsize % 2) != 0:
            idx += 1
        # special index file
        if fname == "//":
            indexdata = fcontent
            continue
        # filename index lookup
        if (m := re.match(r"^\/(\d+)$", fname)) is not None:
            if indexdata is None:
                raise Exception("filename that references index appeared in the archive before the index itself")
            fname = indexdata[int(m.group(1)):].split(b"\n")[0].decode("ascii")
        # fixup filename
        fname = fname.removesuffix("/")
        yield (fname, fmodts, uid, gid, fmode, fcontent)
