#!/usr/bin/env python3
"""
Apply Manuscript Edits to Google Docs in Safe Batches

Orchestrates all 7 batches of edits from manuscript_v2_final.md to Google Docs:
  Batch 1: Title replacement
  Batch 2: Terminology find/replace
  Batch 3: Abstract replacement
  Batch 4: Introduction replacement
  Batch 5: Results replacement
  Batch 6: Discussion replacement
  Batch 7: Methods (SKIPPED per user clarification)

Usage:
    # Dry run all batches
    python scripts/apply_manuscript_edits.py \
        --document-id 1gwjtHp863cFv61rJ3gd7l2RGje6tQy6he3bC8YFBuSU \
        --manuscript-file manuscript/kbaseeco_v2/manuscript_v2_final.md \
        --dry-run

    # Apply specific batches
    python scripts/apply_manuscript_edits.py \
        --document-id DOC_ID \
        --manuscript-file manuscript_v2_final.md \
        --batches 1,2,3 \
        --validate-after-each

    # Apply all batches (excluding Batch 7)
    python scripts/apply_manuscript_edits.py \
        --document-id DOC_ID \
        --manuscript-file manuscript_v2_final.md \
        --all
"""

import argparse
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from safe_gdoc_editor import SafeGoogleDocEditor
from table_preserving_editor import TablePreservingEditor


SCOPES = ['https://www.googleapis.com/auth/documents']


@dataclass
class BatchConfig:
    """Configuration for a batch of edits"""
    batch_num: int
    name: str
    description: str
    risk_level: str  # NONE, LOW, MEDIUM, HIGH


class ManuscriptParser:
    """Parse manuscript_v2_final.md to extract sections"""

    SECTION_MARKERS = {
        'title': r'^#\s+(.+?)(?:\n|$)',
        'abstract': r'##\s+Abstract[^\n]*\n+(.*?)(?=\n##[^#]|\Z)',
        'introduction': r'##\s+Introduction[^\n]*\n+(.*?)(?=\n##[^#]|\Z)',
        'results': r'##\s+Results[^\n]*\n+(.*?)(?=\n##[^#]|\Z)',
        'discussion': r'##\s+Discussion[^\n]*\n+(.*?)(?=\n##[^#]|\Z)',
        'methods': r'##\s+Methods[^\n]*\n+(.*?)(?=\n##[^#]|\Z)',
    }

    def __init__(self, manuscript_path: Path):
        self.manuscript_path = manuscript_path
        self.content = manuscript_path.read_text()

    def extract_title(self) -> Optional[str]:
        """Extract manuscript title"""
        match = re.search(self.SECTION_MARKERS['title'], self.content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None

    def extract_section(self, section_name: str) -> Optional[str]:
        """Extract section content by name"""
        pattern = self.SECTION_MARKERS.get(section_name.lower())
        if not pattern:
            return None

        match = re.search(pattern, self.content, re.DOTALL | re.MULTILINE)
        if match:
            raw_text = match.group(1).strip() if section_name.lower() != 'title' else match.group(1).strip()
            # Clean markdown formatting before returning
            return self.clean_markdown(raw_text)
        return None

    def clean_markdown(self, text: str) -> str:
        """
        Clean markdown formatting for Google Docs insertion

        Removes:
        - Horizontal line separators (--------)
        - Markdown heading markers (#####)
        - Bold/italic markers (**, __, *, _)
        - Image references (![...]) - COMPLETELY REMOVED
        - Markdown tables (|---|) and table borders (+===+)
        - Figure placeholders
        - Preserves citation parentheses
        """
        # Remove horizontal line separators
        text = re.sub(r'^-{3,}$', '', text, flags=re.MULTILINE)

        # Remove markdown image references COMPLETELY (don't leave placeholder)
        # Handles: ![caption](path) or ![](path){attributes}
        text = re.sub(r'!\[.*?\]\(.*?\)(\{.*?\})?', '', text)

        # Remove figure reference lines (e.g., "Figure X" on its own line)
        text = re.sub(r'^\s*Figure\s+X\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'^\s*\[IMAGE PLACEHOLDER\]\s*$', '', text, flags=re.MULTILINE)

        # Remove markdown table syntax completely
        # Table borders: +-----+
        text = re.sub(r'^\+[+=]+\+$', '', text, flags=re.MULTILINE)
        # Table rows: | col | col |
        text = re.sub(r'^\|.*?\|$', '', text, flags=re.MULTILINE)
        # Table separators: |---|---|
        text = re.sub(r'^\|[-:|]+\|$', '', text, flags=re.MULTILINE)

        # Remove any lines that are just separators
        text = re.sub(r'^[+|=\-\s]+$', '', text, flags=re.MULTILINE)

        # Remove markdown heading markers (##### **Text** -> Text)
        text = re.sub(r'^#{1,6}\s+\*\*(.+?)\*\*', r'\1', text, flags=re.MULTILINE)
        text = re.sub(r'^#{1,6}\s+(.+?)$', r'\1', text, flags=re.MULTILINE)

        # Remove bold markers but preserve content: **text** -> text
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)

        # Remove italic markers: *text* -> text (but not in citations)
        # Only remove single * that are not in (Author et al. year) patterns
        text = re.sub(r'(?<![(\w])\*(?!\*)(.+?)\*(?![)\w])', r'\1', text)

        # Remove underline markers: __text__ -> text
        text = re.sub(r'__(.+?)__', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)

        # Clean up multiple blank lines (but preserve paragraph breaks)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Remove any remaining placeholder text
        text = re.sub(r'\[IMAGE PLACEHOLDER\]', '', text)

        return text.strip()


class BatchOrchestrator:
    """Orchestrates batched edits to Google Doc"""

    # Batch configurations
    BATCHES = {
        1: BatchConfig(1, "Title", "Replace title with subtitle", "NONE"),
        2: BatchConfig(2, "Terminology", "Find/replace terminology", "LOW"),
        3: BatchConfig(3, "Abstract", "Replace Abstract section", "MEDIUM"),
        4: BatchConfig(4, "Introduction", "Replace Introduction section", "HIGH"),
        5: BatchConfig(5, "Results", "Replace Results section", "HIGH"),
        6: BatchConfig(6, "Discussion", "Replace Discussion section", "HIGH"),
        7: BatchConfig(7, "Methods", "Replace Methods section", "MEDIUM"),
    }

    # Terminology replacements for Batch 2
    TERMINOLOGY_REPLACEMENTS = {
        "adaptive significance": "ecosystem-discriminative significance",
        "essential for survival": "characteristic of",
        "selection": "enrichment",
    }

    def __init__(
        self,
        service,
        document_id: str,
        manuscript_parser: ManuscriptParser,
        dry_run: bool = False
    ):
        self.service = service
        self.document_id = document_id
        self.parser = manuscript_parser
        self.dry_run = dry_run
        self.editor = SafeGoogleDocEditor(service, document_id)

    def apply_batch_1_title(self) -> bool:
        """Batch 1: Replace title"""
        print(f"\n{'='*70}")
        print(f"BATCH 1: TITLE REPLACEMENT (Risk: NONE)")
        print(f"{'='*70}")

        new_title = self.parser.extract_title()
        if not new_title:
            print("❌ Could not extract title from manuscript")
            return False

        print(f"New title: {new_title[:80]}...")

        if self.dry_run:
            print("\n[DRY RUN] Would replace title with:")
            print(f"  {new_title}")
            return True

        # Use simple replaceAllText (safe - single occurrence)
        try:
            # First, get current title to replace
            doc = self.service.documents().get(documentId=self.document_id).execute()
            content = doc.get('body', {}).get('content', [])

            # Find first heading (could be TITLE or HEADING_1)
            old_title = None
            for element in content:
                if 'paragraph' in element:
                    style = element['paragraph'].get('paragraphStyle', {})
                    style_type = style.get('namedStyleType', '')
                    if style_type in ['TITLE', 'HEADING_1']:
                        for elem in element['paragraph'].get('elements', []):
                            if 'textRun' in elem:
                                old_title = elem['textRun'].get('content', '').strip()
                                break
                    if old_title:
                        break

            if not old_title:
                print("❌ Could not find current title in document")
                return False

            print(f"Old title: {old_title[:80]}...")

            # Replace title
            requests = [{
                'replaceAllText': {
                    'containsText': {
                        'text': old_title,
                        'matchCase': True
                    },
                    'replaceText': new_title
                }
            }]

            result = self.service.documents().batchUpdate(
                documentId=self.document_id,
                body={'requests': requests}
            ).execute()

            print("✅ Title replaced successfully")
            return True

        except HttpError as error:
            print(f'❌ Error: {error}')
            return False

    def apply_batch_2_terminology(self) -> bool:
        """Batch 2: Find/replace terminology"""
        print(f"\n{'='*70}")
        print(f"BATCH 2: TERMINOLOGY REPLACEMENTS (Risk: LOW)")
        print(f"{'='*70}")

        for old_term, new_term in self.TERMINOLOGY_REPLACEMENTS.items():
            print(f"\n  '{old_term}' → '{new_term}'")

        if self.dry_run:
            print("\n[DRY RUN] Would apply terminology replacements")
            return True

        # Apply sequential replaceAllText
        try:
            requests = []
            for old_term, new_term in self.TERMINOLOGY_REPLACEMENTS.items():
                requests.append({
                    'replaceAllText': {
                        'containsText': {
                            'text': old_term,
                            'matchCase': False
                        },
                        'replaceText': new_term
                    }
                })

            result = self.service.documents().batchUpdate(
                documentId=self.document_id,
                body={'requests': requests}
            ).execute()

            print(f"\n✅ Applied {len(self.TERMINOLOGY_REPLACEMENTS)} terminology replacements")
            return True

        except HttpError as error:
            print(f'❌ Error: {error}')
            return False

    def apply_batch_section(self, batch_num: int, section_name: str, preserve_tables: bool = False) -> bool:
        """Apply section replacement (Batches 3-6)"""
        config = self.BATCHES[batch_num]

        print(f"\n{'='*70}")
        print(f"BATCH {batch_num}: {config.name.upper()} (Risk: {config.risk_level})")
        print(f"{'='*70}")

        # Extract section from manuscript
        new_text = self.parser.extract_section(section_name)
        if not new_text:
            print(f"❌ Could not extract {section_name} from manuscript")
            return False

        print(f"Extracted {len(new_text):,} characters from {section_name}")

        # Use table-preserving editor for sections with tables
        if preserve_tables:
            print(f"🛡️ Using TABLE-PRESERVING mode (keeps existing tables/figures)")
            table_editor = TablePreservingEditor(self.service, self.document_id)
            return table_editor.replace_section_preserve_tables(section_name, new_text, dry_run=self.dry_run)
        else:
            # Use SafeGoogleDocEditor for normal section replacement
            return self.editor.replace_section(section_name, new_text, dry_run=self.dry_run)

    def validate_batch(self, batch_num: int) -> bool:
        """Validate batch results"""
        print(f"\n🔍 Validating Batch {batch_num}...")

        try:
            doc = self.service.documents().get(documentId=self.document_id).execute()

            if batch_num == 2:
                # Check for forbidden terms
                text = self._extract_full_text(doc)
                forbidden_found = []

                for term in self.TERMINOLOGY_REPLACEMENTS.keys():
                    if term.lower() in text.lower():
                        forbidden_found.append(term)

                if forbidden_found:
                    print(f"  ⚠️ Found forbidden terms: {', '.join(forbidden_found)}")
                    return False
                else:
                    print(f"  ✓ No forbidden terms found")

            elif batch_num >= 3:
                # Check for Paperpile links
                links = self._count_paperpile_links(doc)
                print(f"  ✓ Found {links} Paperpile citation links")

                # Check for 'cite' prefix (unmatched citations)
                text = self._extract_full_text(doc)
                cite_count = text.count('cite(')
                if cite_count > 0:
                    print(f"  ⚠️ Found {cite_count} unmatched citations with 'cite' prefix")
                    print(f"     → Manually add Paperpile links for these")

            return True

        except HttpError as error:
            print(f'  ❌ Validation error: {error}')
            return False

    def _extract_full_text(self, doc: Dict) -> str:
        """Extract all text from document"""
        text_parts = []
        for element in doc.get('body', {}).get('content', []):
            if 'paragraph' in element:
                for elem in element['paragraph'].get('elements', []):
                    if 'textRun' in elem:
                        text_parts.append(elem['textRun'].get('content', ''))
        return ''.join(text_parts)

    def _count_paperpile_links(self, doc: Dict) -> int:
        """Count Paperpile links in document"""
        count = 0
        for element in doc.get('body', {}).get('content', []):
            if 'paragraph' in element:
                for elem in element['paragraph'].get('elements', []):
                    if 'textRun' in elem:
                        style = elem['textRun'].get('textStyle', {})
                        if 'link' in style:
                            url = style['link'].get('url', '')
                            if 'paperpile.com' in url:
                                count += 1
        return count


def main():
    parser = argparse.ArgumentParser(
        description="Apply manuscript edits to Google Docs in safe batches"
    )
    parser.add_argument('--document-id', required=True, help="Google Doc ID")
    parser.add_argument('--manuscript-file', type=Path, required=True,
                       help="Path to manuscript_v2_final.md")
    parser.add_argument('--credentials', type=Path, default=Path('credentials.json'),
                       help="Path to credentials.json")
    parser.add_argument('--batches', help="Comma-separated batch numbers (e.g., 1,2,3)")
    parser.add_argument('--all', action='store_true',
                       help="Apply all batches (1-6, skipping 7)")
    parser.add_argument('--dry-run', action='store_true',
                       help="Preview changes without applying")
    parser.add_argument('--validate-after-each', action='store_true',
                       help="Validate after each batch")

    args = parser.parse_args()

    # Validate manuscript file exists
    if not args.manuscript_file.exists():
        print(f"❌ Manuscript file not found: {args.manuscript_file}")
        return 1

    # Parse batch numbers
    if args.all:
        batch_nums = [1, 2, 3, 4, 5, 6]  # Skip batch 7
    elif args.batches:
        batch_nums = [int(b.strip()) for b in args.batches.split(',')]
        # Validate batch numbers
        for b in batch_nums:
            if b not in BatchOrchestrator.BATCHES:
                print(f"❌ Invalid batch number: {b}")
                return 1
    else:
        print("❌ Must specify either --batches or --all")
        return 1

    print(f"\n{'='*70}")
    print(f"MANUSCRIPT EDIT ORCHESTRATOR")
    print(f"{'='*70}")
    print(f"Document ID: {args.document_id}")
    print(f"Manuscript: {args.manuscript_file}")
    print(f"Batches: {', '.join(map(str, batch_nums))}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"{'='*70}")

    # Authenticate
    try:
        creds = service_account.Credentials.from_service_account_file(
            str(args.credentials), scopes=SCOPES)
        service = build('docs', 'v1', credentials=creds)
        print("✓ Authenticated with Google Docs API")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return 1

    # Parse manuscript
    manuscript = ManuscriptParser(args.manuscript_file)
    print(f"✓ Parsed manuscript")

    # Initialize orchestrator
    orchestrator = BatchOrchestrator(
        service,
        args.document_id,
        manuscript,
        dry_run=args.dry_run
    )

    # Apply batches
    results = {}
    for batch_num in batch_nums:
        config = BatchOrchestrator.BATCHES[batch_num]

        # Apply batch
        if batch_num == 1:
            success = orchestrator.apply_batch_1_title()
        elif batch_num == 2:
            success = orchestrator.apply_batch_2_terminology()
        elif batch_num == 3:
            success = orchestrator.apply_batch_section(3, 'Abstract')
        elif batch_num == 4:
            success = orchestrator.apply_batch_section(4, 'Introduction')
        elif batch_num == 5:
            success = orchestrator.apply_batch_section(5, 'Results', preserve_tables=True)
        elif batch_num == 6:
            success = orchestrator.apply_batch_section(6, 'Discussion')
        elif batch_num == 7:
            success = orchestrator.apply_batch_section(7, 'Methods')
        else:
            print(f"❌ Unknown batch number: {batch_num}")
            success = False

        results[batch_num] = success

        if not success:
            print(f"\n❌ Batch {batch_num} failed. Stopping.")
            break

        # Validate if requested
        if args.validate_after_each and not args.dry_run:
            if not orchestrator.validate_batch(batch_num):
                print(f"\n⚠️ Validation warnings for Batch {batch_num}")

    # Summary
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")

    for batch_num in batch_nums:
        config = BatchOrchestrator.BATCHES[batch_num]
        status = "✅ SUCCESS" if results.get(batch_num) else "❌ FAILED"
        print(f"Batch {batch_num} ({config.name}): {status}")

    if args.dry_run:
        print(f"\n💡 This was a DRY RUN. Run without --dry-run to apply changes.")
    else:
        print(f"\n🔗 View document: https://docs.google.com/document/d/{args.document_id}/edit")

    all_success = all(results.values())
    return 0 if all_success else 1


if __name__ == '__main__':
    exit(main())
