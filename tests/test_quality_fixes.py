from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_scripts_expose_help_when_run_directly() -> None:
    for script_name in ["dashboard.py", "ocr_text_extraction.py", "extract_invoice_fields.py"]:
        completed = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / script_name), "--help"],
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )

        assert completed.returncode == 0
        assert "usage:" in completed.stdout.lower()


def test_active_safety_config_files_exist() -> None:
    assert (PROJECT_ROOT / ".gitignore").exists()
    assert (PROJECT_ROOT / ".env.example").exists()
    gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in gitignore
    assert "data/data_raw/" in gitignore
    assert "data/data_pdf/" in gitignore
    assert "data/data_txt/" in gitignore
    assert "data/data_processed/invoice_structured_fields.csv" in gitignore
    assert "rag/knowledge_base.json" in gitignore
    assert "your-gemini-api-key-here" in (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8")


def test_workflow_graph_is_documented_and_linked() -> None:
    workflow_graph = PROJECT_ROOT / "docs" / "workflow_graph.md"
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    graph_text = workflow_graph.read_text(encoding="utf-8")

    assert workflow_graph.exists()
    assert "docs/workflow_graph.md" in readme
    assert "```mermaid" in graph_text
    assert "data/data_raw/" in graph_text


def test_ocr_config_has_no_machine_specific_tesseract_path() -> None:
    ocr_source = (PROJECT_ROOT / "scripts" / "ocr_text_extraction.py").read_text(encoding="utf-8")

    assert "pedro.carreiro" not in ocr_source
    assert "TESSERACT_CMD" in ocr_source
    assert "\nconfigure_local_ocr_environment()\n" not in ocr_source


def test_dashboard_helpers_are_importable_and_keep_pdf_paths_inside_pdf_dir() -> None:
    from scripts.dashboard import DEFAULT_PDF_DIR, safe_filename, source_pdf_name, source_pdf_path

    assert safe_filename(r"..\private\invoice?.pdf") == "invoice.pdf"

    row = {"source_file": r"..\outside\secret.pdf", "ocr_text_file": "null"}
    assert source_pdf_name(row) == "secret.pdf"
    assert source_pdf_path(row) == DEFAULT_PDF_DIR / "secret.pdf"
