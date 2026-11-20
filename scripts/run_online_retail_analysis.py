from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from online_retail import download_dataset, run_analysis


def main():
    parser = argparse.ArgumentParser(description="Download and analyse the UCI Online Retail dataset.")
    parser.add_argument("--cache-dir", type=Path, default=ROOT / "data" / "raw")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs" / "online_retail")
    parser.add_argument("--refresh", action="store_true", help="Download the UCI archive again.")
    args = parser.parse_args()

    archive_path, digest = download_dataset(args.cache_dir, refresh=args.refresh)
    report = run_analysis(archive_path, args.output_dir, digest)
    print("UCI Online Retail analysis completed.")
    print(f"Source rows: {report['data_quality_audit']['source_rows']:,}")
    print(f"Included sales lines: {report['included_sales_lines']:,}")
    print(f"Date range: {report['date_start']} to {report['date_end']}")
    print(f"Total sales: GBP {report['total_sales_gbp']:,.2f}")
    print(f"Reports: {args.output_dir}")


if __name__ == "__main__":
    main()
