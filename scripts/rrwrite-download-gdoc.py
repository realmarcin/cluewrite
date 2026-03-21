#!/usr/bin/env python3
"""
Download Google Doc as DOCX format with metadata extraction.

Extends existing Google Docs API authentication patterns to support
document export functionality via Drive API.

Usage:
    python scripts/rrwrite-download-gdoc.py \
        --document-id 1ABC...XYZ \
        --output manuscript.docx \
        --credentials credentials.json
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# Extended scopes: Docs (read) + Drive (export)
SCOPES = [
    'https://www.googleapis.com/auth/documents.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]


def authenticate_gdocs(credentials_path: Path, token_path: Path) -> Credentials:
    """Authenticate with Google Docs/Drive API (supports OAuth2 and Service Account)"""

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


def get_document_metadata(docs_service, document_id: str) -> Dict:
    """Retrieve Google Doc metadata"""
    try:
        document = docs_service.documents().get(documentId=document_id).execute()
        return {
            'title': document.get('title', 'Untitled'),
            'document_id': document_id,
            'revision_id': document.get('revisionId', 'unknown'),
            'retrieved_at': datetime.now().isoformat()
        }
    except HttpError as error:
        print(f'❌ Error retrieving document metadata: {error}')
        raise


def export_document_as_docx(
    drive_service,
    document_id: str,
    output_path: Path
) -> None:
    """Export Google Doc as DOCX format"""
    try:
        # Request export as DOCX
        request = drive_service.files().export_media(
            fileId=document_id,
            mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

        # Download to file
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"📥 Download progress: {progress}%", end='\r')

        print(f"\n✓ Document exported: {output_path}")
        print(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")

    except HttpError as error:
        print(f'❌ Error exporting document: {error}')
        raise


def save_metadata(metadata: Dict, output_path: Path) -> None:
    """Save document metadata as JSON"""
    metadata_path = output_path.with_suffix('.metadata.json')

    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"✓ Metadata saved: {metadata_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Download Google Doc as DOCX with metadata extraction',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--document-id',
        required=True,
        help='Google Doc document ID (from URL)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output DOCX file path'
    )
    parser.add_argument(
        '--credentials',
        type=Path,
        default=Path('credentials.json'),
        help='Google API credentials file (default: credentials.json)'
    )
    parser.add_argument(
        '--token',
        type=Path,
        default=Path.home() / '.gdocs_token.json',
        help='OAuth2 token cache file (default: ~/.gdocs_token.json)'
    )
    parser.add_argument(
        '--save-metadata',
        action='store_true',
        help='Save document metadata as JSON'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Validate credentials file
    if not args.credentials.exists():
        print(f"❌ Error: Credentials file not found: {args.credentials}", file=sys.stderr)
        print("\nTo set up Google Docs API:", file=sys.stderr)
        print("1. Visit https://console.cloud.google.com/", file=sys.stderr)
        print("2. Enable Google Docs API + Google Drive API", file=sys.stderr)
        print("3. Create OAuth2 credentials or Service Account", file=sys.stderr)
        print("4. Download credentials.json", file=sys.stderr)
        return 1

    try:
        # Authenticate
        creds = authenticate_gdocs(args.credentials, args.token)

        # Build API clients
        docs_service = build('docs', 'v1', credentials=creds)
        drive_service = build('drive', 'v3', credentials=creds)

        # Get document metadata
        if args.verbose:
            print(f"📄 Retrieving document metadata...")

        metadata = get_document_metadata(docs_service, args.document_id)

        if args.verbose:
            print(f"  Title: {metadata['title']}")
            print(f"  Revision: {metadata['revision_id']}")

        # Export as DOCX
        print(f"📥 Downloading Google Doc as DOCX...")
        export_document_as_docx(drive_service, args.document_id, args.output)

        # Save metadata
        if args.save_metadata:
            save_metadata(metadata, args.output)

        print(f"\n✅ Success!")
        print(f"  Document: {metadata['title']}")
        print(f"  Output: {args.output}")

        return 0

    except HttpError as error:
        print(f"\n❌ Google API error: {error}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
