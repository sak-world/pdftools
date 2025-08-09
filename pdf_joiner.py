#!/usr/bin/env python3
"""
PDF Merger Script
=================

Description:
    A Python script that merges PDF files from a specified directory with intelligent
    behavior based on the number of files found. Provides both automatic and selective
    merging options.

Features:
    - Search current directory by default or specify custom path
    - Smart merging logic based on file count:
      * ≤10 PDFs: Interactive selection with numbered list
      * >10 PDFs: Automatic merging of all files
    - Automatic output file naming with conflict resolution
    - User-friendly interface with cancellation options
    - Comprehensive error handling

Requirements:
    - Python 3.6+
    - PyPDF2 library (install with: pip install PyPDF2)

Usage:
    Basic usage (search current directory):
        python pdf_merger.py

    Specify custom directory:
        python pdf_merger.py --path /path/to/pdf/files
        python pdf_merger.py -p /path/to/pdf/files

    Interactive examples:
        # When ≤10 PDFs found, you can:
        - Enter numbers: "1 3 5" (merges files 1, 3, and 5)
        - Enter "all" (merges all files)
        - Press Enter (cancels operation)

Output:
    - Creates merged PDF in the same directory as source files
    - Default name: "merged_pdfs.pdf"
    - Auto-increments if file exists: "merged_pdfs_1.pdf", "merged_pdfs_2.pdf", etc.

Examples:
    $ python pdf_merger.py
    Searching for PDF files in: /current/directory
    Found 5 PDF files
    
    Found PDF files:
    1. document1.pdf
    2. document2.pdf
    3. document3.pdf
    4. document4.pdf
    5. document5.pdf
    
    Select PDFs to merge:
    - Enter numbers separated by spaces (e.g., '1 3 5')
    - Enter 'all' to merge all files
    - Press Enter to cancel
    
    Your selection: 1 2 4
    
    Merging 3 PDF files...
    Adding: document1.pdf
    Adding: document2.pdf
    Adding: document4.pdf
    
    Success! Merged PDF saved as: /current/directory/merged_pdfs.pdf

Author: Assistant
Version: 1.0
"""

import os
import sys
import argparse
from pathlib import Path
try:
    from PyPDF2 import PdfMerger
except ImportError:
    print("PyPDF2 is required. Install it with: pip install PyPDF2")
    sys.exit(1)

def find_pdf_files(directory):
    """Find all PDF files in the given directory."""
    pdf_files = []
    for file in os.listdir(directory):
        if file.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(directory, file))
    return sorted(pdf_files)

def display_pdf_list(pdf_files):
    """Display PDF files with numbers for selection."""
    print("\nFound PDF files:")
    for i, pdf in enumerate(pdf_files, 1):
        filename = os.path.basename(pdf)
        print(f"{i}. {filename}")

def get_user_selection(pdf_files):
    """Get user selection for PDFs to merge."""
    display_pdf_list(pdf_files)
    print("\nSelect PDFs to merge:")
    print("- Enter numbers separated by spaces (e.g., '1 3 5')")
    print("- Enter 'all' to merge all files")
    print("- Press Enter to cancel")
    
    while True:
        user_input = input("\nYour selection: ").strip()
        
        if not user_input:
            return None
            
        if user_input.lower() == 'all':
            return pdf_files
            
        try:
            numbers = [int(x) for x in user_input.split()]
            selected_files = []
            
            for num in numbers:
                if 1 <= num <= len(pdf_files):
                    selected_files.append(pdf_files[num - 1])
                else:
                    print(f"Invalid number: {num}. Please enter numbers between 1 and {len(pdf_files)}")
                    break
            else:
                return selected_files
                
        except ValueError:
            print("Invalid input. Please enter numbers separated by spaces or 'all'")

def merge_pdfs(pdf_files, output_path):
    """Merge PDF files into a single PDF."""
    if not pdf_files:
        print("No PDF files to merge.")
        return False
        
    try:
        merger = PdfMerger()
        
        print(f"\nMerging {len(pdf_files)} PDF files...")
        for pdf_file in pdf_files:
            print(f"Adding: {os.path.basename(pdf_file)}")
            merger.append(pdf_file)
        
        merger.write(output_path)
        merger.close()
        
        print(f"\nSuccess! Merged PDF saved as: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error merging PDFs: {e}")
        return False

def generate_output_filename(directory):
    """Generate a unique output filename."""
    base_name = "merged_pdfs.pdf"
    output_path = os.path.join(directory, base_name)
    
    # If file exists, add a number
    counter = 1
    while os.path.exists(output_path):
        name_without_ext = f"merged_pdfs_{counter}"
        output_path = os.path.join(directory, f"{name_without_ext}.pdf")
        counter += 1
    
    return output_path

def main():
    parser = argparse.ArgumentParser(description='Merge PDF files from a directory')
    parser.add_argument('--path', '-p', type=str, help='Path to directory containing PDF files')
    args = parser.parse_args()
    
    # Determine the directory to search
    if args.path:
        directory = args.path
        if not os.path.exists(directory):
            print(f"Error: Directory '{directory}' does not exist.")
            sys.exit(1)
        if not os.path.isdir(directory):
            print(f"Error: '{directory}' is not a directory.")
            sys.exit(1)
    else:
        directory = os.getcwd()
    
    print(f"Searching for PDF files in: {directory}")
    
    # Find PDF files
    pdf_files = find_pdf_files(directory)
    
    if not pdf_files:
        print("No PDF files found in the directory.")
        sys.exit(0)
    
    print(f"Found {len(pdf_files)} PDF files")
    
    # Determine merge strategy based on number of files
    if len(pdf_files) <= 10:
        # Show list and ask for selection
        selected_files = get_user_selection(pdf_files)
        if not selected_files:
            print("Operation cancelled.")
            sys.exit(0)
    else:
        # Auto-merge all files
        print(f"Found {len(pdf_files)} PDF files (more than 10). Merging all files automatically...")
        selected_files = pdf_files
    
    # Generate output filename
    output_path = generate_output_filename(directory)
    
    # Merge PDFs
    success = merge_pdfs(selected_files, output_path)
    
    if success:
        print(f"Operation completed successfully!")
    else:
        print("Operation failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()