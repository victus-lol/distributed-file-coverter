import os
import subprocess


def convert(input_path, target_format):
    """
    Convert document files using LibreOffice (soffice).
    Supports: docx→pdf, txt→pdf, odt→pdf, etc.
    Requires LibreOffice installed: sudo apt install libreoffice
    """
    target_format = target_format.lower().strip('.')
    output_dir = os.path.dirname(input_path) or "."

    cmd = [
        "soffice", "--headless",
        "--convert-to", target_format,
        "--outdir", output_dir,
        input_path
    ]

    print(f"[DOC CONVERTER] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"LibreOffice error: {result.stderr}")

    base = os.path.splitext(input_path)[0]
    output_path = f"{base}.{target_format}"

    if not os.path.exists(output_path):
        raise FileNotFoundError(f"Converted file not found: {output_path}")

    print(f"[DOC CONVERTER] {input_path} → {output_path}")
    return output_path


def can_handle(input_path, target_format):
    doc_formats = {'pdf', 'docx', 'odt', 'txt', 'html', 'rtf'}
    ext = os.path.splitext(input_path)[1].lower().strip('.')
    return ext in doc_formats and target_format.lower() in doc_formats