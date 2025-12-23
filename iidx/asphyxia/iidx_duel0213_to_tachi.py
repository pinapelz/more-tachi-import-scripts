import argparse
import json
import os
from datetime import datetime


LAMP_MAP = {
    1: "FAILED",
    2: "ASSIST CLEAR",
    3: "EASY CLEAR",
    4: "CLEAR",
    5: "HARD CLEAR",
    6: "EX HARD CLEAR",
    7: "FULL COMBO"
}

DIFFICULTY_MAP = { # Beginner difficulty not supported
    1: "NORMAL",
    2: "HYPER",
    3: "ANOTHER",
    4: "LEGGENDARIA",
    6: "DP NORMAL",
    7: "DP HYPER",
    8: "DP ANOTHER",
    9: "DP LEGGENDARIA"
}

def convert_duel0213_to_tachi(file: str, single_output_path: str, double_output_path: str, service: str):
    with open(file, "r", encoding="utf-8") as infile:
        sp_scores = []
        dp_scores = []
        export_data = json.load(infile)
        data_sect = export_data["data"]
        for score_id in data_sect:
            data = data_sect[score_id]
            if data["collection"] != "score":
                continue

            music_id = str(data["mid"])
            cArray = data["cArray"]
            played_levels = []
            for i in range(10):
                if i == 0 or i == 5: # skip BEGINNER
                   continue
                if cArray[i] != 0:
                    played_levels.append((i, cArray[i]))

            for diff, lamp_val in played_levels:
                score = data["esArray"][diff]
                difficulty = DIFFICULTY_MAP[diff]
                pgreat = data["pgArray"][diff]
                great = data["gArray"][diff]
                lamp = LAMP_MAP[lamp_val]
                timestamp_str = data["updatedAt"]
                timestamp = int(datetime.fromisoformat(timestamp_str.replace('Z', '+00:00')).timestamp() * 1000)
                judgements = {
                    "pgreat": pgreat,
                    "great": great,
                }
                score_obj = {
                    "score": score,
                    "timeAchieved": timestamp,
                    "matchType": "inGameID",
                    "identifier": music_id,
                    "lamp": lamp,
                    "difficulty": difficulty,
                    "judgements": judgements
                }
                if diff <= 4: # SP
                    sp_scores.append(score_obj)
                else:
                    dp_scores.append(score_obj)

    batch_manual_single = {"meta": {"game": "iidx", "playtype": "SP", "service": service}, "scores": sp_scores}
    batch_manual_double = {"meta": {"game": "iidx", "playtype": "DP", "service": service}, "scores": dp_scores}

    with open(single_output_path, "w", encoding="utf-8") as spoutfile:
        json.dump(batch_manual_single, spoutfile, indent=4, ensure_ascii=False)
        print(f"SP Output saved to {single_output_path}")

    with open(double_output_path, "w", encoding="utf-8") as dpoutfile:
        json.dump(batch_manual_double, dpoutfile, indent=4, ensure_ascii=False)
        print(f"DP Output saved to {double_output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="iidx_duel0213_to_tachi.py",
        description="Converts duel0213 Asphyxia IIDX save data to Tachi compatible JSON",
    )
    parser.add_argument(
        "-s",
        "--service",
        help="Service description to be shown on Tachi (Note for where this score came from)",
        default="beatmania IIDX Asphyxia Export",
    )
    parser.add_argument("-f", "--file", help="Score Export JSON Get this by going to the WebUI -> Profiles -> Detail -> Data -> Score Export", required=True)
    parser.add_argument(
        "-so", "--sp-output", help="Output filename for SP scores", default="iidx_scores_sp.json"
    )
    parser.add_argument(
        "-do", "--dp-output", help="Output filename for DP scores", default="iidx_scores_dp.json"
    )
    args = parser.parse_args()
    if args.file is None:
        print("ERROR: Please specify score JSON. Get this by going to the WebUI -> Profiles -> Detail -> Data -> Score Export")
        exit(1)
    if not os.path.exists(args.file):
        print(f"ERROR: The file {args.file} does not exist.")
        exit(1)

    convert_duel0213_to_tachi(args.file, args.sp_output, args.dp_output, args.service)
