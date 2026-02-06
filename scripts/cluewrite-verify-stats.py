#!/usr/bin/env python3
"""
Fact-checking tool for scientific manuscripts.
Verifies numerical claims against source data files.
"""

import argparse
import pandas as pd
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description='Verify statistical claims against CSV data'
    )
    parser.add_argument('--file', required=True, help='Path to CSV/Excel file')
    parser.add_argument('--col', required=True, help='Column name to analyze')
    parser.add_argument(
        '--op',
        choices=['mean', 'max', 'min', 'std', 'count', 'median'],
        required=True,
        help='Statistical operation to perform'
    )
    parser.add_argument('--filter', help='Optional filter (e.g., "age > 30")')

    args = parser.parse_args()

    # Check file exists
    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Load data
    try:
        if args.file.endswith('.csv'):
            df = pd.read_csv(args.file)
        elif args.file.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(args.file)
        else:
            print(f"Error: Unsupported file format: {args.file}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Apply filter if provided
    if args.filter:
        try:
            df = df.query(args.filter)
        except Exception as e:
            print(f"Error applying filter '{args.filter}': {e}", file=sys.stderr)
            sys.exit(1)

    # Check column exists
    if args.col not in df.columns:
        print(f"Error: Column '{args.col}' not found. Available columns: {list(df.columns)}", file=sys.stderr)
        sys.exit(1)

    # Compute statistic
    try:
        column_data = df[args.col]

        if args.op == 'mean':
            result = column_data.mean()
        elif args.op == 'max':
            result = column_data.max()
        elif args.op == 'min':
            result = column_data.min()
        elif args.op == 'std':
            result = column_data.std()
        elif args.op == 'median':
            result = column_data.median()
        elif args.op == 'count':
            result = column_data.count()

        print(result)

    except Exception as e:
        print(f"Error computing {args.op}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
