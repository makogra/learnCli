import json
import os
import sys
from collections import defaultdict
from typing import List, Dict, Any


CATEGORIES_DIR = "categories"
DEFAULT_INPUT_FILE = "input.json"


class ChallengeLoaderError(Exception):
    pass


def load_input_file(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        raise ChallengeLoaderError(f"Input file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ChallengeLoaderError(f"Invalid JSON in {path}: {e}")

    if not isinstance(data, list):
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


def process_challenges(input_data: List[Dict[str, Any]]):
    grouped = defaultdict(list)

    # Group by category
    for entry in input_data:
        if "category" not in entry:
            raise ChallengeLoaderError("Each challenge must contain a 'category' field")

        category = entry["category"]

        # Create new dict without category
        challenge = {k: v for k, v in entry.items() if k != "category"}

        grouped[category].append(challenge)

    ensure_categories_dir()

    for category, challenges in grouped.items():
        category_file_path = os.path.join(CATEGORIES_DIR, f"{category}.json")

        existing_data = load_category_file(category_file_path)

        if existing_data:
            existing_challenges = existing_data.get("challenges", [])
        else:
            existing_challenges = []
            existing_data = {
                "category": category,
                "version": 1,
                "challenges": []
            }

        next_id = get_next_id(existing_challenges)

        for challenge in challenges:
            challenge["id"] = next_id
            next_id += 1
            existing_data["challenges"].append(challenge)

        save_category_file(category_file_path, existing_data)

        print(f"✔ Added {len(challenges)} challenge(s) to {category}.json")


def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT_FILE

    try:
        input_data = load_input_file(input_file)
        process_challenges(input_data)
        print("Done.")
    except ChallengeLoaderError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
