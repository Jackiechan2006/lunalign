from __future__ import annotations

import csv
import io
import json
from pathlib import Path

from jinja2 import Template
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


HTML_TMPL = Template(
    """
<!doctype html>
<html><head><meta charset="utf-8"/><title>LunaAlign-X Report</title>
<style>
body { font-family: 'Segoe UI', sans-serif; background:#0b0e14; color:#e8eef7; padding:32px; }
h1 { letter-spacing:.12em; color:#f0d9a0; }
.badge { display:inline-block; padding:4px 10px; border:1px solid #f0d9a0; }
table { border-collapse: collapse; width:100%; margin:16px 0; }
td,th { border:1px solid #223; padding:8px; text-align:left; }
.muted { color:#9aa7b8; }
</style></head>
<body>
<h1>LUNAALIGN-X</h1>
<p>Multi-Modal, Sun-Angle and Scale-Invariant Lunar Image Correspondence</p>
<p class="badge">{{ origin_label }}</p>
<h2>1. Problem</h2>
<p>Find reliable correspondences between Chandrayaan-2 OHRC, TMC-2 and IIRS observations despite scale, illumination, geometry and modality differences.</p>
<h2>2. Input data</h2>
<table>
<tr><th></th><th>Reference</th><th>Moving</th></tr>
<tr><td>Sensor</td><td>{{ reference.metadata.sensor }}</td><td>{{ moving.metadata.sensor }}</td></tr>
<tr><td>GSD (m)</td><td>{{ reference.metadata.gsd_m }}</td><td>{{ moving.metadata.gsd_m }}</td></tr>
<tr><td>Sun elevation</td><td>{{ reference.metadata.sun_elevation_deg }}</td><td>{{ moving.metadata.sun_elevation_deg }}</td></tr>
<tr><td>Sun azimuth</td><td>{{ reference.metadata.sun_azimuth_deg }}</td><td>{{ moving.metadata.sun_azimuth_deg }}</td></tr>
<tr><td>Acquisition</td><td>{{ reference.metadata.acquisition }}</td><td>{{ moving.metadata.acquisition }}</td></tr>
</table>
<h2>3. Algorithm transparency</h2>
<ul>
<li>Feature detector: {{ algorithm.feature_detector }}</li>
<li>Descriptor: {{ algorithm.descriptor }}</li>
<li>Matcher: {{ algorithm.matcher }}</li>
<li>Filtering: {{ algorithm.filtering }}</li>
<li>Geometry: {{ algorithm.geometry }} (robust geometric estimation, not ML)</li>
<li>Refinement: {{ algorithm.refinement }}</li>
<li>Dimensionality reduction: {{ algorithm.dimensionality_reduction }}</li>
<li>Deep matcher: {{ algorithm.deep_model }}</li>
</ul>
<h2>4. Correspondence results</h2>
<p>Candidate matches: {{ matching.raw_matches }} · Ratio-test: {{ matching.ratio_test_matches }} · Mutual: {{ matching.mutual_matches }}</p>
<p>Inliers: {{ geometry.inliers }} · Inlier ratio: {{ '%.3f'|format(geometry.inlier_ratio or 0) }} · RMSE: {{ geometry.rmse }} px</p>
<p>Coverage: {{ '%.1f'|format((uniform.coverage or 0)*100) }}%</p>
<h2>5. Quality</h2>
<p>Registration Quality Score: {{ quality.score }} ({{ quality.band }}). {{ quality.disclaimer }}</p>
<p>{{ decision.status }}</p>
<h2>6. DEM / 3D / 4D</h2>
<p>{{ dem.label if dem else 'DEM unavailable. 2D registration continued.' }}</p>
<h2>7. Limitations</h2>
<ul>{% for L in limitations %}<li>{{ L }}</li>{% endfor %}</ul>
</body></html>
"""
)


def write_reports(result: dict, out_dir: str | Path) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "report.json"
    json_path.write_text(json.dumps(result, default=str, indent=2), encoding="utf-8")
    html_path = out / "report.html"
    html_path.write_text(HTML_TMPL.render(**result), encoding="utf-8")
    csv_path = out / "correspondences.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "ref_x", "ref_y", "mov_x", "mov_y", "ncc", "residual", "shift"])
        for c in result.get("correspondences", []):
            w.writerow(
                [
                    c.get("id"),
                    *(c.get("ref") or [None, None]),
                    *(c.get("mov") or [None, None]),
                    c.get("ncc"),
                    c.get("geometric_residual"),
                    c.get("subpixel_shift"),
                ]
            )
    pdf_path = out / "report.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("LunaAlign-X Registration Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph(result.get("origin_label", ""), styles["Normal"]),
        Paragraph(f"Quality score: {result.get('quality', {}).get('score')} ({result.get('quality', {}).get('band')})", styles["Normal"]),
        Paragraph(result.get("decision", {}).get("status", ""), styles["Normal"]),
        Paragraph("This score is not a probability.", styles["Italic"]),
        Spacer(1, 12),
        Paragraph(str(result.get("algorithm", {})), styles["Code"]),
    ]
    doc.build(story)
    return {
        "json": str(json_path.name),
        "html": str(html_path.name),
        "csv": str(csv_path.name),
        "pdf": str(pdf_path.name),
    }
