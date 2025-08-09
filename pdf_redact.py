#!/usr/bin/env python3
"""
PDF Text Redaction Script
=========================

Description:
    Automatically redacts (blackouts) sensitive information from PDF files.
    Searches for specified terms and covers them with black rectangles.
    Supports password-protected PDFs.

Requirements:
    - Python 3.6+
    - PyMuPDF library (install with: pip install PyMuPDF)

Usage:
    python redact_pdf.py input_file.pdf output_file.pdf

Arguments:
    input_pdf       Path to the input PDF file to redact
    output_pdf      Path where the redacted PDF will be saved

Features:
    - Searches for sensitive terms throughout the entire document
    - Handles password-protected PDFs (prompts for password)
    - Creates permanent redactions (black rectangles over text)
    - Preserves original PDF structure and formatting
    - Case-sensitive text matching

Setup:
    Before running, add your sensitive terms to the 'sensitive_terms' list:
    sensitive_terms = [
        "Social Security Number",
        "SSN:",
        "Credit Card",
        "Account Number",
        # Add more terms as needed
    ]

Examples:
    # Basic usage
    python redact_pdf.py document.pdf redacted_document.pdf
    
    # With password-protected PDF
    python redact_pdf.py secure_doc.pdf redacted_secure_doc.pdf
    Enter PDF password (leave blank if not needed): [password will be hidden]

Output:
    - Creates a new PDF file with sensitive information blacked out
    - Original file remains unchanged
    - Redactions are permanent and cannot be undone

Note:
    - Review the sensitive_terms list before running
    - Test on a copy of your document first
    - Redacted text cannot be recovered from the output file
"""

import fitz
import getpass
import argparse

# Add your sensitive terms here before running the script
sensitive_terms = [
    "ANATHA KRISHNAN",
    "ANATM2708754107",
    "4107YG002826",
    "4107YG002831",
    "4107YG002878",
    "49 Years Male"
]

parser = argparse.ArgumentParser(description='Redact sensitive info from PDFs.')
parser.add_argument('input_pdf', help='Input PDF file path')
parser.add_argument('output_pdf', help='Output PDF file path')
args = parser.parse_args()

def redact_text_in_pdf(input_pdf, output_pdf, terms, password=None):
    doc = fitz.open(input_pdf)
    if doc.needs_pass:
        if not doc.authenticate(password):
            print("Wrong password or unable to unlock the PDF.")
            return
    for page in doc:
        for term in terms:
            text_instances = page.search_for(term)
            for inst in text_instances:
                page.add_redact_annot(inst, fill=(0, 0, 0))
        page.apply_redactions()
    doc.save(output_pdf)
    doc.close()
    print(f"Redacted PDF saved as {output_pdf}")

pdf_password = getpass.getpass("Enter PDF password (leave blank if not needed): ")
pdf_password = pdf_password if pdf_password else None
redact_text_in_pdf(args.input_pdf, args.output_pdf, sensitive_terms, pdf_password)