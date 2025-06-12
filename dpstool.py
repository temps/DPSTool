import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import re
from collections import defaultdict
from datetime import datetime

from simcraft import fetch_raid_dps

# Damage event types to consider
DAMAGE_EVENTS = {
    'SWING_DAMAGE', 'SPELL_DAMAGE', 'RANGE_DAMAGE', 'SPELL_PERIODIC_DAMAGE'
}

# Additional event types
CAST_EVENTS = DAMAGE_EVENTS | {'SPELL_CAST_SUCCESS'}
BUFF_APPLIED = {'SPELL_AURA_APPLIED'}

DEFENSIVES = {
    'Divine Shield', 'Ice Block', 'Barkskin', 'Shield Wall',
}

MOVEMENT_ABILITIES = {
    'Blink', 'Dash', 'Charge', 'Heroic Leap',
}

CONSUMABLE_HINTS = {'Potion', 'Flask', 'Rune', 'Oil', 'Food'}
EXPECTED_CONSUMABLES = {'Potion', 'Flask'}

def parse_log(path):
    """Parse a WoW combat log and return per-player statistics."""
    def _player():
        return {
            'damage': defaultdict(int),
            'casts': [],
            'defensives': 0,
            'movement': 0,
            'consumables': set(),
            'enchant_events': set(),
        }

    players = defaultdict(_player)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if ',' not in line:
                    continue
                prefix, rest = line.split(',', 1)
                tokens = prefix.strip().split()
                if len(tokens) < 3:
                    continue
                ts = ' '.join(tokens[:2])
                event = tokens[-1]
                try:
                    time = datetime.strptime(ts, '%m/%d %H:%M:%S.%f')
                except ValueError:
                    continue

                fields = next(csv.reader([rest]))
                if len(fields) < 2:
                    continue

                source = fields[1].strip('"')
                player = players[source]

                ability = None
                if event in CAST_EVENTS:
                    if event == 'SWING_DAMAGE':
                        ability = 'Swing'
                    else:
                        ability = fields[9].strip('"') if len(fields) > 9 else 'Unknown'
                    player['casts'].append((time, ability))

                if event in DAMAGE_EVENTS:
                    dmg_index = 8 if event == 'SWING_DAMAGE' else 12
                    dmg = 0
                    if len(fields) > dmg_index and re.fullmatch(r'-?\d+', fields[dmg_index]):
                        dmg = int(fields[dmg_index])
                    player['damage'][ability] += dmg
                    player['damage']['__total__'] += dmg

                if event in BUFF_APPLIED:
                    ability = fields[9].strip('"') if len(fields) > 9 else 'Unknown'
                    if any(hint.lower() in ability.lower() for hint in CONSUMABLE_HINTS):
                        player['consumables'].add(ability)
                    if ability in DEFENSIVES:
                        player['defensives'] += 1
                    if ability in MOVEMENT_ABILITIES:
                        player['movement'] += 1

                if event == 'ENCHANT_APPLIED':
                    ability = fields[9].strip('"') if len(fields) > 9 else 'Unknown'
                    player['enchant_events'].add(ability)
    except FileNotFoundError:
        messagebox.showerror('Error', f'Could not open file: {path}')

    # Post process downtime, rotation and consumables
    for data in players.values():
        casts = sorted(data['casts'])
        data['rotation'] = [a for _, a in casts]
        downtime = 0.0
        for (t1, _), (t2, _) in zip(casts, casts[1:]):
            gap = (t2 - t1).total_seconds()
            if gap > 2:
                downtime += gap - 2
        data['downtime'] = downtime
        data['consumables_missed'] = [c for c in EXPECTED_CONSUMABLES
                                      if not any(c.lower() in x.lower() for x in data['consumables'])]
        data['missing_enchants'] = not data['enchant_events']

    return players

class DPSApp:
    def __init__(self, root):
        self.root = root
        root.title('WoW DPS Analyzer')
        root.geometry('600x400')

        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.log_button = tk.Button(self.frame, text='Open Combat Log', command=self.load_log)
        self.log_button.pack(pady=5)

        self.player_var = tk.StringVar()
        self.player_menu = tk.OptionMenu(self.frame, self.player_var, [])
        self.player_menu.pack(pady=5)

        self.analyze_button = tk.Button(self.frame, text='Analyze', command=self.show_stats, state=tk.DISABLED)
        self.analyze_button.pack(pady=5)

        self.text = tk.Text(self.frame, state=tk.DISABLED)
        self.text.pack(fill=tk.BOTH, expand=True)

        self.players = {}

    def load_log(self):
        path = filedialog.askopenfilename(title='Select Combat Log')
        if not path:
            return
        self.players = parse_log(path)
        if not self.players:
            messagebox.showinfo('Info', 'No players found in log')
            return
        menu = self.player_menu['menu']
        menu.delete(0, 'end')
        for player in self.players.keys():
            menu.add_command(label=player, command=tk._setit(self.player_var, player))
        self.player_var.set(next(iter(self.players)))
        self.analyze_button.config(state=tk.NORMAL)

    def show_stats(self):
        player = self.player_var.get()
        if not player or player not in self.players:
            return
        stats = self.players[player]
        simc = fetch_raid_dps()

        self.text.config(state=tk.NORMAL)
        self.text.delete('1.0', tk.END)

        if simc.get('raid_dps'):
            self.text.insert(tk.END, f"Raid DPS (SimC): {simc['raid_dps']}\n\n")

        total = stats['damage'].get('__total__', 0)
        self.text.insert(tk.END, f'Total Damage: {total}\n')
        self.text.insert(tk.END, f'Downtime: {stats["downtime"]:.1f}s\n')
        self.text.insert(tk.END, f'Defensives used: {stats["defensives"]}\n')
        self.text.insert(tk.END, f'Movement abilities used: {stats["movement"]}\n')
        consumables = ', '.join(stats['consumables']) or 'None'
        self.text.insert(tk.END, f'Consumables used: {consumables}\n')
        if stats['consumables_missed']:
            self.text.insert(tk.END, 'Missing consumables: ' + ', '.join(stats['consumables_missed']) + '\n')
        if stats['missing_enchants']:
            self.text.insert(tk.END, 'Missing enchants detected\n')

        self.text.insert(tk.END, '\nDamage by Ability:\n')
        for ability, dmg in stats['damage'].items():
            if ability == '__total__':
                continue
            self.text.insert(tk.END, f'{ability}: {dmg}\n')

        if stats['rotation']:
            self.text.insert(tk.END, '\nRotation:\n' + ', '.join(stats['rotation']))

        self.text.config(state=tk.DISABLED)

if __name__ == '__main__':
    root = tk.Tk()
    app = DPSApp(root)
    root.mainloop()
