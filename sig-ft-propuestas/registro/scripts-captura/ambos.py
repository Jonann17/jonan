import re, sys, pathlib
for f in sys.argv[1:]:
    p = pathlib.Path(f); s = p.read_text()
    s = re.sub(r"<<<<<<< [^\n]*\n(.*?)=======\n(.*?)>>>>>>> [^\n]*\n", lambda m: m.group(1)+m.group(2), s, flags=re.S)
    p.write_text(s)
