#!/usr/bin/env python3
"""
TOD-O — Minimalist TODO notebook app for Linux.
Dark-themed, Colab-inspired interface.
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Pango, GLib
import os
import json

TODO_FILENAME = ".todo_notebook.json"


class TodoRow(Gtk.Box):
    """A single TODO row — checkbox-like toggle + text entry, styled like a notebook cell."""

    def __init__(self, parent_app, text="", done=False):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.parent_app = parent_app
        self.done = done

        # --- Left gutter: tilde toggle (acts as checkbox) ---
        self.toggle_btn = Gtk.Button(label="~")
        self.toggle_btn.set_size_request(36, 36)
        self.toggle_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.toggle_btn.connect("clicked", self._on_toggle)
        self._style_toggle()
        self.pack_start(self.toggle_btn, False, False, 0)

        # --- Text entry ---
        self.entry = Gtk.Entry()
        self.entry.set_text(text)
        self.entry.set_placeholder_text("Wpisz TODO...")
        self.entry.set_has_frame(False)
        self.entry.connect("changed", self._on_text_changed)
        self.entry.connect("activate", self._on_enter)
        self.pack_start(self.entry, True, True, 0)

        # --- Delete row button ---
        self.del_btn = Gtk.Button(label="✕")
        self.del_btn.set_size_request(30, 30)
        self.del_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.del_btn.set_tooltip_text("Usuń tę linię")
        self.del_btn.connect("clicked", self._on_delete_row)
        self.pack_start(self.del_btn, False, False, 0)

        self.show_all()

    def _style_toggle(self):
        if self.done:
            self.toggle_btn.set_label("✓")
        else:
            self.toggle_btn.set_label("~")

    def _on_toggle(self, btn):
        self.done = not self.done
        self._style_toggle()
        if self.done:
            self.entry.set_sensitive(False)
        else:
            self.entry.set_sensitive(True)
        self.parent_app.save_todos()

    def _on_text_changed(self, entry):
        self.parent_app.save_todos()

    def _on_enter(self, entry):
        self.parent_app.add_todo_row("", False)

    def _on_delete_row(self, btn):
        self.parent_app.remove_todo_row(self)

    def get_data(self):
        return {"text": self.entry.get_text(), "done": self.done}


class TodoApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="TOD-O")
        self.set_default_size(620, 420)
        self.set_resizable(True)

        # Set window icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "tod-o.svg")
        if os.path.exists(icon_path):
            self.set_icon_from_file(icon_path)
        self.project_dir = None
        self.todo_rows = []

        # --- Apply dark CSS ---
        self._apply_css()

        # --- Main vertical box ---
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(self.main_box)

        # --- Header / Toolbar ---
        self.header_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.header_bar.set_margin_top(4)
        self.header_bar.set_margin_bottom(4)
        self.header_bar.set_margin_start(8)
        self.header_bar.set_margin_end(8)
        header_ctx = self.header_bar.get_style_context()
        header_ctx.add_class("toolbar-bar")

        # + TODO button
        self.add_btn = Gtk.Button(label="+ TODO")
        self.add_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.add_btn.get_style_context().add_class("toolbar-btn")
        self.add_btn.set_tooltip_text("Dodaj nową linię TODO")
        self.add_btn.connect("clicked", self._on_add_clicked)
        self.header_bar.pack_start(self.add_btn, False, False, 0)

        # Separator
        sep1 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        self.header_bar.pack_start(sep1, False, False, 4)

        # Markdown label (decorative, like Colab)
        md_label = Gtk.Label(label="Markdown")
        md_label.get_style_context().add_class("toolbar-label")
        self.header_bar.pack_start(md_label, False, False, 0)

        # --- Spacer ---
        spacer = Gtk.Box()
        self.header_bar.pack_start(spacer, True, True, 0)

        # Trash all button
        self.trash_btn = Gtk.Button(label="🗑")
        self.trash_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.trash_btn.get_style_context().add_class("toolbar-btn")
        self.trash_btn.set_tooltip_text("Usuń wszystkie TODO i zacznij od nowa")
        self.trash_btn.connect("clicked", self._on_trash_all)
        self.header_bar.pack_end(self.trash_btn, False, False, 0)

        # Project name label (right side, like "Detecting Kernels")
        self.project_label = Gtk.Label(label="Wybierz projekt")
        self.project_label.get_style_context().add_class("project-label")
        self.project_label_btn = Gtk.Button()
        self.project_label_btn.add(self.project_label)
        self.project_label_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.project_label_btn.get_style_context().add_class("toolbar-btn")
        self.project_label_btn.set_tooltip_text("Zmień katalog projektu")
        self.project_label_btn.connect("clicked", self._on_choose_project)
        self.header_bar.pack_end(self.project_label_btn, False, False, 0)

        self.main_box.pack_start(self.header_bar, False, False, 0)

        # --- Separator line ---
        sep_main = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.main_box.pack_start(sep_main, False, False, 0)

        # --- Scrollable area for TODO rows ---
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.rows_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.rows_box.set_margin_top(6)
        self.rows_box.set_margin_bottom(6)
        self.rows_box.set_margin_start(8)
        self.rows_box.set_margin_end(8)
        self.scroll.add(self.rows_box)
        self.main_box.pack_start(self.scroll, True, True, 0)

        # --- Status bar ---
        self.status_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.status_bar.set_margin_start(8)
        self.status_bar.set_margin_end(8)
        self.status_bar.set_margin_top(2)
        self.status_bar.set_margin_bottom(4)
        self.status_label = Gtk.Label(label="Brak projektu")
        self.status_label.get_style_context().add_class("status-label")
        self.status_bar.pack_start(self.status_label, False, False, 0)
        self.main_box.pack_end(self.status_bar, False, False, 0)

        self.connect("destroy", Gtk.main_quit)
        self.show_all()

        # --- On start: choose project dir ---
        GLib.idle_add(self._on_choose_project, None)

    def _apply_css(self):
        css = b"""
        window {
            background-color: #1e1e2e;
        }
        * {
            color: #cdd6f4;
            font-family: "JetBrains Mono", "Fira Code", "Source Code Pro", monospace;
            font-size: 13px;
        }
        .toolbar-bar {
            background-color: #181825;
            border-bottom: 1px solid #313244;
        }
        .toolbar-btn {
            color: #89b4fa;
            font-weight: bold;
            padding: 2px 8px;
            border-radius: 4px;
        }
        .toolbar-btn:hover {
            background-color: #313244;
        }
        .toolbar-label {
            color: #6c7086;
            padding: 2px 6px;
        }
        .project-label {
            color: #a6e3a1;
            font-weight: bold;
        }
        entry {
            background-color: #1e1e2e;
            color: #cdd6f4;
            border: none;
            border-bottom: 1px solid #313244;
            padding: 6px 8px;
            font-size: 14px;
        }
        entry:focus {
            border-bottom: 1px solid #89b4fa;
            background-color: #181825;
        }
        button {
            background: transparent;
            border: none;
            min-height: 0;
            min-width: 0;
            padding: 4px;
        }
        button:hover {
            background-color: #313244;
            border-radius: 4px;
        }
        separator {
            background-color: #313244;
            min-height: 1px;
            min-width: 1px;
        }
        .status-label {
            color: #585b70;
            font-size: 11px;
        }
        scrolledwindow {
            background-color: #1e1e2e;
        }
        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def _on_choose_project(self, _btn):
        dialog = Gtk.FileChooserDialog(
            title="Wybierz katalog projektu",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )
        dialog.set_default_size(500, 400)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.project_dir = dialog.get_filename()
            project_name = os.path.basename(self.project_dir)
            self.project_label.set_text(project_name)
            self.set_title(f"TOD-O — {project_name}")
            self.status_label.set_text(self.project_dir)
            self._clear_rows()
            self._load_todos()
        dialog.destroy()

    def _on_add_clicked(self, _btn):
        self.add_todo_row("", False)

    def add_todo_row(self, text="", done=False):
        row = TodoRow(self, text=text, done=done)
        self.todo_rows.append(row)
        self.rows_box.pack_start(row, False, False, 0)
        row.entry.grab_focus()
        self.save_todos()

    def remove_todo_row(self, row):
        if row in self.todo_rows:
            self.todo_rows.remove(row)
            self.rows_box.remove(row)
            row.destroy()
            self.save_todos()

    def _clear_rows(self):
        for row in self.todo_rows:
            self.rows_box.remove(row)
            row.destroy()
        self.todo_rows.clear()

    def _on_trash_all(self, _btn):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Usunąć wszystkie TODO?",
        )
        dialog.format_secondary_text("Ta operacja usunie wszystkie wpisy i stworzy pusty list.")
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.YES:
            self._clear_rows()
            self.add_todo_row("", False)
            self.save_todos()

    def save_todos(self):
        if not self.project_dir:
            return
        data = [row.get_data() for row in self.todo_rows]
        path = os.path.join(self.project_dir, TODO_FILENAME)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Błąd zapisu: {e}")

    def _load_todos(self):
        if not self.project_dir:
            return
        path = os.path.join(self.project_dir, TODO_FILENAME)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for item in data:
                    self.add_todo_row(item.get("text", ""), item.get("done", False))
            except Exception as e:
                print(f"Błąd odczytu: {e}")
                self.add_todo_row("", False)
        else:
            self.add_todo_row("", False)


if __name__ == "__main__":
    app = TodoApp()
    Gtk.main()
