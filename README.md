# TOD-O

> A minimalist notebook-style TODO application for Linux.

![TOD-O](assets/tod-o.svg)

## Features

- 🎨 Dark theme (Catppuccin-inspired)
- ✅ Checkbox `~` / `✓` next to each line
- 📁 Project directory selector — TODOs are saved automatically
- 🗑️ Trash icon — clears everything and creates an empty list
- ⌨️ Enter at the end of a line adds a new one
- 💾 Auto-save to `.todo_notebook.json` in the project directory

## Installation

### Quick Run (No installation required)

```bash
python3 todo_app.py
```

### System-wide Installation

```bash
sudo make install
```

The application will appear in your system menu as **TOD-O** with an icon.

### Uninstallation

```bash
sudo make uninstall
```

## Requirements

- Python 3.6+
- GTK 3 (PyGObject)

```bash
# Ubuntu/Debian
sudo apt install python3-gi gir1.2-gtk-3.0

# Fedora
sudo dnf install python3-gobject gtk3

# Arch
sudo pacman -S python-gobject gtk3
```

## Usage

1. Launch the application
2. Select a project directory
3. Start typing your TODOs — every line is saved automatically
4. Click `~` to mark a task as completed (`✓`)
5. Click 🗑️ to clear everything

## License

MIT
