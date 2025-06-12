#!/usr/bin/env python3
"""Simple DPS analysis tool for World of Warcraft combat logs."""

import argparse
from datetime import datetime
from typing import Optional, Tuple


def parse_timestamp(value: str) -> datetime:
    """Parse combat log timestamp of the form ``M/D H:M:S.ms``."""
    # Combat logs don't include the year, so we prepend 2000 as a dummy year
    return datetime.strptime("2000/" + value, "%Y/%m/%d %H:%M:%S.%f")


def parse_log(path: str, player: Optional[str] = None) -> Tuple[int, float]:
    """Return total damage and duration in seconds for the given player.

    Parameters
    ----------
    path: str
        Path to the combat log file.
    player: Optional[str]
        Name of the player to filter by. If ``None``, all damage events are used.
    """
    total_damage = 0
    start_time = None
    end_time = None

    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            if "," not in line:
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 2:
                continue

            timestamp = parts[0]
            event = parts[1]
            try:
                event_time = parse_timestamp(timestamp)
            except ValueError:
                continue

            if start_time is None:
                start_time = event_time
            end_time = event_time

            source_name = parts[4].strip('"') if len(parts) > 4 else ""
            if player and source_name != player:
                continue

            amount_index = None
            if event == "SWING_DAMAGE":
                amount_index = 11
            elif event in {"RANGE_DAMAGE", "SPELL_DAMAGE", "SPELL_PERIODIC_DAMAGE"}:
                amount_index = 15

            if amount_index is None or len(parts) <= amount_index:
                continue

            try:
                damage = int(parts[amount_index])
            except ValueError:
                continue

            total_damage += damage

    duration = (end_time - start_time).total_seconds() if start_time and end_time else 0.0
    return total_damage, duration


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyse DPS from World of Warcraft logs")
    parser.add_argument("logfile", help="Path to CombatLog.txt")
    parser.add_argument("--player", help="Filter by player name")
    args = parser.parse_args()

    damage, duration = parse_log(args.logfile, args.player)

    if duration <= 0:
        print("No damage events found.")
        return

    dps = damage / duration
    if args.player:
        print(f"Player {args.player} dealt {damage} damage in {duration:.1f}s -> {dps:.2f} DPS")
    else:
        print(f"Total damage: {damage} in {duration:.1f}s -> {dps:.2f} DPS")


if __name__ == "__main__":
    main()
