#!/usr/bin/env python3
"""
PDF Splitter - Interactively split a PDF file by page numbers.

Usage:
    python pdf_splitter.py <input.pdf>

Requirements:
    pip install pypdf
"""

import sys
import os
from pypdf import PdfReader, PdfWriter


def get_page_count(pdf_path: str) -> int:
    reader = PdfReader(pdf_path)
    return len(reader.pages)


def parse_page_range(range_str: str, total_pages: int) -> list[int]:
    """Parse a page range string like '1-5' or '3' into a list of 0-indexed page numbers."""
    pages = []
    parts = range_str.strip().split("-")
    if len(parts) == 1:
        page = int(parts[0])
        if not (1 <= page <= total_pages):
            raise ValueError(f"Page {page} is out of range (1-{total_pages})")
        pages.append(page - 1)  # Convert to 0-indexed
    elif len(parts) == 2:
        start, end = int(parts[0]), int(parts[1])
        if start > end:
            raise ValueError(f"Start page {start} must be <= end page {end}")
        if not (1 <= start <= total_pages and 1 <= end <= total_pages):
            raise ValueError(f"Pages must be between 1 and {total_pages}")
        pages.extend(range(start - 1, end))  # Convert to 0-indexed
    else:
        raise ValueError(f"Invalid range format: '{range_str}'. Use '3' or '1-5'.")
    return pages


def save_split(reader: PdfReader, pages: list[int], output_path: str):
    """Write the given 0-indexed pages to a new PDF file."""
    writer = PdfWriter()
    for page_index in pages:
        writer.add_page(reader.pages[page_index])
    with open(output_path, "wb") as f:
        writer.write(f)


def split_every_page(reader: PdfReader, base_name: str, output_dir: str):
    """Split into one PDF per page."""
    total = len(reader.pages)
    for i in range(total):
        out_path = os.path.join(output_dir, f"{base_name}_page_{i + 1}.pdf")
        save_split(reader, [i], out_path)
        print(f"  Saved: {out_path}")
    print(f"\n✅ Split into {total} individual page(s).")


def split_at_page(reader: PdfReader, split_page: int, base_name: str, output_dir: str):
    """Split into two parts: before and from the given page."""
    total = len(reader.pages)
    part1 = list(range(0, split_page - 1))      # pages before split_page
    part2 = list(range(split_page - 1, total))   # pages from split_page onward

    if not part1 or not part2:
        print("⚠️  Split point would result in an empty section. Choose a different page.")
        return

    out1 = os.path.join(output_dir, f"{base_name}_pages_1-{split_page - 1}.pdf")
    out2 = os.path.join(output_dir, f"{base_name}_pages_{split_page}-{total}.pdf")

    save_split(reader, part1, out1)
    save_split(reader, part2, out2)
    print(f"  Saved: {out1}  ({len(part1)} page(s))")
    print(f"  Saved: {out2}  ({len(part2)} page(s))")
    print(f"\n✅ Split into 2 parts at page {split_page}.")


def split_custom_ranges(reader: PdfReader, total_pages: int, base_name: str, output_dir: str):
    """Let the user define multiple named ranges to extract."""
    print("\nEnter each range on its own line (e.g. '1-5' or '7').")
    print("Press Enter on a blank line when done.\n")

    ranges = []
    while True:
        entry = input("  Range (or blank to finish): ").strip()
        if not entry:
            break
        try:
            pages = parse_page_range(entry, total_pages)
            ranges.append((entry, pages))
            print(f"    → {len(pages)} page(s) added.")
        except ValueError as e:
            print(f"    ⚠️  {e}")

    if not ranges:
        print("No ranges entered. Returning to menu.")
        return

    for idx, (label, pages) in enumerate(ranges, start=1):
        safe_label = label.replace("-", "_")
        out_path = os.path.join(output_dir, f"{base_name}_range_{safe_label}.pdf")
        save_split(reader, pages, out_path)
        print(f"  Saved: {out_path}  ({len(pages)} page(s))")

    print(f"\n✅ Saved {len(ranges)} custom range(s).")


def show_menu(total_pages: int):
    print("\n" + "=" * 50)
    print(f"  PDF has {total_pages} page(s). Choose a split method:")
    print("=" * 50)
    print("  1. Split every page into a separate PDF")
    print("  2. Split into two parts at a specific page")
    print("  3. Extract custom page ranges")
    print("  4. Quit")
    print("=" * 50)


def main():
    if len(sys.argv) < 2:
        print("Usage: python pdf_splitter.py <input.pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not os.path.isfile(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)

    if not pdf_path.lower().endswith(".pdf"):
        print("❌ File does not appear to be a PDF.")
        sys.exit(1)

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_dir = os.path.dirname(os.path.abspath(pdf_path))

    print(f"\n📄 Loaded: {pdf_path}")
    print(f"   Total pages: {total_pages}")

    while True:
        show_menu(total_pages)
        choice = input("Enter choice (1-4): ").strip()

        if choice == "1":
            split_every_page(reader, base_name, output_dir)

        elif choice == "2":
            try:
                page_num = int(input(f"Split BEFORE which page? (2-{total_pages}): ").strip())
                if not (2 <= page_num <= total_pages):
                    print(f"⚠️  Please enter a page between 2 and {total_pages}.")
                else:
                    split_at_page(reader, page_num, base_name, output_dir)
            except ValueError:
                print("⚠️  Please enter a valid integer.")

        elif choice == "3":
            split_custom_ranges(reader, total_pages, base_name, output_dir)

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("⚠️  Invalid choice. Enter 1, 2, 3, or 4.")

        again = input("\nPerform another split on the same file? (y/n): ").strip().lower()
        if again != "y":
            print("Done.")
            break


if __name__ == "__main__":
    main()
