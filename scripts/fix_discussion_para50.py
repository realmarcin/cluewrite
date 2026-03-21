#!/usr/bin/env python3
"""
Fix the broken Discussion Para 50 by replacing the mangled text with proper revision.
"""

import json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/documents']

def authenticate_gdocs(credentials_path: Path):
    """Authenticate with Google Docs API"""
    with open(credentials_path, 'r') as f:
        cred_data = json.load(f)
    return service_account.Credentials.from_service_account_file(
        str(credentials_path), scopes=SCOPES)

def fix_discussion_para50(document_id: str, credentials_path: Path):
    """Fix the broken Discussion Para 50"""

    creds = authenticate_gdocs(credentials_path)
    service = build('docs', 'v1', credentials=creds)

    print(f"🔧 Fixing Discussion Para 50...")

    # The broken text to find and replace
    broken_text = "how they reveal p Our ecosystem classification approach complements recent findings on planetary-scale microbiome structure (Kim et al., 2026) and leverages resources such as the MicrobeAtlas database (Rodrigues et al., 2025) to provide context for ecosystem-level patterns across diverse environments.atterns of ecosystem similarity"

    # The corrected text
    fixed_text = """how they reveal patterns of ecosystem similarity, how model misclassifications expose informative structure, and how this approach prioritizes uncharacterized functions for further investigation.

Our ecosystem classification approach complements recent findings on planetary-scale microbiome structure (Kim et al., 2026), which demonstrate how microbial communities show both habitat specialization and generalist-driven gene flow across Earth's diverse environments. By leveraging resources such as the MicrobeAtlas database (Rodrigues et al., 2025), our framework provides context for understanding which metagenomic features consistently discriminate ecosystems at a global scale. While Kim et al. revealed patterns"""

    requests = [{
        'replaceAllText': {
            'containsText': {
                'text': broken_text,
                'matchCase': False
            },
            'replaceText': fixed_text
        }
    }]

    print(f"📝 Replacing broken text...")
    print(f"   Find: ...reveal p Our ecosystem...atterns...")
    print(f"   Replace with: ...reveal patterns...Our ecosystem (new paragraph)...")

    try:
        result = service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()

        print(f"\n✅ Success! Para 50 fixed")
        print(f"   - Removed broken sentence")
        print(f"   - Added proper paragraph break")
        print(f"   - Strengthened Kim et al. citation context")
        print(f"\n📄 View document:")
        print(f"   https://docs.google.com/document/d/{document_id}/edit")

        return 0

    except Exception as error:
        print(f"❌ Error: {error}")
        return 1

if __name__ == '__main__':
    document_id = '1gwjtHp863cFv61rJ3gd7l2RGje6tQy6he3bC8YFBuSU'
    credentials_path = Path('credentials.json')
    exit(fix_discussion_para50(document_id, credentials_path))
