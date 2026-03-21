#!/usr/bin/env python3
"""
Find and insert the missing Para 13 citation by analyzing document structure.
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

    print("🔑 Using service account authentication")
    return service_account.Credentials.from_service_account_file(
        str(credentials_path), scopes=SCOPES)

def find_and_insert_para13_citation(document_id: str, credentials_path: Path):
    """Find Para 13 and insert the Kim et al. citation"""

    creds = authenticate_gdocs(credentials_path)
    service = build('docs', 'v1', credentials=creds)

    print(f"📄 Retrieving document...")
    doc = service.documents().get(documentId=document_id).execute()
    print(f"✓ Document: {doc.get('title')}")

    content = doc.get('body', {}).get('content', [])

    # Search for paragraph containing "Zhao" citation
    print(f"\n🔍 Searching for paragraph with Zhao citation...")

    target_para = None
    insert_index = None

    for element in content:
        if 'paragraph' not in element:
            continue

        para = element['paragraph']
        para_text = ''

        # Reconstruct paragraph text
        for elem in para.get('elements', []):
            if 'textRun' in elem:
                para_text += elem['textRun'].get('content', '')

        # Check if this is the target paragraph (contains key phrases)
        if ('Microbial communities are central' in para_text and
            'Zhao' in para_text):

            target_para = para_text
            insert_index = element.get('endIndex', 0) - 1

            print(f"✓ Found target paragraph!")
            print(f"  Text preview: {para_text[:100]}...")
            print(f"  End text: ...{para_text[-100:]}")
            print(f"  Insert index: {insert_index}")
            break

    if not insert_index:
        print("❌ Could not find target paragraph")
        return 1

    # Prepare the citation text to insert
    citation_text = " Recent work has revealed planetary-scale patterns in microbiome structure across disparate habitats, highlighting the interconnectedness of microbial communities across Earth's ecosystems (Kim et al., 2026)."

    print(f"\n📝 Inserting citation:")
    print(f"  {citation_text[:80]}...")

    # Create insert request
    requests = [{
        'insertText': {
            'location': {'index': insert_index},
            'text': citation_text
        }
    }]

    # Apply the change
    try:
        result = service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()

        print(f"\n✅ Success! Citation inserted at index {insert_index}")
        print(f"\n📄 View document:")
        print(f"   https://docs.google.com/document/d/{document_id}/edit")

        return 0

    except Exception as error:
        print(f"❌ Error: {error}")
        return 1

if __name__ == '__main__':
    document_id = '1gwjtHp863cFv61rJ3gd7l2RGje6tQy6he3bC8YFBuSU'
    credentials_path = Path('credentials.json')

    exit(find_and_insert_para13_citation(document_id, credentials_path))
