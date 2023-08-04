import json
from pathlib import Path

MY_DATA_FOLDER = Path(__file__).parent / "my_data"

all_data = {
    activity_id: data
    for p in MY_DATA_FOLDER.glob("*.json")
    for activity_id, data in json.loads(p.read_text()).items()
}

for activity_id, info in all_data.items():
    print(f"{activity_id=}")
    for thing in info:
        print(thing["type"], thing["original_size"])
