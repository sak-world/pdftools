#!/usr/bin/env python3
"""
PDF Arranger - Interactively rearrange pages in a PDF file.

Usage:
    python pdf_arranger.py <input.pdf>

Requirements:
    pip install pypdf
"""

import sys
import os
from pypdf import PdfReader, PdfWriter


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def load_pdf(pdf_path: str) -> tuple[PdfReader, int]:
    reader = PdfReader(pdf_path)
    return reader, len(reader.pages)


def display_current_order(page_order: list[int]):
    print(f"\n  Current order: {', '.join(str(p) for p in page_order)}")


def save_pdf(reader: PdfReader, page_order: list[int], output_path: str):
    writer = PdfWriter()
    for page_num in page_order:
        writer.add_page(reader.pages[page_num - 1])  # Convert to 0-indexed
    with open(output_path, "wb") as f:
        writer.write(f)


def preview_and_save(reader: PdfReader, page_order: list[int], base_name: str, output_dir: str):
    print(f"\n  📋 Preview new order: {', '.join(str(p) for p in page_order)}")

    default_name = os.path.join(output_dir, f"{base_name}_arranged.pdf")
    user_input = input(f"\n  Save as (press Enter for '{os.path.basename(default_name)}'): ").strip()

    output_path = os.path.join(output_dir, user_input) if user_input else default_name

    # Ensure .pdf extension
    if not output_path.lower().endswith(".pdf"):
        output_path += ".pdf"

    save_pdf(reader, page_order, output_path)
    print(f"\n  ✅ Saved: {output_path}")


# ─────────────────────────────────────────────
#  Operations
# ─────────────────────────────────────────────

def reorder_pages(page_order: list[int], total_pages: int) -> list[int]:
    print(f"\n  Enter the new page order as comma-separated page numbers.")
    print(f"  Example: 3,1,2,5,4")
    print(f"  You can omit pages (they will be excluded from output).")

    raw = input("\n  New order: ").strip()
    if not raw:
        print("  ⚠️  No input provided. Order unchanged.")
        return page_order

    try:
        new_order = [int(p.strip()) for p in raw.split(",")]
    except ValueError:
        print("  ⚠️  Invalid input. Please enter numbers separated by commas.")
        return page_order

    # Validate
    invalid = [p for p in new_order if not (1 <= p <= total_pages)]
    if invalid:
        print(f"  ⚠️  Invalid page number(s): {invalid}. Must be between 1 and {total_pages}.")
        return page_order

    print(f"  → New order set: {', '.join(str(p) for p in new_order)}")
    return new_order


def delete_pages(page_order: list[int], total_pages: int) -> list[int]:
    print(f"\n  Enter page numbers to delete (comma-separated).")
    print(f"  Example: 2,5,7")

    raw = input("\n  Pages to delete: ").strip()
    if not raw:
        print("  ⚠️  No input provided. Nothing deleted.")
        return page_order

    try:
        to_delete = set(int(p.strip()) for p in raw.split(","))
    except ValueError:
        print("  ⚠️  Invalid input. Please enter numbers separated by commas.")
        return page_order

    invalid = [p for p in to_delete if not (1 <= p <= total_pages)]
    if invalid:
        print(f"  ⚠️  Invalid page number(s): {invalid}. Must be between 1 and {total_pages}.")
        return page_order

    new_order = [p for p in page_order if p not in to_delete]

    if not new_order:
        print("  ⚠️  Cannot delete all pages. Operation cancelled.")
        return page_order

    print(f"  → Deleted page(s): {', '.join(str(p) for p in sorted(to_delete))}")
    return new_order


def reverse_pages(page_order: list[int]) -> list[int]:
    confirm = input("\n  Reverse all pages? (y/n): ").strip().lower()
    if confirm == "y":
        new_order = list(reversed(page_order))
        print(f"  → Pages reversed.")
        return new_order
    else:
        print("  → Reverse cancelled.")
        return page_order


def duplicate_page(page_order: list[int], total_pages: int) -> list[int]:
    print(f"\n  Which page would you like to duplicate?")

    try:
        page_num = int(input("  Page to duplicate: ").strip())
    except ValueError:
        print("  ⚠️  Invalid input. Enter a valid page number.")
        return page_order

    if not (1 <= page_num <= total_pages):
        print(f"  ⚠️  Page {page_num} is out of range (1-{total_pages}).")
        return page_order

    print(f"\n  Insert the duplicate at which position? (1-{len(page_order) + 1})")

    try:
        position = int(input("  Insert at position: ").strip())
    except ValueError:
        print("  ⚠️  Invalid input. Enter a valid position.")
        return page_order

    if not (1 <= position <= len(page_order) + 1):
        print(f"  ⚠️  Position {position} is out of range.")
        return page_order

    new_order = page_order.copy()
    new_order.insert(position - 1, page_num)  # Convert to 0-indexed insert
    print(f"  → Page {page_num} duplicated at position {position}.")
    return new_order


# ─────────────────────────────────────────────
#  Menu
# ─────────────────────────────────────────────

def show_menu():
    print("\n" + "=" * 50)
    print("  Choose an arrange option:")
    print("=" * 50)
    print("  1. Reorder pages manually")
    print("  2. Delete pages")
    print("  3. Reverse all pages")
    print("  4. Duplicate a page")
    print("  5. Save & Quit")
    print("=" * 50)


# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python pdf_arranger.py <input.pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not os.path.isfile(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)

    if not pdf_path.lower().endswith(".pdf"):
        print("❌ File does not appear to be a PDF.")
        sys.exit(1)

    reader, total_pages = load_pdf(pdf_path)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_dir = os.path.dirname(os.path.abspath(pdf_path))

    # Track the working page order (1-indexed throughout)
    page_order = list(range(1, total_pages + 1))

    print(f"\n📄 Loaded: {pdf_path}")
    print(f"   Total pages: {total_pages}")

    while True:
        display_current_order(page_order)
        show_menu()

        choice = input("Enter choice (1-5): ").strip()

        if choice == "1":
            page_order = reorder_pages(page_order, total_pages)

        elif choice == "2":
            page_order = delete_pages(page_order, total_pages)

        elif choice == "3":
            page_order = reverse_pages(page_order)

        elif choice == "4":
            page_order = duplicate_page(page_order, total_pages)

        elif choice == "5":
            preview_and_save(reader, page_order, base_name, output_dir)
            break

        else:
            print("⚠️  Invalid choice. Enter 1 to 5.")


if __name__ == "__main__":
    main()
