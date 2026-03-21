#!/usr/bin/env python3
"""
Insert critical citations into Google Doc at specific locations.

Uses Google Docs API to insert citations in Introduction, Discussion, and References.
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict

from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/documents']


def authenticate_gdocs(credentials_path: Path) -> Credentials:
    """Authenticate with Google Docs API"""
    try:
        with open(credentials_path, 'r') as f:
            cred_data = json.load(f)

        if cred_data.get('type') == 'service_account':
            print("🔑 Using service account authentication")
            return service_account.Credentials.from_service_account_file(
                str(credentials_path), scopes=SCOPES)
    except (json.JSONDecodeError, KeyError):
        pass

    # OAuth2 flow
    print("🔑 Using OAuth2 authentication")
    token_path = Path('token.json')

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        if creds and creds.valid:
            return creds

    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
    creds = flow.run_local_server(port=0)

    with open(token_path, 'w') as token:
        token.write(creds.to_json())

    return creds


def get_document(service, document_id: str) -> Dict:
    """Retrieve the document structure"""
    try:
        doc = service.documents().get(documentId=document_id).execute()
        return doc
    except HttpError as error:
        print(f"❌ Error retrieving document: {error}")
        return None


def find_text_index(doc: Dict, search_text: str) -> int:
    """Find the index of text in the document"""
    content = doc.get('body', {}).get('content', [])

    for element in content:
        if 'paragraph' in element:
            para = element['paragraph']
            para_text = ''
            start_index = element.get('startIndex', 0)

            for elem in para.get('elements', []):
                if 'textRun' in elem:
                    para_text += elem['textRun'].get('content', '')

            if search_text in para_text:
                # Return end index of paragraph
                return element.get('endIndex', 0)

    return None


def insert_citations(document_id: str, credentials_path: Path, dry_run: bool = False):
    """Insert critical citations into the Google Doc"""

    creds = authenticate_gdocs(credentials_path)
    service = build('docs', 'v1', credentials=creds)

    print(f"📄 Retrieving document structure...")
    doc = get_document(service, document_id)
    if not doc:
        return 1

    print(f"✓ Document: {doc.get('title', 'Unknown')}")

    # Define citations to insert
    insertions = [
        {
            'location': 'intro_para13',
            'search_text': '(Zhao et al. 2022).',
            'insert_text': ' Recent work has revealed planetary-scale patterns in microbiome structure across disparate habitats, highlighting the interconnectedness of microbial communities across Earth\'s ecosystems (Kim et al., 2026).',
            'priority': 'CRITICAL'
        },
        {
            'location': 'intro_para14',
            'search_text': 'many ecosystems, feature types, and studies are considered simultaneously.',
            'insert_text': ' Global microbiome databases such as MicrobeAtlas (Rodrigues et al., 2025) provide comprehensive resources for understanding ecosystem-level patterns across diverse environments.',
            'priority': 'CRITICAL'
        },
        {
            'location': 'discussion_para50',
            'search_text': 'providing a basis for hypothesis generation about microbial functional variation.',
            'insert_text': ' Our ecosystem classification approach complements recent findings on planetary-scale microbiome structure (Kim et al., 2026) and leverages resources such as the MicrobeAtlas database (Rodrigues et al., 2025) to provide context for ecosystem-level patterns across diverse environments.',
            'priority': 'CRITICAL'
        }
    ]

    # Prepare batch requests
    requests = []

    for insertion in insertions:
        print(f"\n🔍 Searching for: {insertion['location']}")
        print(f"   Text: {insertion['search_text'][:80]}...")

        # Find the index
        index = find_text_index(doc, insertion['search_text'])

        if index is None:
            print(f"   ⚠️  Text not found, skipping")
            continue

        print(f"   ✓ Found at index {index}")
        print(f"   📝 Will insert: {insertion['insert_text'][:80]}...")

        # Create insert request
        request = {
            'insertText': {
                'location': {'index': index - 1},  # Insert before paragraph end
                'text': insertion['insert_text']
            }
        }
        requests.append(request)

    # Add references at end
    print(f"\n📚 Adding references to References section...")

    references_text = """

Kim, C. Y., Podlesny, D., Schiller, J., Khedkar, S., Fullam, A., Orakov, A., Schudoma, C., Robbani, S. M., Grekova, A., et al. (2026). Planetary microbiome structure and generalist-driven gene flow across disparate habitats. Cell. https://doi.org/10.1016/j.cell.2025.12.051

Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. Advances in Neural Information Processing Systems, 30. https://arxiv.org/abs/1705.07874

Prokhorenkova, L., Gusev, G., Vorobev, A., Dorogush, A. V., & Gulin, A. (2018). CatBoost: unbiased boosting with categorical features. Advances in Neural Information Processing Systems, 31.

Rodrigues, J. F. M., Tackmann, J., Malfertheiner, L., Patsch, D., Perez-Molphe-Montoya, E., Nägele, T., et al. (2025). The MicrobeAtlas database: Global trends and insights into Earth's microbial ecosystems. bioRxiv. https://doi.org/10.1101/2025.07.18.665519
"""

    # Find end of document (before last paragraph)
    content = doc.get('body', {}).get('content', [])
    end_index = content[-1].get('endIndex', 1) - 1

    requests.append({
        'insertText': {
            'location': {'index': end_index},
            'text': references_text
        }
    })

    print(f"\n📊 Summary:")
    print(f"   Total insertions: {len(requests)}")
    print(f"   - Introduction: 2 citations")
    print(f"   - Discussion: 1 citation")
    print(f"   - References: 4 new entries")

    if dry_run:
        print(f"\n⚠️  DRY RUN - No changes made")
        print(f"\nTo apply changes, run without --dry-run flag")
        return 0

    # Apply changes
    print(f"\n🚀 Applying changes...")

    try:
        result = service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()

        print(f"✅ Success! Applied {len(requests)} edits")
        print(f"\n📄 View document:")
        print(f"   https://docs.google.com/document/d/{document_id}/edit")

        return 0

    except HttpError as error:
        print(f"❌ Error applying edits: {error}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='Insert critical citations into Google Doc'
    )
    parser.add_argument(
        '--document-id',
        required=True,
        help='Google Doc ID'
    )
    parser.add_argument(
        '--credentials',
        type=Path,
        default=Path('credentials.json'),
        help='Path to credentials.json'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be inserted without making changes'
    )

    args = parser.parse_args()

    if not args.credentials.exists():
        print(f"❌ Credentials file not found: {args.credentials}")
        return 1

    return insert_citations(args.document_id, args.credentials, args.dry_run)


if __name__ == '__main__':
    exit(main())
