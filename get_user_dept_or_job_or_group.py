import requests
import pandas as pd
from time import sleep

""" the goal here was to look up users by inst_id and return the primary identifier along with ideally the deaprtment or college of the user. if those values are weird or unavailable, then it returns the job if available, and as a last resort the user group """

# ==== CONFIGURATION ====
ALMA_API_KEY = 'APIKEY'
BASE_URL = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/users'
HEADERS = {
    'Authorization': f'apikey {ALMA_API_KEY}',
    'Accept': 'application/json'
}
INPUT_CSV = 'input_ids.csv'
OUTPUT_EXCEL = 'alma_user_output.xlsx'
REQUEST_DELAY = 0.25

# ==== COLLEGE/DEPARTMENT EXTRACTION ====
def extract_college_or_department(stats):
    college = None
    department = None

    for stat in stats:
        category_type = stat.get("category_type", {}).get("value")
        desc = stat.get("statistic_category", {}).get("desc", "")

        if category_type == "COLLEGE" and desc and desc.lower() != "unknown college":
            college = desc
        elif category_type == "DEPARTMENT" and desc and desc.lower() != "unknown department":
            department = desc

    return college or department  # don't return default here — fallback logic will handle it

# ==== FUNCTION TO QUERY ALMA ====
def get_user_data(institution_id):
    url = f"{BASE_URL}/{institution_id}"
    params = {
        'user_id_type': 'INST_ID'
    }

    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code == 200:
        data = response.json()
        primary_id = data.get('primary_id', 'N/A')

        # Try college or department
        stats = data.get('user_statistic', [])
        college_or_dept = extract_college_or_department(stats)

        # === Fallback: job title or user group if necessary ===
        if not college_or_dept or "unknown" in college_or_dept.lower():
            job_desc = data.get('job_description', '').strip()
            user_group_desc = data.get('user_group', {}).get('desc', '').strip()

            if job_desc:
                college_or_dept = job_desc
            elif user_group_desc:
                college_or_dept = user_group_desc
            else:
                college_or_dept = "Unknown"

        return {
            'inst_id': institution_id,
            'gtid': primary_id,
            'college/department': college_or_dept
        }

    elif response.status_code == 404:
        return {
            'inst_id': institution_id,
            'gtid': 'Not found',
            'college/department': 'User not found'
        }

    else:
        return {
            'inst_id': institution_id,
            'gtid': 'Error',
            'college/department': f"API error {response.status_code}"
        }

# ==== MAIN WORKFLOW ====
def main():
    input_df = pd.read_csv(INPUT_CSV)

    required_column = 'inst_id'
    if required_column not in input_df.columns:
        raise ValueError(f"Missing required column '{required_column}' in CSV file.")

    results = []
    total = len(input_df)
    success_count = 0
    failure_count = 0

    for index, row in input_df.iterrows():
        inst_id = row['inst_id']
        print(f"[{index + 1}/{total}]")
        result = get_user_data(inst_id)
        results.append(result)

        if result['gtid'] not in ('Not found', 'Error'):
            success_count += 1
        else:
            failure_count += 1

    output_df = pd.DataFrame(results)
    output_df.to_excel(OUTPUT_EXCEL, index=False)
    print(f"Done. Output saved to {OUTPUT_EXCEL}")
    print(f"{success_count} successes, {failure_count} failures")

if __name__ == "__main__":
    main()
