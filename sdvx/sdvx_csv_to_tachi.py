import csv
import json
import argparse
import time

DIFFICULTY_MAPPING = {
    "NOVICE": "NOV",
    "ADVANCED": "ADV",
    "EXHAUST": "EXH",
    "INFINITE": "INF",
    "GRAVITY": "GRV",
    "HEAVENLY": "HVN",
    "VIVD": "VVD",
    "EXCEED": "XCD",
    "MAXIMUM": "MXM"
}

LAMP_MAPPING = {
    "PLAYED": "FAILED",
    "COMPLETE": "CLEAR",
}

def convert_sdvx_csv_to_tachi_json(csv_file, game, playtype, service, unixtime):
    encodings = ['utf-8-sig', 'utf-8', 'shift-jis', 'cp932']

    for encoding in encodings:
        try:
            batch_manual = {
                "meta": {
                    "game": game,
                    "playtype": playtype,
                    "service": service
                },
                "scores": []
            }

            with open(csv_file, newline='', encoding=encoding) as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                required_fields = ["楽曲名", "難易度", "クリアランク", "ハイスコア"]
                if not all(field in fieldnames for field in required_fields):
                    continue


                for row in reader:
                    lamp = LAMP_MAPPING[row["クリアランク"].upper()]
                    if row.get("ULTIMATE CHAIN"):
                        lamp = "ULTIMATE CHAIN"
                    if row.get("PERFECT"):
                        lamp = "PERFECT ULTIMATE CHAIN"

                    score_entry = {
                        "score": int(row["ハイスコア"]),
                        "lamp": lamp,
                        "matchType": "songTitle",
                        "identifier": row["楽曲名"],
                        "difficulty": DIFFICULTY_MAPPING[row["難易度"].upper()],
                    }
                    optional_fields = {}
                    if row.get("EXスコア"):
                        optional_fields["exScore"] = int(row["EXスコア"])
                    if row.get("fast"):
                        optional_fields["fast"] = int(row["fast"])
                    if row.get("slow"):
                        optional_fields["slow"] = int(row["slow"])
                    if row.get("maxCombo"):
                        optional_fields["maxCombo"] = int(row["maxCombo"])
                    if row.get("gauge"):
                        optional_fields["gauge"] = float(row["gauge"])
                    if unixtime:
                        if unixtime == "now":
                            unixtime = int(time.time())*1000
                        optional_fields["timeAchieved"] = unixtime
                    if optional_fields:
                        score_entry["optional"] = optional_fields
                    batch_manual["scores"].append(score_entry)
                return batch_manual
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error with encoding {encoding}: {str(e)}")
            continue

    raise ValueError("Failed to read CSV file with any supported encoding")


if __name__ == "__main__":
    print("!!!!! WARNING !!!!!")
    print("Please make sure you have read the README about SDVX's official CSV files before importing")
    parser = argparse.ArgumentParser(
        prog="sdvx_csv_to_tachi",
        description="Converts CSV data exported from SDVX eAmuse site to Tachi compatibile JSON",
        epilog="Note that not all information can be derived from the CSV so some fields will be missing from Tachi"
    )
    parser.add_argument("csv_filename", help="Path to the CSV file")
    parser.add_argument("-s", "--service", help="Service description to be shown on Tachi (Note for where this score came from)", default="SDVX Arcade Import")
    parser.add_argument("-o", "--output", help="Output filename", default="sdvx_tachi.json")
    parser.add_argument("-t", "--time", help="UNIX time (in milliseconds) that should be added to the scores. Input 'now' if you want to use current time. If no value is provided timeAchieved will not be added to the final JSON", default=None)
    args = parser.parse_args()

try:
    output_json = convert_sdvx_csv_to_tachi_json(args.csv_filename, "sdvx", "Single", args.service)

    with open(args.output, "w", encoding="utf-8") as json_file:
        json.dump(output_json, json_file, ensure_ascii=False, indent=4)

    print("Conversion completed. JSON saved as " + args.output)
except Exception as e:
    print(f"Error: {str(e)}")
