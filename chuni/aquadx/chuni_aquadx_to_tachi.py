import argparse
import json
import urllib.request
import os

DIFFICULTY_MAPPING = {
    0: "BASIC",
    1: "ADVANCED",
    2: "EXPERT",
    3: "MASTER",
    4: "ULTIMA",
    5: "WORLD'S END",
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

def convert_from_aquadx_json_to_tachi_json(raw_data: str, output_file: str, service: str):
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
            note_lamp = "NONE"
            clear_lamp = "FAILED" # AquaNet doesn't export other clear lamps?
            if is_all_perfect:
                note_lamp = "ALL JUSTICE CRITICAL"
            elif is_all_justice:
                note_lamp = "ALL JUSTICE"
            elif is_full_combo:
                note_lamp = "FULL COMBO"
            elif is_clear:
                clear_lamp = "CLEAR"
            timestamp = entry.get("sortNumber", None)

            jcrit = entry.get("judgeHeaven", 0) + entry.get("judgeCritical", 0)
            justice = entry.get("judgeJustice", 0)
            attack = entry.get("judgeAttack", 0)
            miss = entry.get("judgeGuilty", 0)
            combo = entry.get("maxCombo", 0)

            score_entry = {
                "score": score_value,
                "noteLamp": note_lamp,
                "clearLamp": clear_lamp,
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
    parser.add_argument("-f", "--file", help="Manual. Specify path to the input exported score JSON file exported from AquaDX", required=False)
    parser.add_argument(
        "-s",
        "--service",
        help="Service description to be shown on Tachi (Note for where this score came from)",
        default="AquaDX Chuni Import",
    )
    parser.add_argument("-t", "--token", help="Use AquaNet Token to directly grab data from API. Get it from Network tab in your browser and check the API request it makes ?token=???", required=False)
    parser.add_argument("-u", "--url", help="AquaNet API endpoint. No need to use this unless you self-host AquaDX", default="https://aquadx.net/aqua")
    parser.add_argument(
        "-o", "--output", help="Output filename", default="aquadx_chuni_tachi.json"
    )
    args = parser.parse_args()
    # Some checks to make sure input is valid
    if args.token is None and args.file is None:
        print("ERROR: No valid input method specified. You must specify either --file or --token")
        exit(1)
    aquadx_url = args.url
    if not aquadx_url.startswith("https://") and not aquadx_url.startswith("http://"):
        aquadx_url = "https://" + aquadx_url


    if args.file is not None:
        print("An input file has been specified, using local file as input")
        if not os.path.exists(args.file):
            print(f"ERROR: The file {args.file} does not exist.")
            exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    else:
        print("Pulling Chuni playdata from remote AquaDX at: " + aquadx_url)
        req = urllib.request.Request(aquadx_url+"/api/v2/game/chu3/export?token="+args.token, headers=headers)
        with urllib.request.urlopen(req) as response:
            raw_data = json.load(response)
    convert_from_aquadx_json_to_tachi_json(raw_data, args.output, args.service)
