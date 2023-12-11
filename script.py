import csv
import json
import sys
from pprint import pprint


def parse_csv(file_name, race):
    csvfile = open(file_name, "r")
    if "Overall" in file_name:
        field_names = (
            "ID",
            "Pos",
            "Timestamp",
            f"R{race}",
            "Firstname",
            "Surname",
            "Sex",
            "Club",
            "ClubSex",
            "Age Group",
        )
    else:
        field_names = (
            "ID",
            "Firstname",
            "Surname",
            "Club",
            "Age Group",
            "R1",
            "R2",
            "R3",
            "R4",
            "R5",
            "R6",
            "R7",
            "Blank",
            "R1 Age Group",
            "R2 Age Group",
            "R3 Age Group",
            "R4 Age Group",
            "R5 Age Group",
            "R6 Age Group",
            "R7 Age Group",
        )
    reader = csv.DictReader(csvfile, field_names)
    results_list = []
    for row in reader:
        if row["Firstname"] in ["Firstname", "Fname"] or not row[f"R{race}"]:
            continue

        if not row["Firstname"]:
            results_list.append(
                {
                    "firstName": "Unknown",
                    "surname": "Runner",
                    "club": "Unknown",
                    "ageGroup": "Senior",
                    "position": int(row[f"R{race}"]),
                }
            )
            continue

        results_list.append(
            {
                "firstName": row["Firstname"].strip().title(),
                "surname": row["Surname"].strip().title(),
                "club": row["Club"].strip(),
                "ageGroup": row["Age Group"].strip(),
                "position": int(row[f"R{race}"])
                if not row.get(f"R{race} Age Group")
                else int(row[f"R{race} Age Group"]),
            }
        )
    return sorted(results_list, key=lambda d: d["position"])


sexes = ["Men", "Women"]
age_cats = ["", "V40", "V50", "V60", "V70"]
race = sys.argv[1]
file_prefix = f"Race-{race}-Results"
file_list = []
complete_results_dict = {}

for combination in [(sex, age_cat) for sex in sexes for age_cat in age_cats]:
    maybe_dash = "-" if combination[1] else ""
    file_name = f"{file_prefix}-{combination[0]}{maybe_dash}{combination[1]}.csv"
    dict_key = (
        f"{combination[0]} {combination[1]}" if maybe_dash else f"{combination[0]}"
    )
    file_list.append({"file_name": file_name, "dict_key": dict_key})

file_list += [{"file_name": file_prefix + "-Overall.csv", "dict_key": "Overall"}]

for file in file_list:
    file_name = file["file_name"]
    print("Processing " + file_name)
    complete_results_dict[file["dict_key"]] = parse_csv(file_name, race)

with open(file_prefix + ".json", "w", encoding="utf-8") as json_file:
    json.dump(complete_results_dict, json_file, ensure_ascii=False, indent=4)
