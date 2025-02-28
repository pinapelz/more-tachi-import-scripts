import argparse
import csv

def merge_csv(old_file: str, new_file: str):
    old_csv_set = set()
    new_csv_set = set()
    encoding = "utf-8"
    with open(old_file, encoding=encoding) as old_csv:
        reader = csv.reader(old_csv, delimiter=",")
        [old_csv_set.add(tuple(row)) for row in reader]
        with open(new_file, "r", encoding=encoding) as new_csv:
            reader = csv.reader(new_csv, delimiter=",")
            header = next(reader)
            [new_csv_set.add(tuple(row)) for row in reader]
            new_csv_set = new_csv_set - old_csv_set

        with open(new_file, "w", encoding=encoding, newline="") as new_csv:
            writer = csv.writer(new_csv, delimiter=",")
            writer.writerow(header)
            for row in new_csv_set:
                if row == ():
                    continue
                writer.writerow(list(row))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="eamuse_merge_to_csv",
        description="Merges an old SDVX e-amuse CSV with a new one. Keeping only new scores in the new file",
    )
    parser.add_argument("--old", help="Old CSV file", required=True)
    parser.add_argument("--new", help="New CSV file", required=True)
    args = parser.parse_args()
    merge_csv(args.old, args.new)
