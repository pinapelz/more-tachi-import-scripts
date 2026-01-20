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
import zipfile
from pathlib import Path
import hashlib
import shutil
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

USC_DIFFICULTY_MAP = {
    "light": "NOV",
    "challenge": "ADV",
    "extended": "EXH",
    "infinite": "INF"
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

def find_all_ksh_files(path):
    target_dir = Path(path)
    ksh_files = [f for f in target_dir.rglob("*.ksh") if f.is_file() and "__MACOSX" not in f.parts]
    return ksh_files


def get_ksh_difficulty(path):
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("difficulty="):
                    return line.split("=")[1]
            return None
    except:
        return None

def compute_sha1(path: Path) -> str:
    sha1 = hashlib.sha1()
    with path.open("rb") as f:
        while chunk := f.read(0x80):
            sha1.update(chunk)
    digest = sha1.digest()
    parts = [int.from_bytes(digest[i:i+4], "big") for i in range(0, 20, 4)]
    return "".join(f"{x:08x}" for x in parts)

def download_and_generate_chart_hash(download_url: str):
    chart_file_name = download_url.split("/")[-1]
    try:
        print(f"[DOWNLOAD] Downloading Chart Data {chart_file_name}")
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        with open("chart.zip", "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("[DOWNLOAD] Downloading ")
    except Exception as e:
        print(f"[DOWNLOAD] ERROR! Failed to download {chart_file_name}. EXCEPTION: {e}")
        return None
    os.makedirs("working", exist_ok=True)
    try:
        with zipfile.ZipFile("chart.zip", 'r') as zip_ref:
            zip_ref.extractall("working")
    except Exception:
        print("[ERROR] Unable to extract, bad ZIP file? Skipping...")
        return None
    print("[EXTRACT] Successfully extracted chart data")
    ksh_files = find_all_ksh_files("working")
    processed_charts = {}
    for chart_path in ksh_files:
        print(f"[HASH] Now generating hash for {chart_path}")
        ksh_difficulty = get_ksh_difficulty(chart_path)
        if not ksh_difficulty:
            print("[ERROR] No difficulty found in KSM chart. This may be an invalid chart")
            continue
        usc_diff_name = USC_DIFFICULTY_MAP[ksh_difficulty]
        sha1_hash = compute_sha1(chart_path)
        processed_charts[usc_diff_name] = sha1_hash
    return processed_charts

def create_row_db(data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Charts (internalId, hash, title, artist, effector, level, diff_shortname, path, folderid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (
        data["internalId"], data["hash"], data["title"], data["artist"], data["effector"], data["level"], data["diff_shortname"], data["path"], data["folderid"]
    ))
    result = cursor.fetchone()
    conn.commit()
    print("[DB] Wrote row to DB")
    conn.close()
    return result is not None

def process_chart_page(page_num: int, db_path: str, auto_stop: bool):
    charts = []
    response = requests.get(NAUTICA_URL + "?page="+str(page_num), headers=headers)
    resp_page_obj = json.loads(response.text)
    folder_id = get_next_available_folder_id(db_path)
    for entry in resp_page_obj["data"]:
        title = entry["title"]
        artist = entry["artist"]
        download_url = entry["cdn_download_url"]
        if os.path.exists("working"):
            shutil.rmtree("working")
            print("[CLEANUP] Removed existing working directory")
        if os.path.exists("chart.zip"):
            os.remove("chart.zip")
            print("[CLEANUP] Removed existing chart.zip")
        hash_data = download_and_generate_chart_hash(download_url)
        if hash_data is None:
            continue
        for chart in entry["charts"]:
            difficulty = int(chart["difficulty"])
            level = chart["level"]
            if chart_already_processed(db_path, chart["id"]):
                if auto_stop:
                    print("[TERMINATE] Auto stopping due to finding a chart that's already added")
                    exit(0)
                print(f"[SKIP] {title} - {difficulty} already exists. Skipping...")
                continue
            effector = chart["effector"]
            diff_shortname = DIFF_NAME_MAP[difficulty]
            charts.append({
                "internalId": chart["id"],
                "title": title,
                "hash": hash_data[diff_shortname],
                "artist": artist,
                "effector": effector,
                "level": level,
                "diff_shortname": diff_shortname,
                "path": f"/nautica/chart.ksh",
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
    parser.add_argument("--start-page", help="Start from this page on ksm.dev", default=1)
    parser.add_argument("--auto-stop", help="Auto stop on name collision (indicates all caught up)", action="store_true")
    args = parser.parse_args()
    db_path = args.db
    if not db_path:
        db_path = "maps.db"
    create_maps_db_if_not_exists(db_path)
    num_pages = get_nautica_num_pages()
    start_page = int(args.start_page)
    auto_stop = bool(args.auto_stop)
    print(f"Found {num_pages} to process...")
    for i in range(start_page, num_pages + 1):
        print(f"[PROGRESS] {i}/{num_pages + 1} COMPLETED")
        charts = process_chart_page(i, db_path, auto_stop)
        for chart in charts:
            create_row_db(chart)
