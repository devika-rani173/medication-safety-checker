
import requests

url = "https://api.fda.gov/drug/label.json"

params = {
    "search": 'openfda.generic_name:"caffeine"',
    "limit": 1,
}

try:
    response = requests.get(url, params=params, timeout=15)

    if response.status_code == 404:
        print("No matching label was found for this query.")
    else:
        response.raise_for_status()
        payload = response.json()

        for label in payload.get("results", []):
            drug_info = label.get("openfda", {})

            print("Generic names:",
                  drug_info.get("generic_name", []))
            print("Brand names:",
                  drug_info.get("brand_name", []))
            print("Interaction information:")
            print(label.get("drug_interactions",
                            ["No interaction section available"]))

except requests.RequestException as error:
    print("API request failed:", error)
except ValueError:
    print("The API response was not valid JSON.")
