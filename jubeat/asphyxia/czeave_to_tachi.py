import argparse
import json
import os

LAMP_MAP = {
    1: "FAILED",
    3: "CLEARED"
}

SEQUENCE_MAP = {
    0: "BSC",
    1: "ADV",
    2: "EXT"
}

def convert_from_czeave_json_to_tachi_json(file: str, output_path: str, service: str):
    with open(file, "r", encoding="utf-8") as infile:
        batch_manual = {
            "meta": {"game": "jubeat", "playtype": "Single", "service": service},
        }
        scores = []
        data = [json.loads(line) for line in infile if '"collection":"score"' in line]
        for score in data:
            difficulty = SEQUENCE_MAP[score["seq"]]
            if score["isHardMode"]:
                difficulty = "HARD " + difficulty
            lamp = "FAILED"
            if score["clearCount"] >= 1:
                lamp = "CLEAR"
            if score["fullcomboCount"] >= 1:
                lamp = "FULL COMBO"
            if score["excellentCount"] >= 1:
                lamp = "EXCELLENT"

            timestamp = score["updatedAt"]["$$date"]
            music_rate = score["musicRate"] / 10
            curr_score = {
                "matchType": "inGameID",
                "identifier": str(score["musicId"]),
                "difficulty": difficulty,
                "score": score["score"],
                "lamp": lamp,
                "timeAchieved": timestamp,
                "musicRate": music_rate,
            }
            scores.append(curr_score)
        batch_manual["scores"] = scores
        with open(output_path, "w", encoding="utf-8") as outfile:
            json.dump(batch_manual, outfile, indent=4, ensure_ascii=False)
            print(f"Output saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="czeave_to_tachi.py",
        description="Converts czeave Asphyxia Jubeat save data to Tachi compatible JSON",
    )
    parser.add_argument(
        "-s",
        "--service",
        help="Service description to be shown on Tachi (Note for where this score came from)",
        default="jubeat Asphyxia CZEAve",
    )
    parser.add_argument("-f", "--file", help="AsphyxiaCORE jubeat .db file (jubeat@asphyxia.db)", required=True)
    parser.add_argument(
        "-o", "--output", help="Output filename", default="czeave_asphyxia_batch_manual.json"
    )
    args = parser.parse_args()
    if args.file is None:
        print("ERROR: Please specify Asphyxia DB file (from savedata folder)")
        exit(1)
    if not os.path.exists(args.file):
        print(f"ERROR: The file {args.file} does not exist.")
        exit(1)

    convert_from_czeave_json_to_tachi_json(args.file, args.output, args.service)
