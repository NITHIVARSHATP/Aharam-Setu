from pathlib import Path
root = Path(r"C:/Users/NITHISHVARAN T P/OneDrive/Pictures/Screenshots/filez/sem 6/innov/repo/Aharam-Setu")
cands = list(root.glob("*Pattinathil-Pasi.pdf"))
if not cands:
    raise SystemExit("PDF_NOT_FOUND")
pdf = cands[0]
from pypdf import PdfReader
r = PdfReader(str(pdf))
txt = "\n".join([(p.extract_text() or "") for p in r.pages])
out = root / "Pattinathil-Pasi.extracted.txt"
out.write_text(txt, encoding='utf-8')
print('OK', len(r.pages), len(txt), out)
