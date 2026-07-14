#!/usr/bin/env python3
"""
scoreboard.py — command-line tool to manage data.json for The Scoreboard.

Usage:
  python3 scoreboard.py list
  python3 scoreboard.py add-player "Alice"
  python3 scoreboard.py remove-player "Alice"
  python3 scoreboard.py add-category "Trivia Night"
  python3 scoreboard.py remove-category "Trivia Night"
  python3 scoreboard.py set "Alice" "Trivia Night" 12
  python3 scoreboard.py add "Alice" "Trivia Night" 3      # increments by 3 (use -3 to subtract)
  python3 scoreboard.py publish "your commit message"     # commit + push data.json

Run with no arguments for interactive help.
"""
import json
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime, timezone

DATA_FILE = Path(__file__).parent / "data.json"


def load():
    if not DATA_FILE.exists():
        return {"updated": "", "categories": [], "players": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save(data):
    data["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"✔ saved {DATA_FILE}")


def cmd_list(data, args):
    cats = data["categories"]
    print(f"Categories: {', '.join(cats) if cats else '(none)'}\n")
    if not data["players"]:
        print("No players yet.")
        return
    rows = []
    for name, scores in data["players"].items():
        total = sum(scores.get(c, 0) for c in cats)
        rows.append((total, name, scores))
    rows.sort(reverse=True)
    for total, name, scores in rows:
        detail = ", ".join(f"{c}: {scores.get(c, 0)}" for c in cats)
        print(f"{total:>5}  {name:<20} {detail}")


def cmd_add_player(data, args):
    if args.name in data["players"]:
        print(f"'{args.name}' already exists.")
        return
    data["players"][args.name] = {c: 0 for c in data["categories"]}
    save(data)
    print(f"Added player '{args.name}'.")


def cmd_remove_player(data, args):
    if args.name not in data["players"]:
        print(f"'{args.name}' not found.")
        return
    del data["players"][args.name]
    save(data)
    print(f"Removed player '{args.name}'.")


def cmd_add_category(data, args):
    if args.name in data["categories"]:
        print(f"Category '{args.name}' already exists.")
        return
    data["categories"].append(args.name)
    for scores in data["players"].values():
        scores.setdefault(args.name, 0)
    save(data)
    print(f"Added category '{args.name}'.")


def cmd_remove_category(data, args):
    if args.name not in data["categories"]:
        print(f"Category '{args.name}' not found.")
        return
    data["categories"].remove(args.name)
    for scores in data["players"].values():
        scores.pop(args.name, None)
    save(data)
    print(f"Removed category '{args.name}'.")


def _ensure_player_category(data, player, category):
    if player not in data["players"]:
        print(f"Player '{player}' not found. Add them first with add-player.")
        sys.exit(1)
    if category not in data["categories"]:
        print(f"Category '{category}' not found. Add it first with add-category.")
        sys.exit(1)


def cmd_set(data, args):
    _ensure_player_category(data, args.player, args.category)
    data["players"][args.player][args.category] = args.value
    save(data)
    print(f"Set {args.player} / {args.category} = {args.value}")


def cmd_add(data, args):
    _ensure_player_category(data, args.player, args.category)
    current = data["players"][args.player].get(args.category, 0)
    data["players"][args.player][args.category] = current + args.value
    save(data)
    print(f"{args.player} / {args.category}: {current} -> {current + args.value}")


def cmd_publish(data, args):
    msg = args.message or "update scores"
    try:
        subprocess.run(["git", "add", "data.json"], check=True, cwd=DATA_FILE.parent)
        subprocess.run(["git", "commit", "-m", msg], check=True, cwd=DATA_FILE.parent)
        subprocess.run(["git", "push"], check=True, cwd=DATA_FILE.parent)
        print("✔ pushed to GitHub — the live site will update shortly.")
    except subprocess.CalledProcessError as e:
        print(f"git command failed: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Manage The Scoreboard's data.json")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list").set_defaults(func=cmd_list)

    p = sub.add_parser("add-player"); p.add_argument("name"); p.set_defaults(func=cmd_add_player)
    p = sub.add_parser("remove-player"); p.add_argument("name"); p.set_defaults(func=cmd_remove_player)

    p = sub.add_parser("add-category"); p.add_argument("name"); p.set_defaults(func=cmd_add_category)
    p = sub.add_parser("remove-category"); p.add_argument("name"); p.set_defaults(func=cmd_remove_category)

    p = sub.add_parser("set")
    p.add_argument("player"); p.add_argument("category"); p.add_argument("value", type=int)
    p.set_defaults(func=cmd_set)

    p = sub.add_parser("add")
    p.add_argument("player"); p.add_argument("category"); p.add_argument("value", type=int)
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("publish")
    p.add_argument("message", nargs="?", default=None)
    p.set_defaults(func=cmd_publish)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    data = load()
    args.func(data, args)


if __name__ == "__main__":
    main()
