import tempfile
from pathlib import Path
from apply_theme import apply_theme
CSS = Path(__file__).with_name("lavender-refresh.css")
checks = []
with tempfile.TemporaryDirectory() as d:
    root=Path(d)
    web=root/"web"
    web.mkdir()
    (web/"studio.css").write_bytes(b"body { color: black; }\r\n")
    (web/"index.html").write_bytes(b"<!doctype html><title>fixture</title>")
    (web/"compare.js").write_bytes(b"const fixture = true;\r\n")
    original={p.name:p.read_bytes() for p in web.iterdir()}
    first=apply_theme(root,CSS)
    assert first["status"]=="applied"
    checks.append("CSS applied to an independent fixture")
    assert (web/"index.html").read_bytes()==original["index.html"]
    assert (web/"compare.js").read_bytes()==original["compare.js"]
    checks.append("Fixture HTML and JavaScript remain byte-identical")
    assert (web/"studio.css.before_lavender.bak").read_bytes()==original["studio.css"]
    checks.append("Original CSS bytes preserved in backup")
    changed=(web/"studio.css").read_bytes()
    assert apply_theme(root,CSS)["status"]=="already_applied"
    assert (web/"studio.css").read_bytes()==changed
    checks.append("Repeat application makes no duplicate change")
with tempfile.TemporaryDirectory() as d:
    try:
        apply_theme(Path(d),CSS)
        raise AssertionError("Invalid target accepted")
    except ValueError:
        checks.append("Invalid target rejected without writing")
with tempfile.TemporaryDirectory() as d:
    root=Path(d)
    for relative in ("web","app/web"):
        web=root/relative
        web.mkdir(parents=True)
        for name in ("studio.css","index.html","compare.js"):
            (web/name).write_text("fixture",encoding="utf-8")
    try:
        apply_theme(root,CSS)
        raise AssertionError("Ambiguous target accepted")
    except ValueError:
        checks.append("Ambiguous targets rejected without writing")
print("PATCH_FIXTURE_CHECKS", len(checks))
for c in checks:
    print("PASS", c)
