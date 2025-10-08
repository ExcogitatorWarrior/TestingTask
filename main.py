import argparse
import csv
import sys
from tabulate import tabulate
from reports import average_rating, average_price


def parse_args():
    parser = argparse.ArgumentParser(description="Generate product reports from CSV files.")
    parser.add_argument("--files", nargs="+", required=True, help="List of CSV files to read.")
    parser.add_argument("--report", default="average-rating", help="Report type (default: 'average-rating').")
    return parser.parse_args()


def read_csv_files(file_paths):
    rows = []
    for path in file_paths:
        try:
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows.extend(reader)
        except FileNotFoundError:
            print(f"Error: file not found: {path}")
            sys.exit(1)
    return rows

def main():
    args = parse_args()
    data = read_csv_files(args.files)

    if args.report == "average-rating":
        report_data = average_rating.generate(data)
        headers = [" ", "Brand", "Average Rating"]
    # Potential upgrade
    #elif args.report == "average-price":
    #    report_data = average_price.generate(data)
    #    headers = [" ", "Brand", "Average Price"]
    else:
        raise ValueError(f"Unknown report type: {args.report}")

    # .2f for consistent formatting
    table = [[i+1, brand, f"{rating:.2f}"] for i, (brand, rating) in enumerate(report_data)]
    print(tabulate(table, headers=headers, tablefmt="rounded_grid"))


if __name__ == "__main__":
    main()