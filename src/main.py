"""
This script OCRs PDFs
"""

import os
import sys
from pathlib import Path

import pymupdf
import pytesseract
from joblib import Parallel, delayed
from pdf2image import convert_from_path
from tqdm import tqdm


def process_pdfs(base: Path = Path(".")):
    """
    Process all PDF files in "todo" and save the results in "done".

    :param base: The base directory containing the "todo" and "done" directories.
    """
    base.mkdir(exist_ok=True, parents=True)
    (base / "todo").mkdir(exist_ok=True, parents=True)
    (base / "done").mkdir(exist_ok=True, parents=True)

    def predict(input_file: Path, output_file: Path):
        relative_path = input_file.relative_to(base / "todo")
        print(f"Processing {relative_path}...")
        pages = convert_from_path(input_file, fmt="jpeg")

        try:
            input_file.unlink()
        except:
            pass

        # Perform OCR on the images
        doc = pymupdf.open()
        [doc.insert_pdf(pymupdf.open("pdf", pytesseract.image_to_pdf_or_hocr(page))) for page in tqdm(pages)]
        doc.save(output_file, garbage=4, deflate=True)
        doc.close()
        print(f"Processed {relative_path}")

    Parallel(n_jobs=-1)(
        delayed(predict)(Path(root) / file, Path(root.replace("todo", "done")) / file)
        for root, _, files in os.walk(base / "todo")
        for file in files
        if file.lower().endswith(".pdf")
    )


if __name__ == "__main__":
    process_pdfs(Path(sys.argv[1]))
