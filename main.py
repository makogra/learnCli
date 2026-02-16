import os
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROGRESS_FILE = BASE_DIR / "progress.json"
# CATEGORIES_DIR = Path("categories")
CATEGORIES_DIR = BASE_DIR / "categories"


# ------------------------
# Utilities
# ------------------------

def load_json(path, default=None):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def pretty_json(data):
    return json.dumps(data, indent=2)


# ------------------------
# Progress handling
# ------------------------

def load_progress():
    default = {
        "active": None,
        "completed": {},
        "hint_index": {}
    }
    return load_json(PROGRESS_FILE, default)


def save_progress(progress):
    save_json(PROGRESS_FILE, progress)


# ------------------------
# Category helpers
# ------------------------

def list_categories():
    if not CATEGORIES_DIR.exists():
        return []
    return [f.stem for f in CATEGORIES_DIR.glob("*.json")]


def load_category(category):
    path = CATEGORIES_DIR / f"{category}.json"
    if not path.exists():
        print(f"Category '{category}' not found.")
        sys.exit(1)
    return load_json(path)


def find_challenge(category_data, challenge_id):
    for ch in category_data.get("challenges", []):
        if ch["id"] == challenge_id:
            return ch
    return None


def first_not_completed(category, progress, category_data):
    completed_ids = progress["completed"].get(category, [])
    for ch in category_data.get("challenges", []):
        if ch["id"] not in completed_ids:
            return ch
    return None


# ------------------------
# Commands
# ------------------------

def cmd_list(args):
    if len(args) == 0:
        cats = list_categories()
        for c in cats:
            print(c)
        return

    category = args[0]
    data = load_category(category)

    for ch in data.get("challenges", []):
        desc = ch.get("description", "")
        print(f"{ch['id']:>3} | {ch['title']} | {desc}")


def cmd_goal(args, progress):
    if len(args) == 0:
        print("Usage: learn goal <category> [id]")
        return

    category = args[0]
    data = load_category(category)

    if len(args) > 1:
        challenge_id = int(args[1])
        challenge = find_challenge(data, challenge_id)
        if not challenge:
            print("Challenge not found.")
            return
    else:
        challenge = first_not_completed(category, progress, data)
        if not challenge:
            print("All challenges completed in this category.")
            return

    progress["active"] = {
        "category": category,
        "id": challenge["id"]
    }
    save_progress(progress)

    print_active_challenge(progress)


def print_active_challenge(progress):
    active = progress.get("active")
    if not active:
        print(f"No active challenge. progress = {progress}")
        return

    category = active["category"]
    challenge_id = active["id"]

    data = load_category(category)
    challenge = find_challenge(data, challenge_id)

    if not challenge:
        print("Active challenge not found.")
        return

    print(f"\n[{category} #{challenge_id}] {challenge['title']}")
    if "description" in challenge:
        print(challenge["description"])

    # for step in challenge.get("steps", []):
    #     print(f"  Step {step['id']}: {step['description']}")


def cmd_hint(progress):
    active = progress.get("active")
    if not active:
        print("No active challenge.")
        return

    category = active["category"]
    cid = active["id"]

    data = load_category(category)
    challenge = find_challenge(data, cid)

    hints = challenge.get("hints") or []
    if not hints:
        print("No hints available.")
        return

    # key = f"{category}:{cid}"
    idx = progress.get(hint_index,0)

    if idx >= len(hints):
        print("Hints: ")
        for h in hints:
            print(h)
        print("No more hints.")
        return

    print("Hint:", hints[idx])
    progress["hint_index"] = idx + 1
    save_progress(progress)


def cmd_check(progress):
    active = progress.get("active")
    if not active:
        print("No active challenge.")
        return

    category = active["category"]
    cid = active["id"]

    data = load_category(category)
    challenge = find_challenge(data, cid)

    for step in challenge.get("steps", []):
        print(f"\nStep {step['id']} solution:")
        print(pretty_json(step.get("verification")))

    print(pretty_json(challenge.get("verification")))


def cmd_ok(progress):
    active = progress.get("active")
    if not active:
        print("No active challenge.")
        return

    category = active["category"]
    cid = active["id"]

    progress["hint_index"] = 0
    progress["completed"].setdefault(category, [])
    if cid not in progress["completed"][category]:
        progress["completed"][category].append(cid)

    print("Marked as completed.")

    # activate next
    data = load_category(category)
    next_ch = first_not_completed(category, progress, data)

    if next_ch:
        progress["active"]["id"] = next_ch["id"]
        print_active_challenge(progress)
    else:
        progress["active"] = None
        print("All challenges completed.")

    save_progress(progress)


def cmd_skip(progress):
    active = progress.get("active")
    if not active:
        print("No active challenge.")
        return

    progress["hint_index"] = 0

    category = active["category"]

    data = load_category(category)
    current_id = active["id"]

    challenges = data.get("challenges", [])
    ids = [c["id"] for c in challenges]

    try:
        idx = ids.index(current_id)
        next_id = ids[idx + 1]
        progress["active"]["id"] = next_id
        # TODO check if next_id isn't already finished (current challenge was skipped before)
        print("Skipped. Next challenge activated.")
    except (ValueError, IndexError):
        print("No next challenge.")
        progress["active"] = None

    save_progress(progress)



def cmd_show():
    print_active_challenge(progress)

# ------------------------
# Main routing
# ------------------------

def main():
    progress = load_progress()

    args = sys.argv[1:]

    if not args:
        print_active_challenge(progress)
        return

    cmd = args[0]

    if cmd == "list":
        cmd_list(args[1:])
    elif cmd == "goal":
        cmd_goal(args[1:], progress)
    elif cmd == "hint":
        cmd_hint(progress)
    elif cmd == "check":
        cmd_check(progress)
    elif cmd == "ok":
        cmd_ok(progress)
    elif cmd == "skip":
        cmd_skip(progress)
    else:
        print("Unknown command.")


if __name__ == "__main__":
    main()
