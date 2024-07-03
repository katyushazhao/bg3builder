import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

class ScrollableFrame(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)

        self.canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class BG3CharacterPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Baldur's Gate 3 Character Planner")

        self.scrollable_frame = ScrollableFrame(root)
        self.scrollable_frame.pack(fill="both", expand=True)

        # Load classes, races, backgrounds, and skills
        self.classes = self.load_options("classes.json")
        self.races = self.load_options("races.json")
        self.backgrounds = self.load_options("backgrounds.json")
        self.skills = self.load_options("skills.json")

        # Character Name
        self.name_label = tk.Label(self.scrollable_frame.scrollable_frame, text="Character Name:")
        self.name_label.grid(row=0, column=0, padx=10, pady=10)
        self.name_entry = tk.Entry(self.scrollable_frame.scrollable_frame)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)

        # Character Class
        self.class_label = tk.Label(self.scrollable_frame.scrollable_frame, text="Class:")
        self.class_label.grid(row=1, column=0, padx=10, pady=10)
        self.class_combobox = ttk.Combobox(self.scrollable_frame.scrollable_frame, values=self.classes)
        self.class_combobox.grid(row=1, column=1, padx=10, pady=10)

        # Character Race
        self.race_label = tk.Label(self.scrollable_frame.scrollable_frame, text="Race:")
        self.race_label.grid(row=2, column=0, padx=10, pady=10)
        self.race_combobox = ttk.Combobox(self.scrollable_frame.scrollable_frame, values=self.races)
        self.race_combobox.grid(row=2, column=1, padx=10, pady=10)

        # Character Background
        self.background_label = tk.Label(self.scrollable_frame.scrollable_frame, text="Background:")
        self.background_label.grid(row=3, column=0, padx=10, pady=10)
        self.background_combobox = ttk.Combobox(self.scrollable_frame.scrollable_frame, values=self.backgrounds)
        self.background_combobox.grid(row=3, column=1, padx=10, pady=10)

        # Character Skills
        self.skills_label = tk.Label(self.scrollable_frame.scrollable_frame, text="Skills:")
        self.skills_label.grid(row=4, column=0, padx=10, pady=10)
        self.skills_frame = tk.Frame(self.scrollable_frame.scrollable_frame)
        self.skills_frame.grid(row=4, column=1, padx=10, pady=10)
        self.skills_vars = {}
        for skill in self.skills:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(self.skills_frame, text=skill, variable=var)
            cb.pack(anchor='w')
            self.skills_vars[skill] = var

        # Ability Scores
        self.ability_scores = {}
        abilities = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        for i, ability in enumerate(abilities):
            self.ability_scores[ability] = tk.Entry(self.scrollable_frame.scrollable_frame)
            tk.Label(self.scrollable_frame.scrollable_frame, text=f"{ability}:").grid(row=5 + i, column=0, padx=10, pady=5)
            self.ability_scores[ability].grid(row=5 + i, column=1, padx=10, pady=5)

        # Save Button
        self.save_button = tk.Button(self.scrollable_frame.scrollable_frame, text="Save Character", command=self.save_character)
        self.save_button.grid(row=11, column=0, columnspan=2, pady=10)

        # Load Button
        self.load_button = tk.Button(self.scrollable_frame.scrollable_frame, text="Load Characters", command=self.load_characters)
        self.load_button.grid(row=12, column=0, columnspan=2, pady=10)

        # Edit Button
        self.edit_button = tk.Button(self.scrollable_frame.scrollable_frame, text="Edit Selected Character", command=self.edit_character)
        self.edit_button.grid(row=13, column=0, pady=10)

        # Delete Button
        self.delete_button = tk.Button(self.scrollable_frame.scrollable_frame, text="Delete Selected Character", command=self.delete_character)
        self.delete_button.grid(row=13, column=1, pady=10)

        # Character List
        self.character_listbox = tk.Listbox(self.scrollable_frame.scrollable_frame, width=80, height=10)
        self.character_listbox.grid(row=14, column=0, columnspan=2, padx=10, pady=10)
        self.character_listbox.bind("<<ListboxSelect>>", self.on_select)

        # Load presets (origin characters)
        self.load_presets()

        self.selected_index = None

        # Copy Button
        self.copy_button = tk.Button(self.scrollable_frame.scrollable_frame, text="Copy Preset Character", command=self.copy_character)
        self.copy_button.grid(row=15, column=0, columnspan=2, pady=10)

    def copy_character(self):
        if self.selected_index is None:
            messagebox.showwarning("Select Character", "Please select a preset character to copy.")
            return

        if not os.path.exists("presets.json"):
            messagebox.showwarning("File Error", "Presets file (presets.json) not found.")
            return

        with open("presets.json", "r") as presets_file:
            presets = json.load(presets_file)

        if self.selected_index >= len(presets):
            messagebox.showwarning("Index Error", "Selected preset character index is out of range.")
            return

        selected_preset = presets[self.selected_index]

        # Add the selected preset character to characters.json
        character_to_copy = {
            "name": selected_preset["name"],
            "class": selected_preset["class"],
            "race": selected_preset["race"],
            "background": selected_preset["background"],
            "skills": selected_preset["skills"],
            "ability_scores": selected_preset["ability_scores"]
        }

        characters = []
        if os.path.exists("characters.json"):
            with open("characters.json", "r") as characters_file:
                characters = [json.loads(line) for line in characters_file]

        characters.append(character_to_copy)

        with open("characters.json", "w") as characters_file:
            for char in characters:
                json.dump(char, characters_file)
                characters_file.write('\n')

        messagebox.showinfo("Success", "Character copied successfully to characters.json!")
        self.load_characters()

    def load_options(self, filename):
        if os.path.exists(filename):
            with open(filename, "r") as file:
                return json.load(file)
        else:
            return []

    def save_character(self):
        character = {
            "name": self.name_entry.get(),
            "class": self.class_combobox.get(),
            "race": self.race_combobox.get(),
            "background": self.background_combobox.get(),
            "skills": [skill for skill, var in self.skills_vars.items() if var.get()],
            "ability_scores": {key: self.ability_scores[key].get() for key in self.ability_scores}
        }

        if not character["name"] or not character["class"] or not character["race"] or not character["background"] or not character["skills"] or not character["ability_scores"]:
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        characters = []
        if os.path.exists("characters.json"):
            with open("characters.json", "r") as file:
                characters = [json.loads(line) for line in file]

        if self.selected_index is not None:
            characters[self.selected_index] = character
            self.selected_index = None
        else:
            characters.append(character)

        with open("characters.json", "w") as file:
            for char in characters:
                json.dump(char, file)
                file.write('\n')

        messagebox.showinfo("Success", "Character saved successfully!")
        self.clear_entries()
        self.load_characters()

    def load_characters(self):
        self.character_listbox.delete(0, tk.END)

        # Load characters from characters.json
        if os.path.exists("characters.json"):
            with open("characters.json", "r") as file:
                characters = [json.loads(line) for line in file]
                for character in characters:
                    display_text = self.format_character(character)
                    self.character_listbox.insert(tk.END, display_text)

        # Load characters from presets.json
        if os.path.exists("presets.json"):
            with open("presets.json", "r") as file:
                presets = json.load(file)
                for preset in presets:
                    display_text = self.format_character(preset)
                    self.character_listbox.insert(tk.END, display_text)

    def format_character(self, character):
        return f"Name: {character['name']}, Class: {character['class']}, Race: {character['race']}, Background: {character['background']}, Skills: {', '.join(character['skills'])}, Ability Scores: {character['ability_scores']}"

    def load_presets(self):
        if not os.path.exists("presets.json"):
            return

        with open("presets.json", "r") as file:
            presets = json.load(file)
            for preset in presets:
                display_text = f"Name: {preset['name']}, Class: {preset['class']}, Race: {preset['race']}, Background: {preset['background']}, Skills: {', '.join(preset['skills'])}, Ability Scores: {preset['ability_scores']}"
                self.character_listbox.insert(tk.END, display_text)

    def on_select(self, event):
        if self.character_listbox.curselection():
            self.selected_index = self.character_listbox.curselection()[0]
            self.load_character_details()

    def load_character_details(self):
        if self.selected_index is None:
            return

        with open("characters.json", "r") as file:
            characters = [json.loads(line) for line in file]

        if self.selected_index < len(characters):
            character = characters[self.selected_index]
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(tk.END, character["name"])
            self.class_combobox.set(character["class"])
            self.race_combobox.set(character["race"])
            self.background_combobox.set(character["background"])
            for skill, var in self.skills_vars.items():
                var.set(skill in character["skills"])
            for key in self.ability_scores:
                self.ability_scores[key].delete(0, tk.END)
                self.ability_scores[key].insert(tk.END, character["ability_scores"][key])

    def edit_character(self):
        if self.selected_index is None:
            messagebox.showwarning("Select Character", "Please select a character to edit.")
            return

        self.save_character()

    def delete_character(self):
        if self.selected_index is None:
            messagebox.showwarning("Select Character", "Please select a character to delete.")
            return

        with open("characters.json", "r") as file:
            characters = [json.loads(line) for line in file]

        characters.pop(self.selected_index)

        with open("characters.json", "w") as file:
            for char in characters:
                json.dump(char, file)
                file.write('\n')

        messagebox.showinfo("Success", "Character deleted successfully!")
        self.clear_entries()
        self.load_characters()
        self.selected_index = None

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.class_combobox.set('')
        self.race_combobox.set('')
        self.background_combobox.set('')
        for var in self.skills_vars.values():
            var.set(False)
        for key in self.ability_scores:
            self.ability_scores[key].delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")  # Set initial size (width x height)
    app = BG3CharacterPlanner(root)
    root.mainloop()
