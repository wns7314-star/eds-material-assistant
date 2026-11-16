"""Apply only the EDS presentation stylesheet and preserve HTML and JavaScript."""
from pathlib import Path
import argparse
import hashlib
import os
import tempfile

MARKER = "/* EDS Compare Studio — lavender presentation refresh."
CANDIDATES = ("web", "app/web", "EDS_Material_Assistant/web", "EDS_Assistant_Windows/app/web")

def find_web(root):
    root = Path(root).resolve()
    options = ([root] if root.name == "web" else []) + [root / p for p in CANDIDATES]
    matches = sorted({p.resolve() for p in options if (p / "studio.css").is_file() and
        (p / "index.html").is_file() and (p / "compare.js").is_file()})
    if len(matches) != 1:
        raise ValueError("EDS comparison web folder was not uniquely identified.")
    return matches[0]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def apply_theme(root, css_path):
    web = find_web(root)
    target = web / "studio.css"
    addition = Path(css_path).read_bytes()
    if MARKER.encode("utf-8") not in addition:
        raise ValueError("Invalid theme file.")
    original = target.read_bytes()
    if MARKER.encode("utf-8") in original:
        return {"status": "already_applied", "target": str(target)}
    protected = {p: digest(p) for p in web.rglob("*") if p.is_file() and p.suffix.lower() in {".html", ".js"}}
    backup = target.with_name("studio.css.before_lavender.bak")
    if backup.exists() and backup.read_bytes() != original:
        raise ValueError("A different backup already exists. No changes made.")
    if not backup.exists():
        backup.write_bytes(original)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=web, suffix=".tmp", delete=False) as f:
            temporary = Path(f.name)
            f.write(original + b"\n" + addition)
        os.replace(temporary, target)
        if any(not p.exists() or digest(p) != value for p, value in protected.items()):
            target.write_bytes(original)
            raise RuntimeError("HTML/JavaScript integrity check failed; CSS restored.")
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return {"status": "applied", "target": str(target), "backup": str(backup),
            "unchanged_html_js_files": len(protected), "css_sha256": digest(target)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply EDS CSS only, preserving HTML/JavaScript.")
    parser.add_argument("program_folder", nargs="?", default=".")
    args = parser.parse_args()
    result = apply_theme(args.program_folder, Path(__file__).with_name("lavender-refresh.css"))
    print(result)
