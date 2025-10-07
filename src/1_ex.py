import tkinter as tk
from tkinter import scrolledtext, Entry, END
import argparse
import os

def load_vfs(vfs_root):
    if not os.path.exists(vfs_root):
        raise FileNotFoundError(f"VFS directory not found: {vfs_root}")

    def build_node(path):
        node = {'type': 'dir', 'children': {}}
        try:
            for name in os.listdir(path):
                full_path = os.path.join(path, name)
                if os.path.isdir(full_path):
                    node['children'][name] = build_node(full_path)
                else:
                    
                    size = os.path.getsize(full_path)
                    node['children'][name] = {
                        'type': 'file',
                        'size': size
                    }
        except PermissionError:
            pass
        return node
    return build_node(vfs_root)

class ShellEmulator:
    def __init__(self, root, vfs_path=None, script_path=None):
        self.root = root
        self.vfs_path = vfs_path
        self.script_path = script_path

        print(f"VFS Path: {self.vfs_path}")
        print(f"Script Path: {self.script_path}")

        self.vfs = None
        self.current_dir = "/"

        if vfs_path:
            try:
                self.vfs = load_vfs(vfs_path)
                print(f"[INFO] VFS successfully loaded from {vfs_path}")
            except Exception as e:
                self.print_output(f"Error loading VFS: {e}\n")
                self.root.quit()
        else:
            self.print_output("Warning: No VFS provided. Commands like ls will not work.\n")

        self.root.title("VFS")
        self.root.geometry("800x600")

        self.output = scrolledtext.ScrolledText(root, state='disabled', wrap=tk.WORD, bg="black", fg="white", font=("Courier", 10))
        self.output.pack(expand=True, fill='both', padx=10, pady=10)

        self.input_entry = Entry(root, font=("Courier", 10), bg="black", fg="white", insertbackground="white")
        self.input_entry.pack(fill='x', padx=10, pady=(0, 10))
        self.input_entry.bind("<Return>", self.on_input)

        self.prompt = "$ "

        self.print_output(f"Shell Emulator started.\n\n")
        
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

            self.print_output(f"$ {line}\n")

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
            self.cmd_ls(args)

        elif cmd == "cd":
            self.cmd_cd(args)
        
        elif cmd == "pwd":
            self.cmd_pwd(args)

        elif cmd == "find":
            self.cmd_find(args)

        elif cmd == "tail":
            self.cmd_tail(args)

        elif cmd == "mkdir":
            self.cmd_mkdir(args)

        elif cmd == "touch":
            self.cmd_touch(args)

        else:
            self.print_output(f"Error: Unknown command '{cmd}'\n")

    def cmd_ls(self, args):
        if self.vfs is None:
            self.print_output("Error: VFS not loaded.\n")
            return

        if len(args) == 0 or args[0].startswith('-'):
            target_path = self.current_dir
        else:
            target_path = args[0]

        abs_path = self.resolve_path(target_path)
        node = self.get_node_at(abs_path)

        if node is None:
            self.print_output(f"Error: No such directory: {target_path}\n")
        elif node['type'] != 'dir':
            self.print_output(f"Error: Not a directory: {target_path}\n")
        else:
            if not node['children']:
                self.print_output("(empty)\n")
            else:
                for name in sorted(node['children']):
                    child = node['children'][name]
                    if child['type'] == 'dir':
                        self.print_output(f"{name}/\n")
                    else:
                        self.print_output(f"{name}\n")

    def cmd_cd(self, args):
        if self.vfs is None:
            self.print_output("Error: VFS not loaded.\n")
            return

        if len(args) != 1:
            self.print_output("Usage: cd <directory>\n")
            self.show_prompt()
            return

        new_path = self.resolve_path(args[0])
        node = self.get_node_at(new_path)

        if node is None:
            self.print_output(f"Error: No such directory: {args[0]}\n")
        elif node['type'] != 'dir':
            self.print_output(f"Error: Not a directory: {args[0]}\n")
        else:
            self.current_dir = new_path
            self.print_output(f"Changed directory to: {self.current_dir}\n")

    def cmd_pwd(self, args):
        if len(args) > 0:
            self.print_output("Usage: pwd\n")
        else:
            self.print_output(f"{self.current_dir}\n")

    def cmd_find(self, args):
        if len(args) != 1:
            self.print_output("Usage: find <filename>\n")
            self.show_prompt()
            return

        target_name = args[0]

        results = []

        def search(node, current_path):
            if node['type'] == 'dir':
                for name, child in node['children'].items():
                    child_path = f"{current_path}/{name}" if current_path != "/" else f"/{name}"
                    if name == target_name:
                        results.append(child_path)
                    search(child, child_path)

        search(self.vfs, "/")

        if results:
            for path in sorted(results):
                self.print_output(f"{path}\n")
        else:
            self.print_output("(no results)\n")


    def cmd_tail(self, args):
        n = 10  # по умолчанию 10 строк
        file_path = None

        # Обработка флага -n
        i = 0
        while i < len(args):
            if args[i] == '-n' and i + 1 < len(args):
                try:
                    n = int(args[i+1])
                    i += 2
                except:
                    self.print_output("Error: invalid number after -n\n")
                    self.show_prompt()
                    return
            else:
                file_path = args[i]
                i += 1

        if not file_path:
            self.print_output("Usage: tail [-n N] <file>\n")
            self.show_prompt()
            return

        # Разрешаем путь
        abs_path = self.resolve_path(file_path)
        node = self.get_node_at(abs_path)

        if not node:
            self.print_output(f"Error: No such file: {file_path}\n")
        elif node['type'] != 'file':
            self.print_output(f"Error: Is a directory: {file_path}\n")
        else:
            # Читаем настоящий файл с диска
            real_file_path = os.path.join(self.vfs_path, *abs_path.strip("/").split("/"))
            try:
                with open(real_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                last_lines = lines[-n:] if len(lines) >= n else lines
                for line in last_lines:
                    self.print_output(line.rstrip('\n') + '\n')
            except Exception as e:
                self.print_output(f"Error reading file: {e}\n")

    def cmd_touch(self, args):
        if len(args) != 1:
            self.print_output("Usage: touch <filename>\n")
            self.show_prompt()
            return

        # Преобразуем в абсолютный путь
        abs_path = self.resolve_path(args[0])
        parent_path = "/".join(abs_path.strip("/").split("/")[:-1]) or "/"
        filename = abs_path.split("/")[-1]

        parent_node = self.get_node_at(parent_path)

        if not parent_node:
            self.print_output(f"Error: Parent directory not found: {parent_path}\n")
        elif parent_node['type'] != 'dir':
            self.print_output(f"Error: Not a directory: {parent_path}\n")
        elif filename in parent_node['children']:
            self.print_output(f"File already exists: {abs_path}\n")
        else:
            parent_node['children'][filename] = {'type': 'file', 'size': 0}
            self.print_output(f"Empty file created: {abs_path}\n")



    def cmd_mkdir(self, args):
        if len(args) != 1:
            self.print_output("Usage: mkdir <dirname>\n")
            self.show_prompt()
            return

        # Преобразуем в абсолютный путь
        abs_path = self.resolve_path(args[0])
        parent_path = "/".join(abs_path.strip("/").split("/")[:-1]) or "/"
        dirname = abs_path.split("/")[-1]

        # Находим родительскую директорию
        parent_node = self.get_node_at(parent_path)

        if not parent_node:
            self.print_output(f"Error: Parent directory not found: {parent_path}\n")
        elif parent_node['type'] != 'dir':
            self.print_output(f"Error: Not a directory: {parent_path}\n")
        elif dirname in parent_node['children']:
            self.print_output(f"Error: Directory already exists: {dirname}\n")
        else:
            parent_node['children'][dirname] = {'type': 'dir', 'children': {}}
            self.print_output(f"Directory created: {abs_path}\n")


    def resolve_path(self, path):
        """
        Преобразует относительный путь в абсолютный, обрабатывая '.', '..', '/'
        """
        if path == "." or path == "":
            return self.current_dir

        if path.startswith("/"):
            abs_parts = [p for p in path.split("/") if p]
        else:
            current_parts = [p for p in self.current_dir.strip("/").split("/") if p]
            rel_parts = [p for p in path.split("/") if p]
            abs_parts = current_parts + rel_parts

        result = []
        for part in abs_parts:
            if part == "..":
                if result:
                    result.pop()
            elif part == ".":
                continue
            else:
                result.append(part)

        # Формируем путь
        return "/" + "/".join(result) if result else "/"

    def get_node_at(self, path):
        if path == "/":
            return self.vfs

        parts = [p for p in path.split("/") if p]
        current = self.vfs
        for part in parts:
            if current['type'] != 'dir' or part not in current['children']:
                return None
            current = current['children'][part]
        return current

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