import json
import os
import sys
from collections import defaultdict
from typing import List, Dict, Any


CATEGORIES_DIR = "categories"
DEFAULT_INPUT_FILE = "input.json"


class ChallengeLoaderError(Exception):
    pass


def load_input_file(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise ChallengeLoaderError(f"Input file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ChallengeLoaderError(f"Invalid JSON in {path}: {e}")

    # print(f"JSON read {data}")

    if not isinstance(data["challenges"], list):
        raise ChallengeLoaderError("Input JSON must be a list of challenge objects")

    return data


def ensure_categories_dir():
    if not os.path.exists(CATEGORIES_DIR):
        os.makedirs(CATEGORIES_DIR)


def load_category_file(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise ChallengeLoaderError(f"Invalid JSON in {path}: {e}")


def save_category_file(path: str, data: Dict[str, Any]):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_next_id(existing_challenges: List[Dict[str, Any]]) -> int:
    if not existing_challenges:
        return 1
    return max(ch["id"] for ch in existing_challenges) + 1


def process_challenges(input_data):

    category = input_data["category"]
    ensure_categories_dir()
    category_file_path = os.path.join(CATEGORIES_DIR, f"{category}.json")

    existing_data = load_category_file(category_file_path)
    if existing_data:
        existing_challenges = existing_data.get("challenges", [])
        # TODO check if versions are the same
    else:
        existing_challenges = []
        existing_data = {
            "version": input_data["version"],
            "challenges": []
        }

    next_id = get_next_id(existing_challenges)

    for challenges in input_data["challenges"]:
        challenges["id"] = next_id
        next_id += 1
        existing_data["challenges"].append(challenges)

    save_category_file(category_file_path, existing_data)
    # print(f"✔ Added {len(input_data["challenges"])} challenge(s) to {category}.json")


def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT_FILE

    try:
        input_data = load_input_file(input_file)
        process_challenges(input_data)
        # print("Done.")
    except ChallengeLoaderError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
