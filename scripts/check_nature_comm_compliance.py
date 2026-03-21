#!/usr/bin/env python3
"""
Check manuscript compliance with Nature Communications requirements
"""

import re
from pathlib import Path

# Nature Communications requirements
NATURE_COMM_REQUIREMENTS = {
    'main_text_max': 5000,  # Introduction + Results + Discussion
    'abstract_min': 150,
    'abstract_max': 200,
    'title_words_max': 20,
    'methods_no_limit': True,
    'figures_tables_max': 8,
    'references_typical': 100,
}


def count_words(text):
    """Count words in text"""
    # Remove citations like [Author2020]
    text = re.sub(r'\[[\w\s,\.]+\d{4}[a-z]?\]', '', text)
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove markdown formatting
    text = re.sub(r'[*_#`]', '', text)
    # Count words
    words = text.split()
    return len(words)


def extract_section(content, section_name):
    """Extract section content"""
    # Try single # first (main sections), then ## (subsections)
    pattern = rf'^#\s+{section_name}[^\n]*\n+(.*?)(?=\n#[^#]|\Z)'
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE | re.MULTILINE)
    if not match:
        pattern = rf'^##\s+{section_name}[^\n]*\n+(.*?)(?=\n##[^#]|\Z)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else ""


def extract_title(content):
    """Extract title"""
    match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    return match.group(1).strip() if match else ""


def count_figures_tables(content):
    """Count figure and table references"""
    # Count unique figure references
    figures = set(re.findall(r'Figure\s+(\d+)', content, re.IGNORECASE))
    # Count unique table references
    tables = set(re.findall(r'Table\s+(\d+)', content, re.IGNORECASE))
    return len(figures), len(tables)


def count_references(content):
    """Count citations"""
    # Count unique citations in format [Author2020] or (Author et al. 2020)
    citations = set(re.findall(r'\[[\w\s,]+\d{4}[a-z]?\]', content))
    citations.update(re.findall(r'\([\w\s,]+et al\.\s+\d{4}[a-z]?\)', content))
    return len(citations)


def check_manuscript(manuscript_path):
    """Check manuscript against Nature Communications requirements"""

    content = Path(manuscript_path).read_text()

    print(f"\n{'='*80}")
    print(f"NATURE COMMUNICATIONS COMPLIANCE CHECK")
    print(f"{'='*80}\n")

    # Title
    title = extract_title(content)
    title_words = count_words(title)
    print(f"📄 TITLE ({title_words} words)")
    print(f"   {title[:80]}...")
    print(f"   Requirement: ≤{NATURE_COMM_REQUIREMENTS['title_words_max']} words")
    if title_words <= NATURE_COMM_REQUIREMENTS['title_words_max']:
        print(f"   ✅ PASS")
    else:
        print(f"   ⚠️  EXCEEDS by {title_words - NATURE_COMM_REQUIREMENTS['title_words_max']} words")

    # Abstract
    abstract = extract_section(content, 'Abstract')
    abstract_words = count_words(abstract)
    print(f"\n📝 ABSTRACT ({abstract_words} words)")
    print(f"   Requirement: {NATURE_COMM_REQUIREMENTS['abstract_min']}-{NATURE_COMM_REQUIREMENTS['abstract_max']} words")
    if NATURE_COMM_REQUIREMENTS['abstract_min'] <= abstract_words <= NATURE_COMM_REQUIREMENTS['abstract_max']:
        print(f"   ✅ PASS")
    elif abstract_words < NATURE_COMM_REQUIREMENTS['abstract_min']:
        print(f"   ⚠️  TOO SHORT by {NATURE_COMM_REQUIREMENTS['abstract_min'] - abstract_words} words")
    else:
        print(f"   ⚠️  TOO LONG by {abstract_words - NATURE_COMM_REQUIREMENTS['abstract_max']} words")

    # Main text sections
    intro = extract_section(content, 'Introduction')
    results = extract_section(content, 'Results')
    discussion = extract_section(content, 'Discussion')

    intro_words = count_words(intro)
    results_words = count_words(results)
    discussion_words = count_words(discussion)
    main_text_words = intro_words + results_words + discussion_words

    print(f"\n📊 MAIN TEXT (Introduction + Results + Discussion)")
    print(f"   Introduction:  {intro_words:5,} words")
    print(f"   Results:       {results_words:5,} words")
    print(f"   Discussion:    {discussion_words:5,} words")
    print(f"   {'─'*40}")
    print(f"   TOTAL:         {main_text_words:5,} words")
    print(f"   Requirement: ≤{NATURE_COMM_REQUIREMENTS['main_text_max']:,} words")

    if main_text_words <= NATURE_COMM_REQUIREMENTS['main_text_max']:
        remaining = NATURE_COMM_REQUIREMENTS['main_text_max'] - main_text_words
        print(f"   ✅ PASS ({remaining:,} words remaining)")
    else:
        excess = main_text_words - NATURE_COMM_REQUIREMENTS['main_text_max']
        print(f"   ❌ EXCEEDS by {excess:,} words ({excess/main_text_words*100:.1f}% over)")

    # Methods
    methods = extract_section(content, 'Methods')
    methods_words = count_words(methods)
    print(f"\n🔬 METHODS ({methods_words:,} words)")
    print(f"   Note: No strict limit for Methods")

    # Figures and Tables
    num_figures, num_tables = count_figures_tables(content)
    total_figs_tables = num_figures + num_tables
    print(f"\n📈 FIGURES & TABLES")
    print(f"   Figures: {num_figures}")
    print(f"   Tables:  {num_tables}")
    print(f"   Total:   {total_figs_tables}")
    print(f"   Requirement: ≤{NATURE_COMM_REQUIREMENTS['figures_tables_max']} total")
    if total_figs_tables <= NATURE_COMM_REQUIREMENTS['figures_tables_max']:
        print(f"   ✅ PASS")
    else:
        print(f"   ⚠️  EXCEEDS by {total_figs_tables - NATURE_COMM_REQUIREMENTS['figures_tables_max']}")

    # References
    num_refs = count_references(content)
    print(f"\n📚 REFERENCES")
    print(f"   Estimated: {num_refs} citations")
    print(f"   Typical: ≤{NATURE_COMM_REQUIREMENTS['references_typical']}")
    if num_refs <= NATURE_COMM_REQUIREMENTS['references_typical']:
        print(f"   ✅ ACCEPTABLE")
    else:
        print(f"   ⚠️  HIGH (consider consolidating)")

    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")

    issues = []
    warnings = []

    if title_words > NATURE_COMM_REQUIREMENTS['title_words_max']:
        issues.append(f"Title too long ({title_words} words)")

    if abstract_words < NATURE_COMM_REQUIREMENTS['abstract_min']:
        warnings.append(f"Abstract too short ({abstract_words} words)")
    elif abstract_words > NATURE_COMM_REQUIREMENTS['abstract_max']:
        issues.append(f"Abstract too long ({abstract_words} words)")

    if main_text_words > NATURE_COMM_REQUIREMENTS['main_text_max']:
        issues.append(f"Main text too long ({main_text_words:,} words, exceeds by {main_text_words - NATURE_COMM_REQUIREMENTS['main_text_max']:,})")

    if total_figs_tables > NATURE_COMM_REQUIREMENTS['figures_tables_max']:
        warnings.append(f"Too many figures/tables ({total_figs_tables})")

    if num_refs > NATURE_COMM_REQUIREMENTS['references_typical']:
        warnings.append(f"High reference count ({num_refs})")

    if issues:
        print(f"\n❌ CRITICAL ISSUES ({len(issues)}):")
        for issue in issues:
            print(f"   • {issue}")

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"   • {warning}")

    if not issues and not warnings:
        print(f"\n✅ MANUSCRIPT COMPLIES WITH NATURE COMMUNICATIONS REQUIREMENTS")
    elif not issues:
        print(f"\n✅ MANUSCRIPT MEETS CRITICAL REQUIREMENTS (minor warnings only)")
    else:
        print(f"\n❌ MANUSCRIPT REQUIRES REVISION TO MEET REQUIREMENTS")

    print()


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python check_nature_comm_compliance.py MANUSCRIPT_FILE")
        sys.exit(1)

    check_manuscript(sys.argv[1])
