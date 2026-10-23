# TOD-O

> Minimalistyczna aplikacja TODO w stylu notebooka dla Linuksa.

![TOD-O](assets/tod-o.svg)

## Funkcje

- 🎨 Ciemny motyw (Catppuccin-inspired)
- ✅ Checkbox `~` / `✓` przy każdej linii
- 📁 Wybór katalogu projektu — TODO zapisuje się automatycznie
- 🗑️ Ikona kosza — czyści wszystko i tworzy pustą listę
- ⌨️ Enter na końcu linii dodaje nową
- 💾 Auto-zapis do `.todo_notebook.json` w katalogu projektu

## Instalacja

### Szybka (bez instalacji)

```bash
python3 todo_app.py
```

### Instalacja systemowa

```bash
sudo make install
```

Aplikacja pojawi się w menu jako **TOD-O** z ikoną.

### Odinstalowanie

```bash
sudo make uninstall
```

## Wymagania

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

## Użycie

1. Uruchom aplikację
2. Wybierz katalog projektu
3. Pisz TODO — każda linia zapisuje się automatycznie
4. Kliknij `~` by oznaczyć jako zrobione (`✓`)
5. Kliknij 🗑️ by wyczyścić wszystko

## Licencja

MIT
