import requests
import os
import sys
import time

# --- CONFIGURATION ---
BASE_OUTPUT_DIR = "./EuropePMC_Breast_Data"
START_YEAR = 2016
END_YEAR = 2026
BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
PAGE_SIZE = 50
RESUME_FILE = os.path.join(BASE_OUTPUT_DIR, "resume_status.txt")

session = requests.Session()


def get_category(title, abstract):
    text = f"{title} {abstract}".lower()
    if any(w in text for w in ["cancer", "carcinoma", "malignant", "tumor", "neoplasm", "metastasis"]):
        return "Cancer"
    if any(w in text for w in ["lactation", "breastfeeding", "milk", "postpartum"]):
        return "Lactation_Breastfeeding"
    if any(w in text for w in ["surgery", "plastic", "reconstruction", "implant", "augmentation", "mammoplasty"]):
        return "Surgery_Cosmetic"
    if any(w in text for w in ["cyst", "mastitis", "fibroadenoma", "benign", "abscess"]):
        return "Benign_Conditions"
    return "General_Biology"


def download_or_copy(pmcid, year, month, category):
    new_dir = os.path.join(BASE_OUTPUT_DIR, str(year), f"{month:02d}", category)
    os.makedirs(new_dir, exist_ok=True)
    new_file = os.path.join(new_dir, f"{pmcid}.xml")

    if os.path.exists(new_file):
        return "Skipped"

    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
    try:
        r = session.get(url, timeout=30)
        if r.status_code == 200 and len(r.content) > 500:
            with open(new_file, "wb") as f:
                f.write(r.content)
            return "Downloaded"
    except:
        pass
    return "Failed"


def get_total_count(query):
    params = {"query": query, "resultType": "idlist", "format": "json", "pageSize": 1}
    try:
        r = session.get(BASE_URL, params=params, timeout=60)
        return int(r.json().get("hitCount", 0))
    except:
        return 0


def load_resume():
    if not os.path.exists(RESUME_FILE):
        return START_YEAR, 1, 0, "*"
    try:
        with open(RESUME_FILE, "r") as f:
            data = f.read().strip().split("|")
            if len(data) == 4:
                return int(data[0]), int(data[1]), int(data[2]), data[3]
    except:
        pass
    return START_YEAR, 1, 0, "*"


def save_resume(year, month, processed, cursor):
    os.makedirs(os.path.dirname(RESUME_FILE), exist_ok=True)
    with open(RESUME_FILE, "w") as f:
        f.write(f"{year}|{month}|{processed}|{cursor}")


def process_month(year, month, start_count, start_cursor):
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-31"
    query = f'(TITLE:(breast OR mammary) OR ABS:(breast OR mammary)) AND (FIRST_PDATE:[{start_date} TO {end_date}]) AND (OPEN_ACCESS:Y)'

    total = get_total_count(query)
    if total == 0:
        return

    print(f"\n--- {year}-{month:02d} | Total in month: {total} ---")
    cursor = start_cursor
    processed = start_count

    while True:
        params = {
            "query": query, "resultType": "core",
            "cursorMark": cursor, "pageSize": PAGE_SIZE, "format": "json"
        }

        try:
            r = session.get(BASE_URL, params=params, timeout=60)
            res_data = r.json()
            articles = res_data.get("resultList", {}).get("result", [])
            if not articles:
                break

            for art in articles:
                pmcid = art.get("pmcid")
                processed += 1
                if pmcid:
                    cat = get_category(art.get("title", ""), art.get("abstractText", ""))
                    status = download_or_copy(pmcid, year, month, cat)
                    sys.stdout.write(f"\rProgress: {processed}/{total} | {status}: {pmcid} ".ljust(65))
                    sys.stdout.flush()

            next_cursor = res_data.get("nextCursorMark")

            # Save progress after each batch of 50
            if next_cursor and next_cursor != cursor:
                cursor = next_cursor
                save_resume(year, month, processed, cursor)
            else:
                break

            time.sleep(0.3)

        except Exception as e:
            print(f"\nError: {e}")
            break


if __name__ == "__main__":
    res_year, res_month, res_count, res_cursor = load_resume()

    print(f"Jump to -> Year: {res_year}, Month: {res_month}, At: {res_count}")

    for year in range(res_year, END_YEAR + 1):
        # Start from res_month only in the first year
        m_start = res_month if year == res_year else 1

        for month in range(m_start, 13):
            # Use saved count/cursor only for the very first step of resume
            current_count = res_count if (year == res_year and month == res_month) else 0
            current_cursor = res_cursor if (year == res_year and month == res_month) else "*"

            process_month(year, month, current_count, current_cursor)

            # Prepare for next month
            res_count = 0
            res_cursor = "*"

            next_month = month + 1
            next_year = year
            if next_month > 12:
                next_month = 1
                next_year += 1

            # Save the start of the next month to resume correctly if interrupted
            save_resume(next_year, next_month, 0, "*")

    print("\n\nAll tasks completed.")