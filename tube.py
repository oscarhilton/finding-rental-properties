import requests
import json
import io

tubestops = ["bakerloo", "central", "circle", "district",  "hammersmith-city", "jubilee", "metropolitan", "northern", "piccadilly", "victoria", "waterloo-city"]
overground = [
    "Liberty",
    "Lioness",
    "Mildmay",
    "Suffragette",
    "Weaver",
    "Windrush"
]

tfl_colors = {
    "bakerloo": "#b26300",
    "central": "#dc241f",
    "circle": "#ffd329",
    "district": "#007d32",
    "hammersmith-city": "#f4a9be",
    "jubilee": "#a1a5a7",
    "metropolitan": "#9b0058",
    "northern": "#000000",
    "piccadilly": "#0019a8",
    "victoria": "#0098d8",
    "waterloo-city": "#93ceba",
    "Liberty": "#606667",
    "Lioness": "#ef9600",
    "Mildmay": "#2774ae",
    "Suffragette": "#5ba763",
    "Weaver": "#893b67",
    "Windrush": "#d22730"
}


combined = tubestops + overground

for t in combined:
    try:
        res = requests.get(f"https://api.tfl.gov.uk/Line/{t}/Route/Sequence/outbound")
        json_ = res.json()
        sequences = json_["stopPointSequences"]

        sequence_res = []

        for sequence in sequences:

            sequence_dict = {
                "branchId": sequence["branchId"],
                "direction": sequence["direction"],
                "nextBranchIds": sequence["nextBranchIds"],
                "prevBranchIds": sequence["prevBranchIds"]
            }

            sequences_ = []

            for stop in sequence["stopPoint"]:  

                station_lines = []
                
                for sl in stop["lines"]:
                    station_lines.append(sl["id"])

                station_dict = {
                    "name": stop["name"],
                    "lat": stop["lat"],
                    "lon": stop["lon"],
                    "lines": station_lines,
                }

                sequences_.append(station_dict)

            sequence_dict["sequences"] = sequences_

            sequence_res.append(sequence_dict)

        line = {
            "id": json_["lineId"],
            "hex": tfl_colors[t],
            "sequences": sequence_res,
            "lineStrings": json_["lineStrings"]
        }

        with io.open(f'./maps/{json_["lineId"]}.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(line, ensure_ascii=False, indent=4))

    except Exception as e:
        print(f"[ERROR]: {e}")
