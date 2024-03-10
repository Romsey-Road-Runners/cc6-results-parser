import csv
import json
import os
import sys
from pprint import pprint


def parse_csv(file_name, race):
    csvfile = open(file_name, "r")
    if f"Race {race}.csv" in file_name:
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
                    "ageGroup": "Unknown",
                    "position": int(row[f"R{race}"]),
                    "gender": "Unknown",
                }
            )
            continue
        age_cat_results = True
        if not row.get(f"R{race} Age Group"):
            age_cat_results = False

        results_dict = {
            "firstName": row["Firstname"].strip().title(),
            "surname": row["Surname"].strip().title(),
            "club": row["Club"].strip(),
            "position": (
                int(row[f"R{race}"])
                if not age_cat_results
                else int(row[f"R{race} Age Group"])
            ),
        }

        if not age_cat_results:
            results_dict["ageGroup"] = row["Age Group"].strip()

        if row.get("Sex"):
            results_dict["gender"] = row["Sex"]

        results_list.append(results_dict)

    return sorted(results_list, key=lambda d: d["position"])


def parse_team_csv(file_name, race, champ=False):
    csvfile = open(file_name, "r")
    field_names = [
        "Name",
        "R1 Total",
        "R2 Total",
        "R3 Total",
        "R4 Total",
        "R5 Total",
        "R6 Total",
        "R7 Total",
        "Blank",
        "R1",
        "R2",
        "R3",
        "R4",
        "R5",
        "R6",
        "R7",
        "Total",
    ]
    reader = csv.DictReader(csvfile, field_names)
    results_list = []
    for row in reader:
        if "TEAM" in row["Name"]:
            continue

        results_list.append(
            {
                "name": row["Name"].strip(),
                "position": int(row[f"R{race}"]) if row[f"R{race}"] != "ORG" else 0,
                "leaguePosition": int(row["Total"]),
            }
        )
    league_position_counter = 0
    league_previous_total = 0
    team_results_list = []
    for team in sorted(results_list, key=lambda d: d["leaguePosition"]):
        league_total = team["leaguePosition"]
        if league_total != league_previous_total:
            league_position_counter += 1
        league_previous_total = league_total
        team["leaguePosition"] = league_position_counter
        team_results_list.append(team)

    if champ:
        champ_results_list = []
        for team in team_results_list:
            champ_results_list.append(
                {
                    "name": team["name"],
                    "position": team["leaguePosition"],
                }
            )
        return sorted(champ_results_list, key=lambda d: d["position"])
    else:
        return sorted(team_results_list, key=lambda d: d["position"])


def parse_champ_csv(file_name):
    csvfile = open(file_name, "r")
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
        "Best4",
    )
    reader = csv.DictReader(csvfile, field_names)
    results_list = []
    league_position_counter = 0
    for row in reader:
        if row["Firstname"] in ["Firstname", "Fname"] or not row[f"Best4"]:
            continue

        league_position_counter += 1
        results_dict = {
            "firstName": row["Firstname"].strip().title(),
            "surname": row["Surname"].strip().title(),
            "club": row["Club"].strip(),
            "position": league_position_counter,
            "ageGroup": row["Age Group"].strip(),
        }
        results_list.append(results_dict)

    return sorted(results_list, key=lambda d: d["position"])


genders = ["Men", "Women"]
age_cats = ["", "V40", "V50", "V60", "V70"]
race = sys.argv[1]
champ = sys.argv[2]
file_prefix = f"Race-{race}-Results"
file_list = []
complete_results_dict = {}

# Convert xlsx to csv
command = f'soffice --headless --convert-to csv:"Text - txt - csv (StarCalc)":"44,34,UTF8,1,,,,,,,,-1" {file_prefix}.xlsx'
os.system(command)

if not champ:
    # Process results for age cats and overall men and women
    for combination in [
        (gender, age_cat) for gender in genders for age_cat in age_cats
    ]:
        maybe_space = " " if combination[1] else ""
        file_name = f"{file_prefix}-{combination[0]}{maybe_space}{combination[1]}.csv"
        dict_key = (
            f"{combination[0]} {combination[1]}" if maybe_space else f"{combination[0]}"
        )
        file_list.append({"file_name": file_name, "dict_key": dict_key})

    # Cheekily add overall results file into the mix
    file_list += [
        {"file_name": f"{file_prefix}-Race {race}.csv", "dict_key": "Overall Results"}
    ]

    for file in file_list:
        file_name = file["file_name"]
        print("Processing " + file_name)
        complete_results_dict[file["dict_key"]] = parse_csv(file_name, race)

    # Process team results
    for team_file in [
        {
            "file_name": f"{file_prefix}-{gender}s Team.csv",
            "dict_key": f"{gender}s Teams",
        }
        for gender in ["Men", "Women"]
    ]:
        file_name = team_file["file_name"]
        print("Processing " + file_name)
        complete_results_dict[team_file["dict_key"]] = parse_team_csv(
            team_file["file_name"], race
        )
else:
    # Process champ results
    for champ_file in [
        {"file_name": f"{file_prefix}-{gender} Champ.csv", "dict_key": f"{gender}"}
        for gender in ["Men", "Women"]
    ]:
        file_name = champ_file["file_name"]
        print("Processing " + file_name)
        complete_results_dict[champ_file["dict_key"]] = parse_champ_csv(
            champ_file["file_name"]
        )

    # Process team results
    for team_file in [
        {
            "file_name": f"{file_prefix}-{gender}s Team.csv",
            "dict_key": f"{gender}s Teams",
        }
        for gender in ["Men", "Women"]
    ]:
        file_name = team_file["file_name"]
        print("Processing " + file_name)
        complete_results_dict[team_file["dict_key"]] = parse_team_csv(
            team_file["file_name"], race, champ=True
        )


# Write out the monster JSON file
with open(file_prefix + ".json", "w", encoding="utf-8") as json_file:
    json.dump(complete_results_dict, json_file, ensure_ascii=False, indent=4)
