"""
Required columsn for a maps.db to be valid for Tachi
hash
title
artist
effector
level
diff_shortname
path
folderid -> Same chart different difficulties just need to have the same value
"""
import argparse
import requests
import json
import sqlite3
import os

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

NAUTICA_URL="https://ksm.dev/app/songs"
SCHEMA = """CREATE TABLE Charts (
    internalId TEXT PRIMARY KEY,
    hash TEXT NOT NULL,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    effector TEXT,
    level INTEGER,
    diff_shortname TEXT,
    path TEXT NOT NULL,
    folderid INTEGER
);
"""
DIFF_NAME_MAP = {
    1 : "NOV",
    2: "ADV",
    3: "EXH",
    4: "INF"
}
def create_maps_db_if_not_exists(filepath: str):
    if os.path.exists(filepath):
        print("[DB] Maps DB already exists, skipping creation")
        return
    print("[DB] Creating new maps.db file")
    conn = sqlite3.connect(filepath)
    cursor = conn.cursor()
    cursor.execute(SCHEMA)
    conn.commit()
    conn.close()


def get_nautica_num_pages():
    response = requests.get(NAUTICA_URL,  headers=headers)
    resp_obj = json.loads(response.text)
    return int(resp_obj["meta"]["last_page"])

def get_next_available_folder_id(db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(folderid) FROM Charts")
    result = cursor.fetchone()
    if result and result[0] is not None:
        return result[0] + 1
    else:
        return 1

def chart_already_processed(db_path: str, internal_id: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM Charts WHERE internalId = ?", (internal_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def download_and_generate_charts():
    pass

def get_charts_from_page(page_num: int, db_path: str):
    charts = []
    response = requests.get(NAUTICA_URL + "?page="+str(page_num), headers=headers)
    resp_page_obj = json.loads(response.text)
    folder_id = get_next_available_folder_id(db_path)
    for entry in resp_page_obj["data"]:
        title = entry["title"]
        artist = entry["artist"]
        download_url = entry["cdn_download_url"]
        for chart in entry["charts"]:
            difficulty = int(chart["difficulty"])
            level = chart["level"]
            if chart_already_processed(chart["id"]):
                print(f"[SKIP] {title} - {difficulty} already exists. Skipping...")
                continue
            effector = chart["effector"]
            diff_shortname = DIFF_NAME_MAP[difficulty]
            charts.append({
                "internalId": chart["id"],
                "title": title,
                "artist": artist,
                "effector": effector,
                "level": level,
                "diff_shortname": diff_shortname,
                "path": "/charts/blahblah",
                "folderid": folder_id
            })
        folder_id += 1
    return charts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="nautica_to_maps",
        description="Converts ALL charts on Nautica (ksm.dev) to a USC maps.db file",
    )
    parser.add_argument("--db", help="Path to existing maps.db if none-specified this script will search in current working dir or create a new one")
    args = parser.parse_args()
    db_path = args.db
    if not db_path:
        db_path = "maps.db"
    create_maps_db_if_not_exists(db_path)
    print(get_charts_from_page(1, db_path))
