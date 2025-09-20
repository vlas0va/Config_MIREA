import tkinter as tk
from tkinter import scrolledtext, Entry, END

class ShellEmulator:
    def __init__(self, root):
        self.root = root
        self.root.title("VFS")
        self.root.geometry("800x600")

        self.output = scrolledtext.ScrolledText(root, state='disabled', wrap=tk.WORD, bg="black", fg="white", font=("Courier", 10))
        self.output.pack(expand=True, fill='both', padx=10, pady=10)

        self.input_entry = Entry(root, font=("Courier", 10), bg="black", fg="white", insertbackground="white")
        self.input_entry.pack(fill='x', padx=10, pady=(0, 10))
        self.input_entry.bind("<Return>", self.on_input)

        self.prompt = "$ "

        self.print_output(f"Shell Emulator started.\nType commands like 'ls', 'cd', or 'exit'.\n\n")
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

    def on_input(self, event):
        command = self.input_entry.get()
        self.input_entry.delete(0, END)

        if not command.strip():
            self.show_prompt()
            return

        self.print_output(command + "\n")

        parts = command.strip().split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == "exit":
            self.print_output("$ Exiting shell...\n")
            self.root.quit()

        elif cmd == "ls":
            self.print_output(f"Command 'ls' called with args: {args}\n")
            self.show_prompt()

        elif cmd == "cd":
            if len(args) != 1:
                self.print_output(f"Error: 'cd' requires exactly one argument.\n")
            else:
                self.print_output(f"Command 'cd' called with arg: {args[0]}\n")
            self.show_prompt()

        else:
            self.print_output(f"Error: Unknown command '{cmd}'\n")
            self.show_prompt()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = ShellEmulator(root)
    app.run()