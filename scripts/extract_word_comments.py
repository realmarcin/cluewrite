#!/usr/bin/env python3
"""
Extract comments from Word .docx file using multiple methods.
"""

import sys
from pathlib import Path
import zipfile
import xml.etree.ElementTree as etree

def extract_comments_comprehensive(docx_path: Path):
    """Extract comments from .docx using comprehensive XML parsing."""

    print(f"Analyzing: {docx_path}\n")

    with zipfile.ZipFile(docx_path, 'r') as docx_zip:
        # List all files in the docx
        print("Files in .docx archive:")
        for name in docx_zip.namelist():
            print(f"  {name}")
        print()

        # Check for comments.xml
        if 'word/comments.xml' in docx_zip.namelist():
            print("Found word/comments.xml - extracting comments...\n")
            comments_xml = docx_zip.read('word/comments.xml')

            # Parse with ElementTree
            root = etree.fromstring(comments_xml)

            # Define namespaces
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

            comments = root.findall('.//w:comment', ns)

            print(f"Found {len(comments)} comments:\n")
            print("=" * 80)

            extracted = []
            for i, comment in enumerate(comments, 1):
                comment_id = comment.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
                author = comment.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author', 'Unknown')
                date = comment.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}date', '')
                initials = comment.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}initials', '')

                # Extract all text from the comment
                text_nodes = comment.findall('.//w:t', ns)
                comment_text = ''.join([t.text for t in text_nodes if t.text])

                print(f"\nComment {i}:")
                print(f"  ID: {comment_id}")
                print(f"  Author: {author} ({initials})")
                print(f"  Date: {date}")
                print(f"  Text: {comment_text}")
                print("-" * 80)

                extracted.append({
                    'id': comment_id,
                    'author': author,
                    'initials': initials,
                    'date': date,
                    'text': comment_text
                })

            return extracted
        else:
            print("No word/comments.xml found - document may have embedded comments\n")

            # Try to extract inline comments/highlights
            if 'word/document.xml' in docx_zip.namelist():
                document_xml = docx_zip.read('word/document.xml')
                doc_root = etree.fromstring(document_xml)

                ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

                # Look for comment markers
                comment_starts = doc_root.findall('.//w:commentRangeStart', ns)
                comment_ends = doc_root.findall('.//w:commentRangeEnd', ns)
                comment_refs = doc_root.findall('.//w:commentReference', ns)

                print(f"Found {len(comment_starts)} comment range starts")
                print(f"Found {len(comment_ends)} comment range ends")
                print(f"Found {len(comment_refs)} comment references")

                # Look for highlights that might be inline comments
                highlights = doc_root.findall('.//w:highlight', ns)
                print(f"Found {len(highlights)} highlights")

                # Look for track changes
                insertions = doc_root.findall('.//w:ins', ns)
                deletions = doc_root.findall('.//w:del', ns)
                print(f"Found {len(insertions)} insertions (track changes)")
                print(f"Found {len(deletions)} deletions (track changes)")

    return []


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_word_comments.py <path_to_docx>")
        sys.exit(1)

    docx_path = Path(sys.argv[1])

    if not docx_path.exists():
        print(f"Error: File not found: {docx_path}")
        sys.exit(1)

    comments = extract_comments_comprehensive(docx_path)

    if comments:
        # Save to file
        output_file = docx_path.parent / 'WORD_COMMENTS.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Comments extracted from: {docx_path}\n")
            f.write(f"Total comments: {len(comments)}\n")
            f.write("=" * 80 + "\n\n")

            for i, comment in enumerate(comments, 1):
                f.write(f"Comment {i}:\n")
                f.write(f"  Author: {comment['author']} ({comment['initials']})\n")
                f.write(f"  Date: {comment['date']}\n")
                f.write(f"  ID: {comment['id']}\n")
                f.write(f"  Text:\n{comment['text']}\n")
                f.write("\n" + "-" * 80 + "\n\n")

        print(f"\n\nComments saved to: {output_file}")
    else:
        print("\n\nNo extractable comments found.")


if __name__ == '__main__':
    main()
