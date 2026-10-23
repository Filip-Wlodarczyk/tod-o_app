PREFIX ?= /usr/local
BINDIR = $(PREFIX)/bin
DATADIR = $(PREFIX)/share
ICONDIR = $(DATADIR)/icons/hicolor/scalable/apps
DESKTOPDIR = $(DATADIR)/applications
APPDIR = $(DATADIR)/tod-o

.PHONY: install uninstall

install:
	@echo "Instalowanie TOD-O..."
	install -d $(DESTDIR)$(APPDIR)
	install -m 755 todo_app.py $(DESTDIR)$(APPDIR)/todo_app.py
	install -d $(DESTDIR)$(BINDIR)
	@echo '#!/bin/bash' > $(DESTDIR)$(BINDIR)/tod-o
	@echo 'exec python3 $(APPDIR)/todo_app.py "$$@"' >> $(DESTDIR)$(BINDIR)/tod-o
	chmod 755 $(DESTDIR)$(BINDIR)/tod-o
	install -d $(DESTDIR)$(ICONDIR)
	install -m 644 assets/tod-o.svg $(DESTDIR)$(ICONDIR)/tod-o.svg
	install -d $(DESTDIR)$(DESKTOPDIR)
	install -m 644 tod-o.desktop $(DESTDIR)$(DESKTOPDIR)/tod-o.desktop
	@echo "✅ TOD-O zainstalowane! Uruchom: tod-o"

uninstall:
	@echo "Odinstalowywanie TOD-O..."
	rm -f $(DESTDIR)$(BINDIR)/tod-o
	rm -rf $(DESTDIR)$(APPDIR)
	rm -f $(DESTDIR)$(ICONDIR)/tod-o.svg
	rm -f $(DESTDIR)$(DESKTOPDIR)/tod-o.desktop
	@echo "✅ TOD-O odinstalowane."
