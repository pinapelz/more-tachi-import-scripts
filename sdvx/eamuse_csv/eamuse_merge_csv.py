import argparse
import csv
import os

def merge_csv(old_file: str, new_file: str, output_file: str):
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

        with open(output_file, "w", encoding=encoding, newline="") as new_csv:
            writer = csv.writer(new_csv, delimiter=",")
            writer.writerow(header)
            for row in new_csv_set:
                if row == ():
                    continue
                writer.writerow(list(row))

        print("Done! Your newly merged CSV is at " + output_file)
        print("Do you want to delete the old file, and create a new old.csv? (y/n)")
        action = input()
        if not action == "y":
            print("OK. Exiting")
            exit(0)
        print("Renaming " + new_file + " to old.csv and deleting " + old_file + "...")
        os.remove(old_file)
        os.rename(new_file, "old.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="eamuse_merge_to_csv",
        description="Merges an old SDVX e-amuse CSV with a new one. Keeping only new scores in the new file",
    )
    parser.add_argument("--old", help="Old CSV file", required=True)
    parser.add_argument("--new", help="New CSV file", required=True)
    parser.add_argument("--output", help="Output File", default="sdvx_merged.csv")
    args = parser.parse_args()
    merge_csv(args.old, args.new, args.output)
