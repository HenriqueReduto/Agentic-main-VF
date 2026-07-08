GEMINI_EXTRACTION_PROMPT_TEMPLATE = """You are extracting fields from the attached invoice PDF.
Use the attached invoice PDF as the source of truth; OCR text is supporting context only.
Return plain text only, with one field per line in this exact format:
field_name: value
Do not return JSON, markdown tables, bullets, or explanatory text.
Use null for missing, unreadable, ambiguous, or unsupported values.
Provider hint: {provider_name}
Invoice type hint: {invoice_type}
Schema fields:
{schema_fields}
Provider/RAG guidance:
{rag_context}
OCR supporting text:
{ocr_text}"""
