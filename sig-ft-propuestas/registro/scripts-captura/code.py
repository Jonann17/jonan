import ast,sys,io,tokenize
src=open(sys.argv[1],encoding='utf-8').read()
lines=src.splitlines()
t=ast.parse(src)
skip=set()
for n in ast.walk(t):
    if isinstance(n,(ast.Module,ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and n.body and isinstance(n.body[0],ast.Expr) and isinstance(getattr(n.body[0],'value',None),ast.Constant) and isinstance(n.body[0].value.value,str):
        d=n.body[0]
        for i in range(d.lineno,d.end_lineno+1): skip.add(i)
for i,l in enumerate(lines,1):
    if i in skip: continue
    s=l.strip()
    if s.startswith('#') or not s: continue
    print(f"{i}: {l}")
