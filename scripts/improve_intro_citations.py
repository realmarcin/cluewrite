#!/usr/bin/env python3
"""
Improve Introduction Para 13 and 14 citations for better integration.
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

def improve_intro_citations(document_id: str, credentials_path: Path):
    """Improve Para 13 and 14 citations"""

    creds = authenticate_gdocs(credentials_path)
    service = build('docs', 'v1', credentials=creds)

    print(f"✨ Improving Introduction citations...")

    requests = []

    # ========================================================================
    # Para 13: Strengthen Kim et al. citation
    # ========================================================================
    print(f"\n📝 Para 13: Strengthening Kim et al. citation...")

    old_text_13 = "Recent work has revealed planetary-scale patterns in microbiome structure across disparate habitats, highlighting the interconnectedness of microbial communities across Earth's ecosystems (Kim et al., 2026)."

    new_text_13 = "Recent work has revealed planetary-scale patterns in microbiome structure across disparate habitats (Kim et al., 2026), demonstrating that while certain microbial taxa are habitat specialists, generalist taxa drive gene flow across environments. Understanding which metagenomic features consistently discriminate ecosystems—despite this cross-habitat gene flow—remains a fundamental challenge."

    requests.append({
        'replaceAllText': {
            'containsText': {
                'text': old_text_13,
                'matchCase': False
            },
            'replaceText': new_text_13
        }
    })

    print(f"   ✓ Will add context about generalists vs specialists")
    print(f"   ✓ Will connect to research question")

    # ========================================================================
    # Para 14: Strengthen MicrobeAtlas citation
    # ========================================================================
    print(f"\n📝 Para 14: Strengthening MicrobeAtlas citation...")

    old_text_14 = "Global microbiome databases such as MicrobeAtlas (Rodrigues et al., 2025) provide comprehensive resources for understanding ecosystem-level patterns across diverse environments."

    new_text_14 = "Global microbiome databases such as MicrobeAtlas (Rodrigues et al., 2025), which aggregates metagenomic data across diverse Earth ecosystems with standardized metadata, provide comprehensive resources for identifying ecosystem-level patterns. Yet, identifying which specific metagenomic features drive ecosystem discrimination across this global diversity remains an open question."

    requests.append({
        'replaceAllText': {
            'containsText': {
                'text': old_text_14,
                'matchCase': False
            },
            'replaceText': new_text_14
        }
    })

    print(f"   ✓ Will explain what MicrobeAtlas is")
    print(f"   ✓ Will transition to your research gap")

    # Apply changes
    print(f"\n🚀 Applying improvements...")

    try:
        result = service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()

        print(f"\n✅ Success! Introduction improved")
        print(f"\n📊 Changes made:")
        print(f"   • Para 13: Added context about generalists/specialists")
        print(f"   • Para 13: Connected Kim et al. to your research challenge")
        print(f"   • Para 14: Explained MicrobeAtlas database contents")
        print(f"   • Para 14: Set up your research question")
        print(f"\n📄 View document:")
        print(f"   https://docs.google.com/document/d/{document_id}/edit")

        return 0

    except Exception as error:
        print(f"❌ Error: {error}")
        return 1

if __name__ == '__main__':
    document_id = '1gwjtHp863cFv61rJ3gd7l2RGje6tQy6he3bC8YFBuSU'
    credentials_path = Path('credentials.json')
    exit(improve_intro_citations(document_id, credentials_path))
