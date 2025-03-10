import argparse
import json
import urllib.request
import pytz
from datetime import datetime

ONGEKI_AQUADX_JSON = "https://aquadx.net/d/wacca/00/all-music.json"

DIFFICULTY_MAPPING = {
    0: "NORMAL",
    1: "HARD",
    2: "EXPERT",
    3: "INFERNO",
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

def convert_to_aquadx_json_to_tachi_json(input_json: str, output_file: str, service: str, music_json: str):
    if music_json == "online":
        req = urllib.request.Request(ONGEKI_AQUADX_JSON, headers=headers)
        with urllib.request.urlopen(req) as response:
            music_json = json.load(response)
    else:
        with open(music_json, "r", encoding="utf-8") as file:
            music_json = json.load(file)

    with open(input_json, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    batch_manual = {
        "meta": {"game": "wacca", "playtype": "Single", "service": service},
        "scores": [],
    }

    processed_count = 0
    skipped_count = 0

    if "recent" in raw_data:
        for entry in raw_data["recent"]:
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
            judgements = entry.get("judgements", [0,0,0,0])
            marvelous = judgements[0]
            great = judgements[1]
            good = judgements[2]
            miss = judgements[3]

            score = entry.get("achievement", 0)

            lamp = "CLEAR" if entry.get("isClear", False) else "FAILED"
            if entry.get("isMissless", False):
                lamp = "MISSLESS"
            if entry.get("isFullCombo", False):
                lamp = "FULL COMBO"
            if entry.get("isAllPerfect", False):
                lamp = "ALL MARVELOUS"

            dt = datetime.fromisoformat(entry.get("userPlayDate").rstrip("Z")).replace(tzinfo=pytz.UTC)
            timestamp = int(dt.timestamp())
            fast = entry.get("fastCt",0)
            slow = entry.get("slowCt", 0)
            combo = entry.get("maxCombo",0)

            score_entry = {
                "score": score,
                "lamp": lamp,
                "matchType": "songTitle",
                "identifier": str(song_title),
                "difficulty": DIFFICULTY_MAPPING[level],
                "timeAchieved": timestamp * 1000 if timestamp else None,
                "judgements": {
                    "marvelous": marvelous,
                    "great": great,
                    "good": good,
                    "miss": miss,
                },
                "optional": {
                    "maxCombo": combo,
                    "fast": fast,
                    "slow": slow,
                },
            }

            batch_manual["scores"].append(score_entry)

    with open(output_file, "w", encoding="utf-8") as f:
        print("--- Processing Summary ---")
        print(f"Total scores processed: {processed_count}")
        print(f"Output saved to {output_file}")
        json.dump(batch_manual, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ongeki_aquadx_to_tachi.py",
        description="Converts AquaDX API JSON for WACCA to Tachi compatible JSON",
        epilog="damage, fast, slow, unavailable on the webui"
    )
    parser.add_argument("input_file", help="Path to the input JSON file exported from AquaDX")
    parser.add_argument(
        "-s",
        "--service",
        help="Service description to be shown on Tachi (Note for where this score came from)",
        default="AquaDX WACCA Import (API JSON)",
    )
    parser.add_argument(
        "-o", "--output", help="Output filename", default="aquadx_wacca_tachi.json"
    )
    parser.add_argument("--music", "--music-file", help="JSON file containing the mappings of song names to IDs. Check README for moe info", default="online")
    args = parser.parse_args()
    convert_to_aquadx_json_to_tachi_json(args.input_file, args.output, args.service, args.music)
