import argparse
import json

DIFFICULTY_MAPPING = {
    0: "BASIC",
    1: "ADVANCED",
    2: "EXPERT",
    3: "MASTER",
    4: "ULTIMA",
    5: "WORLD'S END",
}

def convert_from_aquadx_json_to_tachi_json(input_json: str, output_file: str, service: str):
    with open(input_json, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    batch_manual = {
        "meta": {"game": "chunithm", "playtype": "Single", "service": service},
        "scores": [],
    }

    processed_count = 0
    skipped_count = 0

    if "userPlaylogList" in raw_data:
        for entry in raw_data["userPlaylogList"]:
            level = entry.get("level", 0)
            if level not in DIFFICULTY_MAPPING.keys():
                skipped_count += 1
                continue

            # Skip World's End, Unsupported by Tachi
            if level == 5 or level not in DIFFICULTY_MAPPING:
                skipped_count += 1
                continue

            processed_count += 1
            music_id = entry["musicId"]

            score_value = entry.get("score", 0)
            is_clear = entry.get("isClear", False)
            is_full_combo = entry.get("isFullCombo", False)
            is_all_justice = entry.get("isAllJustice", False)
            is_all_perfect = entry.get("isAllPerfect", False)
            lamp = "FAILED"
            if is_all_perfect:
                lamp = "ALL JUSTICE CRITICAL"
            elif is_all_justice:
                lamp = "ALL JUSTICE"
            elif is_full_combo:
                lamp = "FULL COMBO"
            elif is_clear:
                lamp = "CLEAR"
            timestamp = entry.get("sortNumber", None)

            jcrit = entry.get("judgeHeaven", 0) + entry.get("judgeCritical", 0)
            justice = entry.get("judgeJustice", 0)
            attack = entry.get("judgeAttack", 0)
            miss = entry.get("judgeGuilty", 0)
            combo = entry.get("maxCombo", 0)

            score_entry = {
                "score": score_value,
                "lamp": lamp,
                "matchType": "inGameID",
                "identifier": str(music_id),
                "difficulty": DIFFICULTY_MAPPING[level],
                "timeAchieved": timestamp * 1000 if timestamp else None,
                "judgements": {
                    "jcrit": jcrit,
                    "justice": justice,
                    "attack": attack,
                    "miss": miss,
                },
                "optional": {"maxCombo": combo},
            }

            batch_manual["scores"].append(score_entry)

    with open(output_file, "w", encoding="utf-8") as f:
        print("--- Processing Summary ---")
        print(f"Total scores processed: {processed_count}")
        print(f"Scores skipped (level 5 or invalid): {skipped_count}")
        print(f"Output saved to {output_file}")
        json.dump(batch_manual, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="chuni_aquadx_to_tachi",
        description="Converts AquaDX score data for Chuni to Tachi compatible JSON",
        epilog="Fast/Slow can't be derived (I think)",
    )
    parser.add_argument("input_file", help="Path to the input JSON file exported from AquaDX")
    parser.add_argument(
        "-s",
        "--service",
        help="Service description to be shown on Tachi (Note for where this score came from)",
        default="AquaDX Chuni Import",
    )
    parser.add_argument(
        "-o", "--output", help="Output filename", default="aquadx_chuni_tachi.json"
    )
    args = parser.parse_args()
    convert_from_aquadx_json_to_tachi_json(args.input_file, args.output, args.service)
