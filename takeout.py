import os
import json
import requests
import argparse


def fetch_json(url, token):
    print(f"Fetching: {url[:100]}...")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def strip_metadata(data):
    if isinstance(data, list):
        return [strip_metadata(item) for item in data]
    elif isinstance(data, dict):
        return {
            key: strip_metadata(value)
            for key, value in data.items()
            if key not in ["links", "permissions", "$type"]
        }
    return data


def write_json(data, filepath):
    print(f"Saving JSON to: {filepath}")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def main(token, output_dir="somtoday_takeout"):
    print("Fetching student ID...")
    student_info = fetch_json("https://api.somtoday.nl/rest/v1/leerlingen", token)
    student_id = student_info["items"][0]["links"][0]["id"]

    print("Fetching placements...")
    placements = strip_metadata(fetch_json(
        f"https://api.somtoday.nl/rest/v1/plaatsingen?leerling={student_id}",
        token,
    ))

    for placement in placements.get("items", []):
        placement_uuid = placement["UUID"]
        print(f"Processing placement: {placement_uuid}")

        averages = strip_metadata(fetch_json(
            f"https://api.somtoday.nl/rest/v1/vakkeuzes/plaatsing/{placement_uuid}/vakgemiddelden",
            token,
        ))

        year_label = f"{placement['opleidingsnaam']}-{placement['leerjaar']}-{placement['stamgroepnaam']}-{placement['schooljaar']['naam'].replace('/', '')}"

        write_json(averages, f"{output_dir}/{year_label}/averages.json")

        for avg in averages.get("gemiddelden", []):
            subject = avg["vakkeuze"]["vak"]
            lichting = avg["vakkeuze"]["lichting"]

            subject_uuid = subject["UUID"]
            subject_slug = subject["naam"].replace("/", "-").replace(" ", "-").lower()
            lichting_uuid = lichting["UUID"]

            print(f"Fetching grades for subject: {subject_slug}")

            query_params = "?additional=vaknaam&additional=resultaatkolom&additional=heeftalternatiefniveau&additional=naamalternatiefniveau&additional=naamstandaardniveau&additional=leerjaar&additional=periodeAfkorting&type=Toetskolom&type=SamengesteldeToetsKolom&type=Werkstukcijferkolom&type=Advieskolom&type=PeriodeGemiddeldeKolom&type=RapportGemiddeldeKolom&type=RapportCijferKolom&type=RapportToetskolom&type=SEGemiddeldeKolom&type=ToetssoortGemiddeldeKolom&sort=desc-geldendResultaatCijferInvoer"
            

            grades_url = f"https://api.somtoday.nl/rest/v1/geldendvoortgangsdossierresultaten/vakresultaten/{student_id}/vak/{subject_uuid}/lichting/{lichting_uuid}{query_params}&plaatsingUuid={placement_uuid}"

            grades = strip_metadata(fetch_json(grades_url, token))
            write_json(
                grades.get("items", grades),
                f"{output_dir}/{year_label}/subjects/{subject_slug}_grades.json",
            )

            exam_url = f"https://api.somtoday.nl/rest/v1/geldendexamendossierresultaten/vakresultaten/{student_id}/vak/{subject_uuid}/lichting/{lichting_uuid}{query_params}&plaatsingUuid={placement_uuid}"
            

            exam_grades = strip_metadata(fetch_json(exam_url, token))
            write_json(
                exam_grades.get("items", exam_grades),
                f"{output_dir}/{year_label}/exam_grades/{subject_slug}_grades.json",
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export Somtoday grades")
    parser.add_argument("token", help="Bearer token")
    parser.add_argument("--output", default="somtoday_takeout", help="Output directory")
    args = parser.parse_args()

    main(args.token, args.output)
