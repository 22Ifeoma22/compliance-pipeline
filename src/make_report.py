from pathlib import Path
OUT = Path("data/outputs")
html = f"""
<!doctype html>
<html><head><meta charset="utf-8"><title>Compliance KPIs</title>
<style>body{{font-family:Arial;margin:24px}} img{{max-width:600px;display:block;margin:12px 0}}</style>
</head><body>
<h1>Daily Compliance KPIs</h1>
<p><a href="summary_history.csv">summary_history.csv</a></p>
<h2>ISO 27001</h2>
<img src="iso27001_distribution.png" alt="ISO 27001 Distribution"/>
<h2>ISO 27701</h2>
<img src="iso27701_distribution.png" alt="ISO 27701 Distribution"/>
</body></html>
"""
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "index.html").write_text(html, encoding="utf-8")
print("Report written to", OUT / "index.html")
