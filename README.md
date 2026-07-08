### Invoice Parser Agent

AI-assisted invoice parser for utility and telecom invoices. The project combines local OCR, deterministic field extraction, provider-specific RAG memory, a Gemini PDF second pass, and a local dashboard for human review.

## Supported Invoices

- Electricity
- Water
- Natural gas
- Telecom

Unsupported documents should be rejected or marked invalid instead of being forced into a supported invoice type.

## Project Structure

```text
.
|-- AGENTS.md
|-- README.md
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- scripts/
|   |-- dashboard.py
|   |-- ocr_text_extraction.py
|   |-- extract_invoice_fields.py
|   |-- second_pass_llm.py
|-- invoice_parser/
|   |-- paths.py
|   |-- schema.py
|   |-- text_utils.py
|-- docs/
|   |-- Comando_Git.txt
|   |-- workflow_graph.md
|-- llm/
|   |-- __init__.py
|   |-- agent/
|   |   |-- models.py
|   |   |-- prompts.py
|   |-- api/
|   |   |-- schemas.py
|-- vector_store/
|   |-- base.py
|   |-- documents.py
|-- rag/
|   |-- adaptive_rag.py
|   |-- knowledge_base.json              (generated/local, when provider memory exists)
|   |-- last_retrieval_context.json      (generated/local, when retrieval is exported)
|-- tests/
|   |-- test_shared_utils.py
|   |-- test_second_pass.py
|-- data/
|   |-- data_raw/
|   |-- data_pdf/
|   |-- data_txt/
|   |-- data_processed/
|       |-- invoice_structured_fields.csv
|       |-- reports/
|       |-- llm_second_pass/
|       |-- vector_store/
```

Folder responsibilities:
- `scripts/`: runnable entry-point scripts for the dashboard, OCR, and deterministic extraction.
- `data/data_raw/`: original uploaded invoices. Do not overwrite these files; keep them out of commits.
- `data/data_pdf/`: canonical/searchable PDFs generated or copied by OCR processing.
- `data/data_txt/`: selected OCR text and diagnostics.
- `data/data_processed/`: structured CSV, reports, and generated outputs.
- `data/data_processed/llm_second_pass/`: Gemini raw TXT and normalized JSON outputs.
- `data/data_processed/vector_store/`: generated FAISS/LlamaIndex provider-memory index.
- `rag/`: provider memory adapter and retrieval utilities.
- `llm/`: typed LLM models, prompt templates, and request/response schemas.
- `vector_store/`: local vector-store builder and provider-memory document conversion.
- `invoice_parser/`: shared schema, paths, and normalization helpers used by the pipeline entry points.
- `docs/`: supporting project notes, including Git command references.

Workflow visualization:

- [docs/workflow_graph.md](docs/workflow_graph.md) shows the project pipeline and the boundary between raw/private inputs, source code, generated outputs, tests, logs, and documentation.

## Setup

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Local OCR also requires Tesseract and OCRmyPDF runtime tools available on PATH. On Windows, verify Tesseract with:

```powershell
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

## Gemini Configuration

For command-line use, set:

```powershell
$env:GEMINI_API_KEY="your-real-key"
$env:GEMINI_MODEL="gemini-2.5-flash"
```

Do not put real keys in `.env.example`, logs, reports, screenshots, or commits.

The dashboard also has a Gemini API key field in **Import Invoices**. That key is used only for that import request and is not saved.

The legacy `env.example` file may exist for compatibility, but `.env.example` is the placeholder file to copy from. Never store real keys in either file.
Gemini PDF extraction uses the optional `google-genai` SDK from `requirements.txt`; tests continue to use mocked callers and do not call the real API.

LLM module structure:
- `scripts/second_pass_llm.py`: orchestration, Gemini TXT parsing, normalization, validation, artifact writing, and CLI.
- `llm/agent/models.py`: typed prompt, payload, normalized extraction, and runtime result models.
- `llm/agent/prompts.py`: prompt templates.
- `llm/api/schemas.py`: typed request/output schemas for API-style integrations.
- `vector_store/base.py`: FAISS/LlamaIndex vector index factory in the same style as `Agenti-AI-main`.
- `vector_store/documents.py`: converts local provider memory into vector-store documents.
- `rag/adaptive_rag.py`: provider memory adapter; retrieves vector hits and converts them into `llm.agent.models.RagSnippet` objects for Gemini prompts.

## Run The Pipeline

Run OCR for all files in `data/data_raw/`:

```powershell
python scripts\ocr_text_extraction.py
```

Run OCR for one file:

```powershell
python scripts\ocr_text_extraction.py --input data\data_raw\agua_01.webp
```

Extract structured fields from OCR text:

```powershell
python scripts\extract_invoice_fields.py
```

Refresh provider memory from the structured CSV:

```powershell
python rag\adaptive_rag.py init
```

Build or refresh the local provider-memory vector index:

```powershell
python rag\adaptive_rag.py index
```

The first vector-index build may need to download the configured HuggingFace embedding model. Do not run it during tests or quality checks unless you explicitly want generated index files.

Run Gemini PDF second pass for one invoice:

```powershell
python scripts\second_pass_llm.py --pdf-file data\data_pdf\telecom_05.pdf --text-file data\data_txt\telecom_05.txt --provider vodafone --invoice-type telecom
```

Gemini outputs are written with stable filenames, for example:

```text
data/data_processed/llm_second_pass/telecom_05_gemini_raw.txt
data/data_processed/llm_second_pass/telecom_05_gemini_structured.json
```

New second-pass runs overwrite these stable files for the same invoice instead of creating timestamped duplicates. The raw Gemini response is plain TXT; the structured artifact remains JSON for dashboard review and export.

## Dashboard

Start the dashboard:

```powershell
python scripts\dashboard.py
```

Open:

```text
http://127.0.0.1:8501
```

Main views:
- **Overview**: processing queue, status, completion, and errors.
- **Import Invoices**: upload invoices, optionally provide Gemini API key/model, run OCR and Gemini PDF extraction.
- **Manual Review**: inspect fields, completion %, validation errors, PDF preview, Gemini second-pass summary, and save corrections.
- **RAG Context**: provider-specific memory used during review.
- **Provider Memory**: saved provider tips, OCR corrections, feedback, and validation history.
- **Invoice Fields**: required schema reference.
- **Export**: download CSV and provider memory.

Manual Review actions:
- Save corrections to memory.
- Approve invoice.
- Reject invoice.
- Re-extract selected OCR.
- Run Gemini PDF pass with an API key entered on the Manual Review page.
- Apply latest Gemini fields.

## Extraction Schema

The structured CSV uses these fields:

- `source_file`
- `ocr_text_file`
- `valid_invoice`
- `invoice_type`
- `invoice_number`
- `invoice_date`
- `currency`
- `payment_due_date`
- `provider_name`
- `provider_vat_number`
- `provider_address`
- `buyer_name`
- `buyer_vat_number`
- `buyer_address`
- `service_plan_name`
- `consumption_start_date`
- `consumption_end_date`
- `units_of_consumption`
- `unit_type`
- `subtotal_value`
- `total_vat`
- `total_value`
- `extraction_warnings`

Missing or uncertain values should be `null`. Do not invent invoice data.

## RAG Memory

Provider memory is stored in:

```text
rag/knowledge_base.json
```

The vector retrieval index is generated from that provider memory and stored in:

```text
data/data_processed/vector_store/
```

It can store:
- Provider aliases.
- Provider-specific extraction tips.
- OCR corrections.
- Known layouts.
- Previously validated invoices.
- Human reviewer feedback.
- Validation history.

Retrieve context manually:

```powershell
python rag\adaptive_rag.py retrieve --text-file data\data_txt\telecom_05.txt --provider vodafone --invoice-type telecom
```

The Gemini second pass asks the vector store for matching provider-memory snippets when OCR text, provider, and invoice type are available. If vector-store dependencies are not installed or the index has not been built, the project falls back to the JSON provider memory so local tests and review can still run.

## Tests

Run the current test suite:

```powershell
python -m pytest tests
```

The tests mock Gemini API calls and do not call the real API.

## Security Notes

- Keep `.env` ignored.
- Keep `.env.example` as placeholders only.
- Keep `.gitignore` active so local caches, logs, environments, secrets, and generated Gemini artifacts are not committed accidentally.
- `.gitignore` also protects raw invoices, OCR outputs, generated reports, provider memory, and generated vector indexes.
- Keep generated vector indexes under `data/data_processed/vector_store/`.
- Do not commit real API keys or private invoice data.
- Do not overwrite raw files in `data/data_raw/`.
- Historical generated reports may contain old run data; review them before committing.

## Known Limitations

- OCR quality depends on local Tesseract/OCRmyPDF installation.
- Some source/OCR text may contain encoding artifacts.
- Deterministic extraction is regex/heuristic-based.
- Gemini second pass requires API access, quota, and network availability.
- Provider memory is stored in JSON and indexed locally into FAISS/LlamaIndex when vector dependencies are installed.
- Old timestamped Gemini artifacts may exist from earlier development runs.
