import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import re
from collections import defaultdict

# Damage event types to consider
DAMAGE_EVENTS = {
    'SWING_DAMAGE', 'SPELL_DAMAGE', 'RANGE_DAMAGE', 'SPELL_PERIODIC_DAMAGE'
}

def parse_log(path):
    """Parse a WoW combat log and return mapping of player -> ability -> damage."""
    players = defaultdict(lambda: defaultdict(int))
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if ',' not in line:
                    continue
                prefix, rest = line.split(',', 1)
                tokens = prefix.strip().split()
                if len(tokens) < 2:
                    continue
                event = tokens[-1]
                if event not in DAMAGE_EVENTS:
                    continue

                fields = next(csv.reader([rest]))
                if len(fields) < 2:
                    continue

                source_name = fields[1].strip('"')
                if event == 'SWING_DAMAGE':
                    ability_name = 'Swing'
                    dmg_index = 8
                else:
                    ability_name = fields[9].strip('"') if len(fields) > 9 else 'Unknown'
                    dmg_index = 12

                damage = 0
                if len(fields) > dmg_index and re.fullmatch(r'-?\d+', fields[dmg_index]):
                    damage = int(fields[dmg_index])

                players[source_name][ability_name] += damage
                players[source_name]['__total__'] += damage
    except FileNotFoundError:
        messagebox.showerror('Error', f'Could not open file: {path}')
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
        self.text.config(state=tk.NORMAL)
        self.text.delete('1.0', tk.END)
        total = stats.get('__total__', 0)
        self.text.insert(tk.END, f'Total Damage: {total}\n')
        self.text.insert(tk.END, '\nDamage by Ability:\n')
        for ability, dmg in stats.items():
            if ability == '__total__':
                continue
            self.text.insert(tk.END, f'{ability}: {dmg}\n')
        self.text.config(state=tk.DISABLED)

if __name__ == '__main__':
    root = tk.Tk()
    app = DPSApp(root)
    root.mainloop()
