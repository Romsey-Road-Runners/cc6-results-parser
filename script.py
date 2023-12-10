import csv
import json
import sys
from pprint import pprint


def parse_csv(file_name, race):
    csvfile = open(file_name, "r")
    field_names = (
        ["ID", "Firstname", "Surname", "Club", "Age Group"]
        + [f"R{race_number}" for race_number in range(1, 7)]
        + ["Blank"]
        + [f"R{race_number} Age Group" for race_number in range(1, 7)]
    )
    reader = csv.DictReader(csvfile, field_names)
    results_list = []
    for row in reader:
        if (
            "Firstname" not in row
            or not row["Firstname"]
            or row["Firstname"] == "Firstname"
            or not row[f"R{race}"]
        ):
            continue

        results_list.append(
            {
                "firstName": row["Firstname"].strip().title(),
                "surname": row["Surname"].strip().title(),
                "club": row["Club"].strip(),
                "ageGroup": row["Age Group"].strip(),
                "position": int(row[f"R{race}"])
                if not row[f"R{race} Age Group"]
                else int(row[f"R{race} Age Group"]),
            }
        )
    return results_list


sexes = ["Men", "Women"]
age_cats = ["", "V40", "V50", "V60", "V70"]
race = sys.argv[1]
file_prefix = f"Race-{race}-Results"
file_list = []
complete_results_dict = {}

for combination in [(sex, age_cat) for sex in sexes for age_cat in age_cats]:
    maybe_dash = "-" if combination[1] else ""
    file_name = f"{file_prefix}-{combination[0]}{maybe_dash}{combination[1]}.csv"
    print("Processing " + file_name)
    complete_results_dict[
        f"{combination[0]} {combination[1]}" if maybe_dash else f"{combination[0]}"
    ] = parse_csv(file_name, race)

with open(file_prefix + ".json", "w", encoding="utf-8") as json_file:
    json.dump(complete_results_dict, json_file, ensure_ascii=False, indent=4)
