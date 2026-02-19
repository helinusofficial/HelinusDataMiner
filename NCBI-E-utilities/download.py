import requests
import os
import sys
import time
import calendar

# --- CONFIGURATION ---
BASE_OUTPUT_DIR = "./PMC_BreastCancer_XML"
STATUS_FILE = os.path.join(BASE_OUTPUT_DIR, "resume_status.txt")

START_YEAR = 2016
END_YEAR = 2026
EMAIL = "your mail"
API_KEY = "your key"
REQUEST_DELAY = 0.1 if API_KEY else 0.5

os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})


# ----------------------------
def safe_request(url, params=None, retries=5):
    for i in range(retries):
        try:
            r = session.get(url, params=params, timeout=60)
            if r.status_code == 200: return r
            if r.status_code == 429: time.sleep(10 * (i + 1))
        except:
            time.sleep(2)
    return None


def save_status(year, month, last_id):
    with open(STATUS_FILE, "w") as f:
        f.write(f"{year},{month},{last_id}")


def get_last_status():
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r") as f:
                parts = f.read().strip().split(",")
                if len(parts) == 3: return parts[0], parts[1], parts[2]
        except:
            pass
    return None, None, None


def fetch_pmids_for_month(year, month):
    last_day = calendar.monthrange(year, month)[1]
    start_date = f"{year}/{month:02d}/01"
    end_date = f"{year}/{month:02d}/{last_day}"
    term = f'("breast"[Title/Abstract] OR "mammary"[Title/Abstract]) AND "humans"[MeSH Terms] AND free full text[sb] AND ("{start_date}"[PDAT] : "{end_date}"[PDAT])'
    params = {"db": "pubmed", "term": term, "usehistory": "y", "retmode": "json", "retmax": 0, "email": EMAIL}
    if API_KEY: params["api_key"] = API_KEY
    r = safe_request("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params)
    if not r: return 0, None, None
    data = r.json().get("esearchresult", {})
    return int(data.get("count", 0)), data.get("webenv"), data.get("querykey")


def pmid_to_pmcid(total, webenv, query_key):
    pmcids = []
    batch_size = 200
    for start in range(0, total, batch_size):
        params = {"dbfrom": "pubmed", "db": "pmc", "query_key": query_key, "WebEnv": webenv,
                  "retstart": start, "retmax": batch_size, "retmode": "json", "email": EMAIL, "linkname": "pubmed_pmc"}
        if API_KEY: params["api_key"] = API_KEY
        r = safe_request("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi", params)
        if r:
            try:
                linksets = r.json().get("linksets", [])
                for s in linksets:
                    for ldb in s.get("linksetdbs", []):
                        for link in ldb.get("links", []):
                            val = link if isinstance(link, str) else link.get("id")
                            if val: pmcids.append(str(val))
            except:
                pass
        time.sleep(REQUEST_DELAY)
    return list(set(pmcids))


def download_or_copy(pmcid, year, month):
    new_dir = os.path.join(BASE_OUTPUT_DIR, str(year), f"{month:02d}")
    os.makedirs(new_dir, exist_ok=True)
    new_file = os.path.join(new_dir, f"{pmcid}.xml")
    if os.path.exists(new_file): return "Skipped"
    efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {"db": "pmc", "id": pmcid, "retmode": "xml", "email": EMAIL}
    if API_KEY: params["api_key"] = API_KEY
    r = safe_request(efetch_url, params)
    if r and len(r.content) > 1000:
        with open(new_file, "wb") as f: f.write(r.content)
        return "Downloaded"
    return "Failed"


def fetch_and_download(year, month):
    res_year, res_month, last_id = get_last_status()
    if res_year == str(year) and res_month == str(month) and last_id == "DONE":
        return

    total_hits, webenv, query_key = fetch_pmids_for_month(year, month)
    if total_hits == 0:
        save_status(year, month, "DONE")
        return

    all_pmc_ids = pmid_to_pmcid(total_hits, webenv, query_key)
    if not all_pmc_ids:
        save_status(year, month, "DONE")
        return

    all_pmc_ids.sort()
    total_pmc = len(all_pmc_ids)

    # خروجی هدر ماه
    print(f"\n--- {year}-{month:02d} | Total in month: {total_pmc} ---")

    processed = 0
    skip_mode = (res_year == str(year) and res_month == str(month) and last_id and last_id != "DONE")

    for pmcid in all_pmc_ids:
        processed += 1
        if skip_mode:
            if pmcid == last_id: skip_mode = False
            continue

        status = download_or_copy(pmcid, year, month)
        # خروجی پیشرفت در یک خط
        sys.stdout.write(f"\rProgress: {processed}/{total_pmc} | {status}: PMC{pmcid}                ")
        sys.stdout.flush()

        if processed % 10 == 0:
            save_status(year, month, pmcid)

    save_status(year, month, "DONE")
    print("")  # ایجاد فاصله برای شروع تمیز ماه بعدی


if __name__ == "__main__":
    # ۱. ابتدا ببین آخرین بار کجا بودیم
    res_year, res_month, last_id = get_last_status()

    # تبدیل به عدد برای مقایسه راحت‌تر
    start_y = int(res_year) if (res_year and res_year.isdigit()) else START_YEAR
    start_m = int(res_month) if (res_month and res_month.isdigit()) else 1

    for year in range(START_YEAR, END_YEAR + 1):
        # اگر سال کمتر از سالِ رزومه است، کلاً این سال را رد کن
        if year < start_y:
            continue

        for month in range(1, 13):
            # اگر در سالِ رزومه هستیم، ماه‌های قبل از ماهِ توقف را رد کن
            if year == start_y and month < start_m:
                continue

            fetch_and_download(year, month)