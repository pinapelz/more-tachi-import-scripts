import argparse
import csv
import os
import requests
import time

DIFFICULTY_MAPPING = {
    "NOVICE": "NOV",
    "ADVANCED": "ADV",
    "EXHAUST": "EXH",
    "INFINITE": "INF",
    "GRAVITY": "GRV",
    "HEAVENLY": "HVN",
    "VIVID": "VVD",
    "EXCEED": "XCD",
    "MAXIMUM": "MXM"
}


def merge_csv(input_file: str, tachi_url: str, username: str, output_file: str):
    encoding = "utf-8"
    header_written = False

    with open(input_file, encoding=encoding) as old_csv, open(output_file, 'w', newline='', encoding=encoding) as new_csv:
        reader = csv.reader(old_csv, delimiter=",")
        writer = csv.writer(new_csv, delimiter=",")

        header = next(reader)

        # Count total rows for progress tracking
        rows = list(reader)
        total_rows = len(rows)
        current_row = 0

        for row in rows:
            current_row += 1
            title = requests.utils.quote(row[0])
            diff = DIFFICULTY_MAPPING[row[1]]
            score = int(row[5])
            api_url = f"{tachi_url}/api/v1/users/{username}/games/sdvx/Single/pbs?search={title}"
            print(f"[{current_row}/{total_rows}] Searching for score: {title} at difficulty {diff}")
            try:
                response = requests.get(api_url)
                time.sleep(0.2)
                response.raise_for_status()
                data = response.json()
                charts = data["body"]["charts"]
                is_unique = True
                if len(charts) == 0:
                    print("Score is unique")
                    is_unique = True
                    if not header_written:
                        writer.writerow(header)
                        header_written = True
                    writer.writerow(row)
                    continue
                chart_id = ""
                for chart in charts:
                    if chart["difficulty"] == diff:
                        print("Found proper chart ID")
                        chart_id = chart["chartID"]
                        break
                if chart_id == "":
                    print("Score is Unique, unable to find a match in the DB")
                    if not header_written:
                        writer.writerow(header)
                        header_written = True
                    writer.writerow(row)
                    continue
                pbs = data["body"]["pbs"]
                for pb in pbs:
                    if pb["chartID"] == chart_id and pb["scoreData"]["score"] == score:
                        print("Found match, score is not unique")
                        is_unique = False
                        break
                if is_unique:
                    if not header_written:
                        writer.writerow(header)
                        header_written = True
                    writer.writerow(row)

            except requests.RequestException as e:
                print(f"Error fetching data for {title}: {e}")
                continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="pb_merge.py",
        description="Takes in a SDVX e-amusement PB CSV, checks against scores on Tachi and generates a new file with only unique scores",
    )
    parser.add_argument(
        "-f", "--file", help="SOUND VOLTEX score CSV (score.csv)", required=True
    )
    parser.add_argument(
        "-o", "--output", help="Output filename", default="merged_sdvx_scores.csv"
    )
    parser.add_argument(
        "-t",
        "--tachi",
        help="API URL for your Tachi instance",
        default="https://kamai.tachi.ac",
    )
    parser.add_argument("-u", "--username", help="Your unique username on Tachi", default="")
    args = parser.parse_args()
    if args.file is None:
        print("ERROR: Please specify the path to the score CSV")
        exit(1)
    if not os.path.exists(args.file):
        print(f"ERROR: The file {args.file} does not exist.")
        exit(1)
    merge_csv(args.file, args.tachi, args.username,  args.output)
