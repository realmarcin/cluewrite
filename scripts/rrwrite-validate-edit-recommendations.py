#!/usr/bin/env python3
"""
Validate edit recommendations against schema and perform additional checks.
"""

import argparse
import json
import sys
from pathlib import Path
from collections import Counter

SCRIPTS_DIR = Path(__file__).parent


def validate_schema(recommendations_path: Path, schema_path: Path) -> tuple:
    """Validate JSON against schema."""
    try:
        import jsonschema
    except ImportError:
        return False, ["jsonschema not installed. Install with: pip install jsonschema"]

    with open(recommendations_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    try:
        jsonschema.validate(data, schema)
        return True, []
    except jsonschema.ValidationError as e:
        return False, [str(e)]


def check_duplicate_ids(recommendations: list) -> list:
    """Check for duplicate recommendation IDs."""
    ids = [rec['id'] for rec in recommendations]
    duplicates = [id for id, count in Counter(ids).items() if count > 1]

    if duplicates:
        return [f"Duplicate IDs found: {', '.join(duplicates)}"]
    return []


def check_valid_sections(recommendations: list) -> list:
    """Check if all sections are valid."""
    valid_sections = {
        "abstract", "introduction", "methods", "results",
        "discussion", "availability", "author_summary",
        "multiple", "global"
    }

    errors = []
    for rec in recommendations:
        if rec['section'] not in valid_sections:
            errors.append(f"{rec['id']}: Invalid section '{rec['section']}'")

    return errors


def check_dependency_cycles(recommendations: list) -> list:
    """Check for circular dependencies."""
    errors = []

    # Build dependency graph
    deps = {rec['id']: rec.get('dependencies', []) for rec in recommendations}

    # DFS to detect cycles
    def has_cycle(node, visited, rec_stack):
        visited.add(node)
        rec_stack.add(node)

        for neighbor in deps.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor, visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                return True

        rec_stack.remove(node)
        return False

    visited = set()
    for rec_id in deps:
        if rec_id not in visited:
            if has_cycle(rec_id, visited, set()):
                errors.append(f"Circular dependency detected involving {rec_id}")

    return errors


def check_missing_dependencies(recommendations: list) -> list:
    """Check if all dependencies reference existing edits."""
    errors = []
    all_ids = {rec['id'] for rec in recommendations}

    for rec in recommendations:
        for dep_id in rec.get('dependencies', []):
            if dep_id not in all_ids:
                errors.append(f"{rec['id']}: References non-existent dependency '{dep_id}'")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate edit recommendations")

    parser.add_argument(
        "--recommendations",
        type=Path,
        required=True,
        help="Path to edit_recommendations.json file"
    )

    parser.add_argument(
        "--schema",
        type=Path,
        help="Path to schema file (default: schemas/edit_recommendations_schema.json)"
    )

    args = parser.parse_args()

    if not args.recommendations.exists():
        print(f"✗ File not found: {args.recommendations}")
        return 1

    # Load recommendations
    with open(args.recommendations, 'r', encoding='utf-8') as f:
        data = json.load(f)

    recommendations = data.get('recommendations', [])

    print(f"Validating {len(recommendations)} recommendations...")
    print()

    all_errors = []

    # Schema validation
    if not args.schema:
        args.schema = SCRIPTS_DIR.parent / "schemas" / "edit_recommendations_schema.json"

    if args.schema.exists():
        is_valid, errors = validate_schema(args.recommendations, args.schema)
        if is_valid:
            print("✓ Schema validation passed")
        else:
            print("✗ Schema validation failed:")
            for error in errors:
                print(f"  {error}")
            all_errors.extend(errors)
    else:
        print(f"⚠ Schema not found at {args.schema}, skipping schema validation")

    # Additional checks
    print("\nPerforming additional checks...")

    errors = check_duplicate_ids(recommendations)
    if not errors:
        print("✓ No duplicate IDs")
    else:
        print("✗ Duplicate IDs found:")
        for error in errors:
            print(f"  {error}")
        all_errors.extend(errors)

    errors = check_valid_sections(recommendations)
    if not errors:
        print("✓ All sections valid")
    else:
        print("✗ Invalid sections:")
        for error in errors:
            print(f"  {error}")
        all_errors.extend(errors)

    errors = check_dependency_cycles(recommendations)
    if not errors:
        print("✓ No circular dependencies")
    else:
        print("✗ Circular dependencies detected:")
        for error in errors:
            print(f"  {error}")
        all_errors.extend(errors)

    errors = check_missing_dependencies(recommendations)
    if not errors:
        print("✓ All dependencies exist")
    else:
        print("✗ Missing dependencies:")
        for error in errors:
            print(f"  {error}")
        all_errors.extend(errors)

    # Summary
    print()
    print("=" * 60)
    if all_errors:
        print(f"Validation FAILED with {len(all_errors)} errors")
        return 1
    else:
        print("Validation PASSED ✓")
        print(f"  {len(recommendations)} recommendations validated successfully")
        return 0


if __name__ == "__main__":
    sys.exit(main())
