# Google Docs API Setup Guide

Guide for using `apply_gdoc_edits.py` to programmatically edit Google Docs while preserving Paperpile citation links.

## Prerequisites

### 1. Install Python Dependencies

```bash
pip install -r requirements-gdocs.txt
```

Or manually:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Set Up Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable **Google Docs API**:
   - Navigate to "APIs & Services" → "Library"
   - Search for "Google Docs API"
   - Click "Enable"

### 3. Create OAuth2 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "+ CREATE CREDENTIALS" → "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - User Type: **External** (for testing)
   - App name: "RRWrite Google Docs Editor"
   - User support email: your email
   - Developer contact: your email
   - Scopes: Add `https://www.googleapis.com/auth/documents`
   - Test users: Add your Google account email
4. Create OAuth client ID:
   - Application type: **Desktop app**
   - Name: "RRWrite Desktop Client"
5. Download credentials:
   - Click the download button (⬇) next to your client ID
   - Save as `credentials.json` in the rrwrite root directory

### 4. Get Your Google Doc ID

From your Google Doc URL:
```
https://docs.google.com/document/d/1AbC123XyZ.../edit
                                    ^^^^^^^^^
                                    This is your DOC_ID
```

## Usage

### Step 1: Dry Run (Preview Changes)

**Recommended first step** - preview all changes without applying:

```bash
python scripts/apply_gdoc_edits.py \
    --document-id YOUR_DOC_ID \
    --edit-plan manuscript/kbaseeco_v2/BATCHED_EDIT_PLAN.md \
    --dry-run
```

First run will:
1. Open browser for Google authentication
2. Ask you to authorize the app
3. Save token to `token.json` for future use

### Step 2: Apply Safe Edits (Batches 1-2)

Apply **only** the title and terminology find/replace edits (Paperpile-safe):

```bash
python scripts/apply_gdoc_edits.py \
    --document-id YOUR_DOC_ID \
    --edit-plan manuscript/kbaseeco_v2/BATCHED_EDIT_PLAN.md \
    --batch 1,2
```

This applies:
- **Batch 1**: Title replacement
- **Batch 2**: Terminology find/replace (3 forbidden terms)

### Step 3: Verify Edits

Check that forbidden terms were removed:

```bash
python scripts/apply_gdoc_edits.py \
    --document-id YOUR_DOC_ID \
    --edit-plan manuscript/kbaseeco_v2/BATCHED_EDIT_PLAN.md \
    --verify-only
```

Expected output:
```
✅ All forbidden terms removed!
```

### Step 4: Manual Verification

1. Open the Google Doc
2. Check that:
   - Title has subtitle added
   - "adaptive significance" → "ecosystem-discriminative significance"
   - "essential for survival" → "characteristic of"
   - "selection" → "enrichment"
3. **Verify Paperpile citations still work** (click a citation link)

## Current Limitations

The current implementation handles:
- ✅ **Batch 1**: Title replacement
- ✅ **Batch 2**: Terminology find/replace (safe, preserves all formatting/links)
- ⚠️ **Batches 3-7**: Paragraph replacements (NOT YET IMPLEMENTED via API)

### Why Batches 3-7 Are Not Implemented

Paragraph-level replacements in Google Docs API are complex because:
1. Text positions shift after each edit
2. Preserving rich text formatting requires complex API calls
3. Paperpile links are stored as named ranges that need special handling
4. Risk of breaking citations is higher

### Recommended Approach for Batches 3-7

**Option 1: Manual Copy-Paste** (Safest for Paperpile)
- Use `BATCHED_EDIT_PLAN.md` as a guide
- Manually find and replace paragraphs
- Verify citations after each replacement

**Option 2: Extend API Script** (Advanced)
- Implement paragraph replacement using `DeleteContentRange` + `InsertText`
- Handle named ranges for Paperpile links
- Requires understanding Google Docs API structure

## Troubleshooting

### "Error: credentials.json not found"

Download OAuth2 credentials from Google Cloud Console (see Setup step 3).

### "Error: The caller does not have permission"

1. Check that Google Docs API is enabled
2. Verify you're logged in with correct Google account
3. Check document sharing settings (you must have edit access)

### "No occurrences found" Warning

This is normal if:
- Text was already replaced in a previous run
- Text differs slightly from edit plan (whitespace, formatting)

Run `--verify-only` to check if forbidden terms remain.

### Authentication Issues

Delete `token.json` and re-authenticate:
```bash
rm token.json
python scripts/apply_gdoc_edits.py --document-id YOUR_DOC_ID ...
```

## Security Notes

- `credentials.json`: OAuth2 client credentials (safe to commit if public project)
- `token.json`: Contains your access token (DO NOT COMMIT - add to .gitignore)
- Scopes: Only requests `documents` scope (read/write Google Docs)

## Example: Complete Workflow

```bash
# 1. Install dependencies
pip install -r requirements-gdocs.txt

# 2. Set up credentials (one-time)
# - Download credentials.json from Google Cloud Console
# - Place in rrwrite root directory

# 3. Dry run (preview)
python scripts/apply_gdoc_edits.py \
    --document-id 1AbC123XyZ \
    --edit-plan manuscript/kbaseeco_v2/BATCHED_EDIT_PLAN.md \
    --dry-run

# 4. Apply safe edits (title + terminology)
python scripts/apply_gdoc_edits.py \
    --document-id 1AbC123XyZ \
    --edit-plan manuscript/kbaseeco_v2/BATCHED_EDIT_PLAN.md \
    --batch 1,2

# 5. Verify
python scripts/apply_gdoc_edits.py \
    --document-id 1AbC123XyZ \
    --edit-plan manuscript/kbaseeco_v2/BATCHED_EDIT_PLAN.md \
    --verify-only

# 6. Manually apply Batches 3-7 using BATCHED_EDIT_PLAN.md
```

## Next Steps

After running this script:
1. ✅ Batches 1-2 applied automatically (title + terminology)
2. 📋 Use `BATCHED_EDIT_PLAN.md` to manually apply Batches 3-7 (paragraph edits)
3. 🔍 Final verification with `--verify-only`
4. 🎉 Google Doc aligned with v2_final!
