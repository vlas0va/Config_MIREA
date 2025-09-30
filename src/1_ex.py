import tkinter as tk
from tkinter import scrolledtext, Entry, END
import argparse
import os

class ShellEmulator:
    def __init__(self, root, vfs_path=None, script_path=None):
        self.root = root
        self.vfs_path = vfs_path
        self.script_path = script_path

        print(f"VFS Path: {self.vfs_path}")
        print(f"Script Path: {self.script_path}")

        self.root.title("VFS")
        self.root.geometry("800x600")

        self.output = scrolledtext.ScrolledText(root, state='disabled', wrap=tk.WORD, bg="black", fg="white", font=("Courier", 10))
        self.output.pack(expand=True, fill='both', padx=10, pady=10)

        self.input_entry = Entry(root, font=("Courier", 10), bg="black", fg="white", insertbackground="white")
        self.input_entry.pack(fill='x', padx=10, pady=(0, 10))
        self.input_entry.bind("<Return>", self.on_input)

        self.prompt = "$ "

        self.print_output(f"Shell Emulator started.\nType commands like 'ls', 'cd', or 'exit'.\n\n")
        
        if script_path:
            if os.path.exists(script_path):
                self.print_output(f"$ Loading startup script: {script_path}\n")
                self.run_script(script_path)
            else:
                self.print_output(f"Error: Script file not found: {script_path}\n")
                self.show_prompt()
        else:
            self.show_prompt()

    def print_output(self, text):
        self.output.config(state='normal')
        self.output.insert(END, text)
        self.output.config(state='disabled')
        self.output.see(END)

    def show_prompt(self):
        self.output.config(state='normal')
        self.output.insert(END, self.prompt)
        self.output.config(state='disabled')
        self.output.see(END)
        self.input_entry.focus_set()

    def run_script(self, script_path):
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            self.print_output(f"Error reading script: {e}\n")
            self.show_prompt()
            return

        for line in lines:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            self.print_output(f"> {line}\n")

            self.execute_command(line)

        self.show_prompt()

    def execute_command(self, command):
        parts = command.strip().split()
        if not parts:
            return

        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == "exit":
            self.print_output("$ Exiting shell...\n")
            self.root.quit()

        elif cmd == "ls":
            self.print_output(f"Command 'ls' called with args: {args}\n")

        elif cmd == "cd":
            if len(args) != 1:
                self.print_output(f"Error: 'cd' requires exactly one argument.\n")
            else:
                self.print_output(f"Command 'cd' called with arg: {args[0]}\n")

        else:
            self.print_output(f"Error: Unknown command '{cmd}'\n")

    def on_input(self, event):
        command = self.input_entry.get()
        self.input_entry.delete(0, END)

        if not command.strip():
            self.show_prompt()
            return

        self.print_output(command + "\n")
        self.execute_command(command)
        self.show_prompt()
        

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shell Emulator with VFS and script support")

    parser.add_argument(
        '-vfs',
        type=str,
        help='Path to the physical location of VFS (directory)'
    )
    parser.add_argument(
        '-script',
        type=str,
        help='Path to startup script with commands'
    )

    args = parser.parse_args()
    root = tk.Tk()
    app = ShellEmulator(root, vfs_path=args.vfs, script_path=args.script)
    app.run()