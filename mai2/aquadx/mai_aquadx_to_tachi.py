import argparse
import json
import urllib.request
import os

MAI2_AQUADX_JSON = "https://aquadx.net/d/mai2/00/all-music.json"

DIFFICULTY_MAPPING = {
    0: "DX Basic",
    1: "DX Advanced",
    2: "DX Expert",
    3: "DX Master",
    4: "DX Re:Master"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

def convert_from_aquadx_json_to_tachi_json(raw_data: str, output_file: str, service: str, music_json: str):
    batch_manual = {
        "meta": {"game": "maimaidx", "playtype": "Single", "service": service},
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

            processed_count += 1
            try:
                song_title = music_json[str(entry["musicId"])]["name"]
            except KeyError:
                skipped_count += 1
                continue
            version = music_json[str(entry["musicId"])]["ver"]

            raw_score_value = entry.get("achievement", 0)
            score_value = float(raw_score_value/10000)
            is_clear = entry.get("isClear", False)
            is_full_combo = entry.get("isFullCombo", False)
            is_all_perfect = entry.get("isAllPerfect", False)
            lamp = "FAILED"
            if is_all_perfect:
                lamp = "ALL PERFECT"
                if entry.get("tapGreat") == 0:
                    lamp == "ALL PERFECT+"
            elif is_full_combo:
                lamp = "FULL COMBO"
                if entry.get("tapGood") == 0:
                    lamp = "FULL COMBO+"
            elif is_clear:
                lamp = "CLEAR"
            timestamp = entry.get("loginDate", None)
            combo = entry.get("maxCombo",0)
            fast = entry.get("fastCount", 0)
            slow = entry.get("lateCount", 0)

            pcrit = entry.get("tapCriticalPerfect", 0) + entry.get("holdCriticalPerfect", 0) + entry.get("slideCriticalPerfect", 0)  + entry.get("touchCriticalPerfect", 0) + entry.get("breakCriticalPerfect", 0)
            perfect = entry.get("tapPerfect", 0) + entry.get("holdPerfect", 0) + entry.get("slidePerfect", 0)  + entry.get("touchPerfect", 0) + entry.get("breakPerfect", 0)
            great = entry.get("tapGreat", 0) + entry.get("holdGreat", 0) + entry.get("slideGreat", 0)  + entry.get("touchGreat", 0) + entry.get("breakGreat", 0)
            good = entry.get("tapGood", 0) + entry.get("holdGood", 0) + entry.get("slideGood", 0)  + entry.get("touchGood", 0) + entry.get("breakGood", 0)
            miss = entry.get("tapMiss", 0) + entry.get("holdMiss", 0) + entry.get("slideMiss", 0)  + entry.get("touchMiss", 0) + entry.get("breakMiss", 0)

            difficulty = DIFFICULTY_MAPPING[level]
            if int(version) < 20000:
                print(song_title)
                difficulty = str(difficulty[3:])
            score_entry = {
                "percent": score_value,
                "lamp": lamp,
                "matchType": "songTitle",
                "identifier": str(song_title),
                "difficulty": difficulty,
                "timeAchieved": timestamp * 1000 if timestamp else None,
                "judgements": {
                    "pcrit": pcrit,
                    "perfect": perfect,
                    "great": great,
                    "good": good,
                    "miss": miss
                },
                "optional": {
                    "maxCombo": combo,
                    "fast": fast,
                    "slow": slow

                },
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
        prog="mai_aquadx_to_tachi.py",
        description="Converts AquaDX score data for maimai (DX) to Tachi compatible JSON",
        epilog="Dan and matchingClass not implemented. Please just use other methods for that kind of static info"
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
        "-o", "--output", help="Output filename", default="aquadx_mai2_tachi.json"
    )
    parser.add_argument("-m", "--music", help="all-music.json from AquaNet that maps song id to name (required for Tachi). It will automatically pull from main AquaDX if not specified", default="online")
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
        print("Pulling mai2 playdata from remote AquaDX at: " + aquadx_url)
        req = urllib.request.Request(aquadx_url+"/api/v2/game/mai2/export?token="+args.token, headers=headers)
        with urllib.request.urlopen(req) as response:
            raw_data = json.load(response)

    if args.music == "online":
        req = urllib.request.Request(MAI2_AQUADX_JSON, headers=headers)
        with urllib.request.urlopen(req) as response:
            music_json = json.load(response)
    else:
        with open(args.music, "r", encoding="utf-8") as file:
            music_json = json.load(file)

    args = parser.parse_args()
    convert_from_aquadx_json_to_tachi_json(raw_data, args.output, args.service, music_json)
