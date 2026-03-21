#!/usr/bin/env python3
"""
Apply Batched Edits to Google Doc via API (Paperpile-Safe)

Uses Google Docs API to programmatically apply edits from BATCHED_EDIT_PLAN.md
while preserving Paperpile citation links and formatting.

Prerequisites:
    pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

Authentication:
    1. Create OAuth2 credentials in Google Cloud Console
    2. Download credentials.json
    3. First run will open browser for authorization
    4. Token stored in token.json for future use

Usage:
    python scripts/apply_gdoc_edits.py \
        --document-id YOUR_GOOGLE_DOC_ID \
        --edit-plan manuscript/kbaseeco_v2/BATCHED_EDIT_PLAN.md \
        --credentials credentials.json \
        --batch 1,2,3,4,5,6,7 \
        --dry-run
"""

import argparse
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/documents']


@dataclass
class GoogleDocsEdit:
    """Represents a single edit operation for Google Docs API"""
    batch_num: int
    edit_num: int
    section: str
    edit_type: str  # 'replace_all', 'replace_text', 'insert_text'
    find_text: str
    replace_text: str
    match_case: bool = False
    priority: str = "OPTIONAL"

    def to_request(self) -> Dict:
        """Convert to Google Docs API request format"""
        if self.edit_type == 'replace_all':
            return {
                'replaceAllText': {
                    'containsText': {
                        'text': self.find_text,
                        'matchCase': self.match_case
                    },
                    'replaceText': self.replace_text
                }
            }
        else:
            raise NotImplementedError(f"Edit type {self.edit_type} not yet implemented")


def authenticate_gdocs(credentials_path: Path, token_path: Path) -> Credentials:
    """Authenticate with Google Docs API (supports both OAuth2 and Service Account)"""

    # Check if credentials file is a service account
    try:
        with open(credentials_path, 'r') as f:
            cred_data = json.load(f)

        # Service account credentials have a 'type' field
        if cred_data.get('type') == 'service_account':
            print("🔑 Using service account authentication")
            creds = service_account.Credentials.from_service_account_file(
                str(credentials_path), scopes=SCOPES)
            return creds
    except (json.JSONDecodeError, KeyError):
        pass

    # OAuth2 flow (original implementation)
    print("🔑 Using OAuth2 authentication")
    creds = None

    # Token file stores user's access and refresh tokens
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        token_path.write_text(creds.to_json())

    return creds


def get_document(service, document_id: str) -> Dict:
    """Retrieve Google Doc content"""
    try:
        document = service.documents().get(documentId=document_id).execute()
        return document
    except HttpError as error:
        print(f'❌ Error retrieving document: {error}')
        raise


def parse_edit_plan(edit_plan_path: Path) -> List[GoogleDocsEdit]:
    """Parse BATCHED_EDIT_PLAN.md into GoogleDocsEdit objects"""
    content = edit_plan_path.read_text()
    edits = []

    # Parse Batch 2: Terminology (find/replace) edits
    # These are the safest to apply via API

    current_batch = None
    current_edit_num = None
    find_text = None
    replace_text = None
    priority = None
    section = None

    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Match batch header: ## Batch 2: Terminology Find/Replace
        batch_match = re.match(r'^##\s+Batch\s+(\d+):\s+(.+)$', line)
        if batch_match:
            current_batch = int(batch_match.group(1))
            i += 1
            continue

        # Match edit header: ### Edit 1: Throughout
        edit_match = re.match(r'^###\s+Edit\s+(\d+):\s+(.+)$', line)
        if edit_match:
            current_edit_num = int(edit_match.group(1))
            section = edit_match.group(2)
            i += 1
            continue

        # Match priority: **Priority:** CRITICAL
        priority_match = re.match(r'\*\*Priority:\*\*\s+(\w+)', line)
        if priority_match:
            priority = priority_match.group(1)
            i += 1
            continue

        # Look for code blocks containing old/new text
        # Pattern: #### Old Text followed by ``` block
        if line == '#### Old Text':
            # Next line should be ```
            i += 1
            if i < len(lines) and lines[i].strip() == '```':
                # Collect text until closing ```
                i += 1
                text_lines = []
                while i < len(lines) and lines[i].strip() != '```':
                    text_lines.append(lines[i])
                    i += 1
                find_text = '\n'.join(text_lines).strip()
            i += 1
            continue

        if line == '#### Replace With':
            # Next line should be ```
            i += 1
            if i < len(lines) and lines[i].strip() == '```':
                # Collect text until closing ```
                i += 1
                text_lines = []
                while i < len(lines) and lines[i].strip() != '```':
                    text_lines.append(lines[i])
                    i += 1
                replace_text = '\n'.join(text_lines).strip()
            i += 1
            continue

        # Check if we have all components for Batch 2 (terminology) edits
        if (current_batch == 2 and find_text and replace_text and
            current_edit_num and section and priority):

            # Create edit for find/replace operations
            edits.append(GoogleDocsEdit(
                batch_num=current_batch,
                edit_num=current_edit_num,
                section=section,
                edit_type='replace_all',
                find_text=find_text,
                replace_text=replace_text,
                match_case=False,
                priority=priority
            ))

            # Reset for next edit
            find_text = None
            replace_text = None
            current_edit_num = None
            section = None
            priority = None

        i += 1

    return edits


def apply_batch_1_title(service, document_id: str, old_title: str, new_title: str, dry_run: bool = False) -> bool:
    """Apply Batch 1: Title replacement"""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Applying Batch 1: Title Replacement")
    print(f"  Old: {old_title}")
    print(f"  New: {new_title}")

    if dry_run:
        print("  ✓ Would replace title")
        return True

    try:
        requests = [{
            'replaceAllText': {
                'containsText': {
                    'text': old_title,
                    'matchCase': True
                },
                'replaceText': new_title
            }
        }]

        result = service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()

        print(f"  ✅ Title replaced")
        return True

    except HttpError as error:
        print(f'  ❌ Error: {error}')
        return False


def apply_batch_3_abstract(service, document_id: str, dry_run: bool = False) -> bool:
    """Apply Batch 3: Abstract replacement (0 citations, safe for API)"""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Applying Batch 3: Abstract Replacement")

    # Old abstract (after Batch 2 terminology replacements)
    old_abstract = """Abstract 242
Earth's biosphere is an interconnected and dynamic network of ecosystems, with microbes playing a significant role in the functioning of and relationships between ecosystems. Advances in microbial metagenomics have recently provided extensive data on microbial communities across ecosystems, including biological sequences, functional annotations, and taxonomy. Previously, global comparative studies of 16S amplicon sequencing have revealed a largely uncharacterized microbial diversity, with the geographic distribution of key taxa showing correlations with abiotic and biotic environmental features. We hypothesized that using diverse metagenome features, including sequence domains, functions, and taxa, could reveal traits discriminative for and thus characteristic of different ecosystems, including ones characteristic of in specific ecosystem contexts. Using the largest standardized metagenome sample collection across a wide array of ecosystems, we trained machine learning models to predict the source ecosystem for metagenome samples. We identified optimal metagenome features as well as model parameters for predicting ecosystem labels for metagenome samples, resulting in models that performed well in cross-validation. Training at different ecosystem classification levels improved performance for ecosystems with sparse training data. Using model feature permutation knockoff and importance analysis, we identified signature metagenome features for distinguishing 41 ecosystems, revealing traits that are characteristic of specific ecosystems. This collection of traits, which may have ecosystem-discriminative significance, reveals examples of direct linkages between microbial functions and environmental properties, highlights important unknown functions, and implies ecosystem relationships that align well with established classifications but exhibit relationships beyond what is currently appreciated."""

    # New abstract (from v2_final)
    new_abstract = """Abstract

Earth's biosphere is an interconnected and dynamic network of ecosystems, with microbes playing a significant role in ecosystem functioning and in mediating relationships between environments. Advances in microbial metagenomics have generated extensive data on microbial communities across ecosystems, including biological sequences, functional annotations, and taxonomy. Previous global comparative studies based largely on 16S amplicon sequencing revealed vast microbial diversity and correlations between taxa and environmental features but provided limited functional resolution and interpretability. Here, we hypothesized that integrating diverse metagenome features, including sequence domains, functional annotations, and taxa, could reveal features that discriminate among ecosystems and are therefore characteristic of different ecosystem contexts. Using a large, standardized collection of metagenome samples spanning a wide array of ecosystems, we trained interpretable machine learning models to predict the source ecosystem of metagenome samples. We identified feature representations and model parameters that achieved strong cross-validated performance while enabling systematic feature importance analysis. Using permutation knockoff and importance analyses, we identified a compact set of metagenome features that discriminate 41 ecosystems. These ecosystem-discriminative features highlight functional and taxonomic signals associated with specific environments, prioritize numerous uncharacterized protein domains, and reveal structured patterns of similarity among ecosystems that align with established classifications while extending beyond strictly hierarchical representations. Together, these results provide a scalable and transparent framework for organizing metagenomic data into interpretable feature sets and ecosystem relationships, generating testable hypotheses about microbial functional variation across Earth's ecosystems."""

    if dry_run:
        print("  ✓ Would replace Abstract section")
        print(f"  Old length: {len(old_abstract)} chars")
        print(f"  New length: {len(new_abstract)} chars")
        return True

    try:
        requests = [{
            'replaceAllText': {
                'containsText': {
                    'text': old_abstract,
                    'matchCase': False
                },
                'replaceText': new_abstract
            }
        }]

        result = service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()

        # Check if replacement happened
        reply = result.get('replies', [{}])[0]
        count = reply.get('replaceAllText', {}).get('occurrencesChanged', 0)

        if count > 0:
            print(f"  ✅ Abstract replaced ({count} occurrence)")
            return True
        else:
            print(f"  ⚠️ Abstract text not found - may already be updated")
            return False

    except HttpError as error:
        print(f'  ❌ Error: {error}')
        return False


def apply_edits(
    service,
    document_id: str,
    edits: List[GoogleDocsEdit],
    batches: Optional[List[int]] = None,
    dry_run: bool = False
) -> Tuple[int, int]:
    """
    Apply edits to Google Doc using batch API requests

    Returns:
        (successful_count, failed_count)
    """

    if batches:
        edits = [e for e in edits if e.batch_num in batches]

    if not edits:
        print("⚠️ No edits to apply")
        return 0, 0

    # Group edits by batch for safer application
    batches_dict = {}
    for edit in edits:
        if edit.batch_num not in batches_dict:
            batches_dict[edit.batch_num] = []
        batches_dict[edit.batch_num].append(edit)

    successful = 0
    failed = 0

    for batch_num in sorted(batches_dict.keys()):
        batch_edits = batches_dict[batch_num]
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Applying Batch {batch_num} ({len(batch_edits)} edits)")

        # Convert edits to API requests
        requests = [edit.to_request() for edit in batch_edits]

        if dry_run:
            for edit in batch_edits:
                print(f"  ✓ Would replace '{edit.find_text}' → '{edit.replace_text}'")
            successful += len(batch_edits)
            continue

        try:
            # Apply all edits in this batch atomically
            result = service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()

            # Check results
            for i, edit in enumerate(batch_edits):
                reply = result.get('replies', [])[i] if i < len(result.get('replies', [])) else {}
                replace_count = reply.get('replaceAllText', {}).get('occurrencesChanged', 0)

                if replace_count > 0:
                    print(f"  ✅ Edit {edit.edit_num}: Replaced {replace_count} occurrence(s)")
                    successful += 1
                else:
                    print(f"  ⚠️ Edit {edit.edit_num}: No occurrences found (may already be applied)")
                    successful += 1  # Count as success if text not found

        except HttpError as error:
            print(f'  ❌ Batch {batch_num} failed: {error}')
            failed += len(batch_edits)

    return successful, failed


def verify_edits(service, document_id: str, forbidden_terms: List[str]) -> Dict[str, int]:
    """Verify that forbidden terms have been removed"""
    print("\n🔍 Verifying edits...")

    # Get updated document
    doc = get_document(service, document_id)

    # Extract all text
    content = extract_text_from_doc(doc)

    # Check for forbidden terms
    remaining = {}
    for term in forbidden_terms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        count = len(pattern.findall(content))
        if count > 0:
            remaining[term] = count

    if remaining:
        print("❌ Forbidden terms still present:")
        for term, count in remaining.items():
            print(f"   - '{term}': {count} occurrence(s)")
    else:
        print("✅ All forbidden terms removed!")

    return remaining


def extract_text_from_doc(doc: Dict) -> str:
    """Extract plain text from Google Doc structure"""
    content = doc.get('body', {}).get('content', [])
    text_parts = []

    def extract_from_element(element):
        if 'paragraph' in element:
            para = element['paragraph']
            for elem in para.get('elements', []):
                if 'textRun' in elem:
                    text_parts.append(elem['textRun'].get('content', ''))
        elif 'table' in element:
            table = element['table']
            for row in table.get('tableRows', []):
                for cell in row.get('tableCells', []):
                    for cell_content in cell.get('content', []):
                        extract_from_element(cell_content)

    for element in content:
        extract_from_element(element)

    return ''.join(text_parts)


def main():
    parser = argparse.ArgumentParser(
        description="Apply batched edits to Google Doc via API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Dry run (preview changes)
    python scripts/apply_gdoc_edits.py \\
        --document-id 1ABC...XYZ \\
        --edit-plan manuscript/kbaseeco_v2/BATCHED_EDIT_PLAN.md \\
        --dry-run

    # Apply Batch 1 and 2 only (title + terminology)
    python scripts/apply_gdoc_edits.py \\
        --document-id 1ABC...XYZ \\
        --edit-plan manuscript/kbaseeco_v2/BATCHED_EDIT_PLAN.md \\
        --batch 1,2

    # Apply all batches
    python scripts/apply_gdoc_edits.py \\
        --document-id 1ABC...XYZ \\
        --edit-plan manuscript/kbaseeco_v2/BATCHED_EDIT_PLAN.md \\
        --batch 1,2,3,4,5,6,7
        """
    )

    parser.add_argument(
        '--document-id',
        type=str,
        required=True,
        help="Google Doc ID (from URL: docs.google.com/document/d/DOC_ID/edit)"
    )
    parser.add_argument(
        '--edit-plan',
        type=Path,
        required=True,
        help="Path to BATCHED_EDIT_PLAN.md"
    )
    parser.add_argument(
        '--credentials',
        type=Path,
        default=Path('credentials.json'),
        help="Path to Google OAuth2 credentials.json (default: credentials.json)"
    )
    parser.add_argument(
        '--token',
        type=Path,
        default=Path('token.json'),
        help="Path to store OAuth2 token (default: token.json)"
    )
    parser.add_argument(
        '--batch',
        type=str,
        help="Comma-separated batch numbers to apply (e.g., '1,2' or '1,2,3,4,5,6,7')"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Preview changes without applying them"
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help="Only verify that forbidden terms are removed (no edits)"
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.edit_plan.exists():
        raise FileNotFoundError(f"Edit plan not found: {args.edit_plan}")

    if not args.verify_only and not args.credentials.exists():
        raise FileNotFoundError(
            f"Credentials file not found: {args.credentials}\n"
            f"Please download OAuth2 credentials from Google Cloud Console"
        )

    # Parse batch numbers
    batch_nums = None
    if args.batch:
        batch_nums = [int(b.strip()) for b in args.batch.split(',')]

    # Authenticate
    print("🔐 Authenticating with Google Docs API...")
    creds = authenticate_gdocs(args.credentials, args.token)
    service = build('docs', 'v1', credentials=creds)

    # Get document info
    print(f"\n📄 Opening document: {args.document_id}")
    doc = get_document(service, args.document_id)
    print(f"   Title: {doc.get('title', 'Unknown')}")

    # Verify only mode
    if args.verify_only:
        forbidden_terms = ['adaptive significance', 'essential for survival', 'selection']
        verify_edits(service, args.document_id, forbidden_terms)
        return

    # Parse edit plan
    print(f"\n📋 Parsing edit plan: {args.edit_plan}")
    edits = parse_edit_plan(args.edit_plan)
    print(f"   Found {len(edits)} edits")

    if batch_nums:
        filtered = [e for e in edits if e.batch_num in batch_nums]
        print(f"   Filtered to {len(filtered)} edits from batches: {batch_nums}")

    # Special handling for Batch 1 (title)
    if batch_nums is None or 1 in batch_nums:
        old_title = "Towards a Global Atlas of Adaptive Microbial Traits"
        new_title = "Towards a Global Atlas of Adaptive Microbial Traits: Uncovering Characteristic Traits of Earth's Microbiomes"
        apply_batch_1_title(service, args.document_id, old_title, new_title, args.dry_run)

    # Special handling for Batch 2 (terminology - hardcoded for reliability)
    if batch_nums is None or 2 in batch_nums:
        batch_2_edits = [
            GoogleDocsEdit(2, 1, "Throughout", "replace_all", "adaptive significance",
                          "ecosystem-discriminative significance", False, "CRITICAL"),
            GoogleDocsEdit(2, 2, "Throughout", "replace_all", "essential for survival",
                          "characteristic of", False, "CRITICAL"),
            GoogleDocsEdit(2, 3, "Throughout", "replace_all", "selection",
                          "enrichment", False, "CRITICAL"),
        ]
        successful_b2, failed_b2 = apply_edits(service, args.document_id, batch_2_edits, [2], args.dry_run)
        successful = successful_b2
        failed = failed_b2
    else:
        successful = 0
        failed = 0

    # Special handling for Batch 3 (Abstract - 0 citations, safe for API)
    if batch_nums is None or 3 in batch_nums:
        batch_3_success = apply_batch_3_abstract(service, args.document_id, args.dry_run)
        successful += 1 if batch_3_success else 0
        failed += 0 if batch_3_success else 1

    # Apply edits (Batch 4+) - parsed from file
    if batch_nums and not any(b in [1, 2, 3] for b in batch_nums):
        successful_other, failed_other = apply_edits(service, args.document_id, edits, batch_nums, args.dry_run)
        successful += successful_other
        failed += failed_other

    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Summary:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")

    if not args.dry_run and successful > 0:
        # Verify forbidden terms removed
        forbidden_terms = ['adaptive significance', 'essential for survival', 'selection']
        verify_edits(service, args.document_id, forbidden_terms)

        print(f"\n🔗 View document: https://docs.google.com/document/d/{args.document_id}/edit")
    elif args.dry_run:
        print(f"\n💡 Run without --dry-run to apply changes")

    print(f"{'='*60}")


if __name__ == '__main__':
    main()
