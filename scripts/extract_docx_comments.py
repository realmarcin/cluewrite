#!/usr/bin/env python3
"""
Extract comments from a Word .docx file.

Usage:
    python scripts/extract_docx_comments.py manuscript/microgrowagents_v3/manuscript_with_comments_v1.docx
"""

import sys
from pathlib import Path
from typing import List, Dict
import zipfile
import xml.etree.ElementTree as ET

def extract_comments_from_docx(docx_path: Path) -> List[Dict]:
    """
    Extract all comments from a .docx file.

    Args:
        docx_path: Path to .docx file

    Returns:
        List of comment dictionaries with id, author, date, text, and referenced_text
    """
    comments = []

    # .docx files are ZIP archives
    with zipfile.ZipFile(docx_path, 'r') as docx_zip:
        # Check if comments.xml exists
        try:
            comments_xml = docx_zip.read('word/comments.xml')
        except KeyError:
            print("No comments found in document (no comments.xml)")
            return []

        # Parse comments.xml
        root = ET.fromstring(comments_xml)

        # Define namespace
        ns = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        }

        # Extract each comment
        for comment in root.findall('.//w:comment', ns):
            comment_id = comment.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
            author = comment.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author', 'Unknown')
            date = comment.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}date', '')

            # Extract comment text from paragraphs
            comment_text_parts = []
            for para in comment.findall('.//w:p', ns):
                para_text = []
                for text_elem in para.findall('.//w:t', ns):
                    if text_elem.text:
                        para_text.append(text_elem.text)
                if para_text:
                    comment_text_parts.append(''.join(para_text))

            comment_text = '\n'.join(comment_text_parts)

            comments.append({
                'id': comment_id,
                'author': author,
                'date': date,
                'text': comment_text
            })

    # Now extract the referenced text from document.xml
    with zipfile.ZipFile(docx_path, 'r') as docx_zip:
        try:
            document_xml = docx_zip.read('word/document.xml')
            doc_root = ET.fromstring(document_xml)

            # Find comment ranges
            for comment in comments:
                comment_id = comment['id']

                # Find commentRangeStart and commentRangeEnd for this comment
                comment_start = doc_root.find(f".//w:commentRangeStart[@w:id='{comment_id}']", ns)
                comment_end = doc_root.find(f".//w:commentRangeEnd[@w:id='{comment_id}']", ns)

                if comment_start is not None and comment_end is not None:
                    # Extract text between start and end markers
                    # This is simplified - a full implementation would need to traverse the XML tree
                    referenced_text = extract_text_between_markers(doc_root, comment_start, comment_end, ns)
                    comment['referenced_text'] = referenced_text
                else:
                    comment['referenced_text'] = ''

        except KeyError:
            pass

    return comments


def extract_text_between_markers(root, start_elem, end_elem, ns):
    """Extract text between two XML elements (simplified version)."""
    # This is a simplified implementation
    # A complete version would need to properly traverse the XML tree
    # For now, we'll return empty string and rely on the comment text itself
    return ''


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/extract_docx_comments.py <path_to_docx>")
        sys.exit(1)

    docx_path = Path(sys.argv[1])

    if not docx_path.exists():
        print(f"Error: File not found: {docx_path}")
        sys.exit(1)

    print(f"Extracting comments from: {docx_path}")
    comments = extract_comments_from_docx(docx_path)

    print(f"\nFound {len(comments)} comments:\n")

    for i, comment in enumerate(comments, 1):
        print(f"Comment {i}:")
        print(f"  ID: {comment['id']}")
        print(f"  Author: {comment['author']}")
        print(f"  Date: {comment['date']}")
        print(f"  Text: {comment['text'][:200]}...")
        if comment.get('referenced_text'):
            print(f"  Referenced: {comment['referenced_text'][:100]}...")
        print()

    # Save to file
    output_file = docx_path.parent / 'extracted_comments.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Comments extracted from: {docx_path}\n")
        f.write(f"Total comments: {len(comments)}\n")
        f.write("=" * 80 + "\n\n")

        for i, comment in enumerate(comments, 1):
            f.write(f"Comment {i}:\n")
            f.write(f"Author: {comment['author']}\n")
            f.write(f"Date: {comment['date']}\n")
            f.write(f"Text:\n{comment['text']}\n")
            if comment.get('referenced_text'):
                f.write(f"Referenced text: {comment['referenced_text']}\n")
            f.write("\n" + "-" * 80 + "\n\n")

    print(f"Comments saved to: {output_file}")


if __name__ == '__main__':
    main()
