#!/usr/bin/env python3
"""
Extract figures/images from DOCX files.

Uses python-docx to extract all embedded images from a Word document.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict
import json

try:
    from docx import Document
    from docx.oxml import parse_xml
except ImportError:
    print("Error: python-docx not installed. Run: pip3 install python-docx")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("Warning: Pillow not installed. Image dimension detection disabled.")
    Image = None


def extract_images_from_docx(docx_path: Path, output_dir: Path) -> List[Dict]:
    """Extract all images from DOCX file."""
    doc = Document(docx_path)

    output_dir.mkdir(parents=True, exist_ok=True)

    images_info = []
    image_count = 0

    # Extract images from document relationships
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            image_count += 1

            # Get image data
            image_data = rel.target_part.blob

            # Determine file extension
            content_type = rel.target_part.content_type
            if 'png' in content_type:
                ext = 'png'
            elif 'jpeg' in content_type or 'jpg' in content_type:
                ext = 'jpg'
            elif 'gif' in content_type:
                ext = 'gif'
            elif 'svg' in content_type:
                ext = 'svg'
            elif 'pdf' in content_type:
                ext = 'pdf'
            else:
                ext = 'bin'

            # Save image
            image_filename = f"extracted_image{image_count}.{ext}"
            image_path = output_dir / image_filename

            with open(image_path, 'wb') as f:
                f.write(image_data)

            # Get dimensions if possible
            dimensions = None
            if Image and ext in ['png', 'jpg', 'jpeg', 'gif']:
                try:
                    with Image.open(image_path) as img:
                        dimensions = f"{img.width}x{img.height}"
                except Exception:
                    pass

            file_size = len(image_data)

            images_info.append({
                "image_number": image_count,
                "filename": image_filename,
                "format": ext.upper(),
                "dimensions": dimensions,
                "size_bytes": file_size,
                "size_kb": round(file_size / 1024, 1)
            })

    return images_info


def main():
    parser = argparse.ArgumentParser(
        description="Extract images from DOCX file"
    )
    parser.add_argument(
        "--docx",
        type=Path,
        required=True,
        help="Path to DOCX file"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Output directory for extracted images"
    )

    args = parser.parse_args()

    if not args.docx.exists():
        print(f"Error: DOCX file not found: {args.docx}")
        sys.exit(1)

    print(f"Extracting images from: {args.docx}")
    images = extract_images_from_docx(args.docx, args.output_dir)

    print(f"\nExtracted {len(images)} images to: {args.output_dir}")

    # Print summary
    for img in images:
        print(f"\nImage {img['image_number']}: {img['filename']}")
        print(f"  Format: {img['format']}")
        if img['dimensions']:
            print(f"  Dimensions: {img['dimensions']}")
        print(f"  Size: {img['size_kb']} KB")

    # Save metadata
    metadata_path = args.output_dir / "images_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(images, f, indent=2)

    print(f"\nMetadata saved to: {metadata_path}")


if __name__ == "__main__":
    main()
