from __future__ import annotations

import hashlib
import html
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QObject, QTimer, Qt, pyqtSignal, QUrl
from PyQt6.QtGui import QAction, QCloseEvent, QDesktopServices, QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout,
    QFrame, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QMessageBox, QPushButton, QSpinBox, QSplitter,
    QStatusBar, QSystemTrayIcon, QTabWidget, QTextBrowser, QVBoxLayout, QWidget,
)

from eliza_engine import ElizaEngine
from steam_backend import SteamBackend, SteamBackendError
from storage import APP_DIR, LOG_DIR, append_chat_log, load_config, save_config
from themes import THEMES


APP_NAME = "Game Troll Buster"
VERSION = "0.2.0"


class BackendSignals(QObject):
    status = pyqtSignal(str)
    message = pyqtSignal(str, str, str)
    friends = pyqtSignal(object)
    auth_required = pyqtSignal(str)


class OptionsDialog(QDialog):
    settings_changed = pyqtSignal(dict)

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Options")
        self.setMinimumSize(560, 430)
        self.config = dict(config)

        outer = QVBoxLayout(self)
        tabs = QTabWidget()
        outer.addWidget(tabs, 1)

        # Appearance
        appearance = QWidget()
        af = QFormLayout(appearance)
        self.theme = QComboBox()
        self.theme.addItems(THEMES.keys())
        self.theme.setCurrentText(self.config.get("theme", "Cyber Dark"))
        self.theme.currentTextChanged.connect(self._preview)
        af.addRow("Theme:", self.theme)
        theme_hint = QLabel("Theme changes are previewed immediately.")
        theme_hint.setWordWrap(True)
        af.addRow("", theme_hint)
        tabs.addTab(appearance, "Appearance")

        # Responder
        responder = QWidget()
        rf = QFormLayout(responder)
        self.mode = QComboBox()
        self.mode.addItems(["Classic ELIZA", "Dry Counter-Questions", "Persistent Mirror"])
        self.mode.setCurrentText(self.config.get("eliza_mode", "Classic ELIZA"))

        self.delay_min = QSpinBox()
        self.delay_min.setRange(3, 3600)
        self.delay_min.setSuffix(" sec")
        self.delay_min.setValue(int(self.config.get("delay_min", 15)))

        self.delay_max = QSpinBox()
        self.delay_max.setRange(3, 7200)
        self.delay_max.setSuffix(" sec")
        self.delay_max.setValue(int(self.config.get("delay_max", 90)))

        self.max_replies = QSpinBox()
        self.max_replies.setRange(1, 10000)
        self.max_replies.setValue(int(self.config.get("max_replies", 250)))

        self.auto_stop = QSpinBox()
        self.auto_stop.setRange(1, 168)
        self.auto_stop.setSuffix(" hours")
        self.auto_stop.setValue(int(self.config.get("auto_stop_hours", 12)))

        rf.addRow("ELIZA personality:", self.mode)
        rf.addRow("Minimum reply delay:", self.delay_min)
        rf.addRow("Maximum reply delay:", self.delay_max)
        rf.addRow("Maximum replies / contact:", self.max_replies)
        rf.addRow("Session auto-stop:", self.auto_stop)
        tabs.addTab(responder, "Responder")

        # Logging
        logging_tab = QWidget()
        lf = QFormLayout(logging_tab)
        self.store_logs = QCheckBox("Save one readable .txt transcript per contact/chat")
        self.store_logs.setChecked(bool(self.config.get("store_logs", True)))
        self.timestamps = QCheckBox("Include timestamps in text transcripts")
        self.timestamps.setChecked(bool(self.config.get("show_timestamps", False)))
        lf.addRow(self.store_logs)
        lf.addRow(self.timestamps)

        log_path = QLabel(str(LOG_DIR))
        log_path.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lf.addRow("Log folder:", log_path)
        open_logs = QPushButton("Open log folder")
        open_logs.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(LOG_DIR))))
        lf.addRow("", open_logs)
        tabs.addTab(logging_tab, "Logging")

        # Safety
        safety = QWidget()
        sf = QFormLayout(safety)
        self.confirm_enable = QCheckBox("Ask for confirmation before enabling ELIZA for a contact")
        self.confirm_enable.setChecked(bool(self.config.get("confirm_before_enable", False)))
        sf.addRow(self.confirm_enable)

        note = QLabel(
            "Game Troll Buster never starts conversations. The responder only reacts to "
            "incoming messages from contacts you explicitly enable. Reply caps and an "
            "auto-stop are always available to prevent accidental endless bot loops."
        )
        note.setWordWrap(True)
        sf.addRow(note)
        tabs.addTab(safety, "Safety")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self._defaults)
        outer.addWidget(buttons)

    def values(self) -> dict:
        lo = min(self.delay_min.value(), self.delay_max.value())
        hi = max(self.delay_min.value(), self.delay_max.value())
        return {
            "theme": self.theme.currentText(),
            "eliza_mode": self.mode.currentText(),
            "delay_min": lo,
            "delay_max": hi,
            "max_replies": self.max_replies.value(),
            "auto_stop_hours": self.auto_stop.value(),
            "store_logs": self.store_logs.isChecked(),
            "show_timestamps": self.timestamps.isChecked(),
            "confirm_before_enable": self.confirm_enable.isChecked(),
        }

    def _preview(self):
        values = self.values()
        self.settings_changed.emit(values)

    def _save(self):
        self.settings_changed.emit(self.values())
        self.accept()

    def _defaults(self):
        self.theme.setCurrentText("Cyber Dark")
        self.mode.setCurrentText("Classic ELIZA")
        self.delay_min.setValue(15)
        self.delay_max.setValue(90)
        self.max_replies.setValue(250)
        self.auto_stop.setValue(12)
        self.store_logs.setChecked(True)
        self.timestamps.setChecked(False)
        self.confirm_enable.setChecked(False)
        self.settings_changed.emit(self.values())


class SteamLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connect to Steam")
        self.setMinimumWidth(440)
        form = QFormLayout(self)

        self.user = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.code = QLineEdit()
        self.code.setPlaceholderText("Optional on first attempt")

        form.addRow("Account name:", self.user)
        form.addRow("Password:", self.password)
        form.addRow("Steam Guard code:", self.code)

        note = QLabel(
            "Your password and Steam Guard code are not written to Game Troll Buster's "
            "config file. Steam session/sentry data may be kept locally by the Steam library."
        )
        note.setWordWrap(True)
        form.addRow(note)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def values(self):
        return self.user.text().strip(), self.password.text(), self.code.text().strip()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.engine = ElizaEngine()
        self.apply_engine_mode()

        self.signals = BackendSignals()
        self.backend = SteamBackend(
            on_status=self.signals.status.emit,
            on_message=self.signals.message.emit,
            on_friends=self.signals.friends.emit,
            on_auth_required=self.signals.auth_required.emit,
        )

        self.demo_mode = True
        self.paused = False
        self.contacts: dict[str, dict] = {}
        self.transcripts: dict[str, list[tuple[str, str, str]]] = {}
        self.seen_messages: set[str] = set()
        self.session_started = time.time()
        self.last_credentials: tuple[str, str] | None = None

        self.signals.status.connect(self.set_status)
        self.signals.message.connect(self.on_incoming)
        self.signals.friends.connect(self.populate_friends)
        self.signals.auth_required.connect(self.on_auth_required)

        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.resize(1280, 800)
        icon_path = Path(__file__).parent / "assets" / "game_troll_buster.svg"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self._build_ui()
        self._build_tray()
        self.apply_theme(self.config.get("theme", "Cyber Dark"))
        self._load_demo_contacts()

    # ---------------- UI ----------------

    def _build_ui(self):
        self._build_menu()

        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 8)
        root.setSpacing(10)
        self.setCentralWidget(central)

        header = QFrame()
        header.setObjectName("HeaderFrame")
        hl = QHBoxLayout(header)
        title_box = QVBoxLayout()
        title = QLabel("GAME TROLL BUSTER")
        title.setObjectName("AppTitle")
        tag = QLabel("ELIZA-powered conversational sinkhole for selected incoming Steam chats")
        tag.setObjectName("TagLine")
        title_box.addWidget(title)
        title_box.addWidget(tag)
        hl.addLayout(title_box, 1)

        self.status_badge = QLabel("DEMO MODE")
        self.status_badge.setObjectName("StatusBadge")
        hl.addWidget(self.status_badge)
        root.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter, 1)

        # Contacts
        left = QGroupBox("TARGET CONTACTS")
        ll = QVBoxLayout(left)
        self.contact_list = QListWidget()
        self.contact_list.currentItemChanged.connect(self.on_contact_selected)
        ll.addWidget(self.contact_list, 1)

        self.enable_contact = QCheckBox("Deploy ELIZA on selected contact")
        self.enable_contact.stateChanged.connect(self.toggle_selected_contact)
        ll.addWidget(self.enable_contact)

        self.contact_stats = QLabel("Replies: 0")
        ll.addWidget(self.contact_stats)
        splitter.addWidget(left)

        # Chat
        middle = QGroupBox("CHAT FEED")
        ml = QVBoxLayout(middle)
        self.chat_title = QLabel("No contact selected")
        self.chat_title.setFont(QFont("", 11, QFont.Weight.Bold))
        ml.addWidget(self.chat_title)

        self.chat = QTextBrowser()
        self.chat.setOpenExternalLinks(False)
        ml.addWidget(self.chat, 1)

        simulator = QHBoxLayout()
        self.sim_input = QLineEdit()
        self.sim_input.setPlaceholderText("Simulate an incoming troll message …")
        self.sim_input.returnPressed.connect(self.simulate_incoming)
        simulator.addWidget(self.sim_input, 1)
        sim_btn = QPushButton("SIMULATE INCOMING")
        sim_btn.clicked.connect(self.simulate_incoming)
        simulator.addWidget(sim_btn)
        ml.addLayout(simulator)
        splitter.addWidget(middle)

        # Control deck
        right = QGroupBox("CONTROL DECK")
        rl = QVBoxLayout(right)

        self.mode_value = QLabel()
        self.connection_value = QLabel("Steam: disconnected")
        self.connection_value.setWordWrap(True)
        rl.addWidget(self.mode_value)
        rl.addWidget(self.connection_value)

        self.pause_btn = QPushButton("PAUSE RESPONDER")
        self.pause_btn.setObjectName("DangerButton")
        self.pause_btn.clicked.connect(self.toggle_pause)
        rl.addWidget(self.pause_btn)

        connect_btn = QPushButton("CONNECT STEAM")
        connect_btn.setObjectName("PrimaryButton")
        connect_btn.clicked.connect(self.connect_steam)
        rl.addWidget(connect_btn)

        disconnect_btn = QPushButton("DISCONNECT")
        disconnect_btn.clicked.connect(self.disconnect_steam)
        rl.addWidget(disconnect_btn)

        options_btn = QPushButton("OPTIONS")
        options_btn.clicked.connect(self.open_options)
        rl.addWidget(options_btn)

        logs_btn = QPushButton("OPEN CHAT LOGS")
        logs_btn.clicked.connect(self.open_logs)
        rl.addWidget(logs_btn)

        info = QLabel(
            "Responder rule: incoming messages only.\n\n"
            "Enable ELIZA separately for each contact. Disabled contacts are never auto-replied to."
        )
        info.setWordWrap(True)
        rl.addWidget(info)
        rl.addStretch(1)

        splitter.addWidget(right)
        splitter.setSizes([270, 700, 260])

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.set_status("Ready. Demo mode is active.")
        self.update_mode_labels()

    def _build_menu(self):
        file_menu = self.menuBar().addMenu("&File")
        open_logs = QAction("Open chat logs", self)
        open_logs.triggered.connect(self.open_logs)
        file_menu.addAction(open_logs)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        steam_menu = self.menuBar().addMenu("&Steam")
        connect_action = QAction("Connect …", self)
        connect_action.triggered.connect(self.connect_steam)
        steam_menu.addAction(connect_action)
        disconnect_action = QAction("Disconnect", self)
        disconnect_action.triggered.connect(self.disconnect_steam)
        steam_menu.addAction(disconnect_action)

        tools_menu = self.menuBar().addMenu("&Tools")
        pause_action = QAction("Pause / Resume responder", self)
        pause_action.triggered.connect(self.toggle_pause)
        tools_menu.addAction(pause_action)
        options_action = QAction("Options …", self)
        options_action.triggered.connect(self.open_options)
        tools_menu.addAction(options_action)

        help_menu = self.menuBar().addMenu("&Help")
        about = QAction("About", self)
        about.triggered.connect(self.show_about)
        help_menu.addAction(about)

    def _build_tray(self):
        self.tray = QSystemTrayIcon(self.windowIcon(), self)
        tray_menu = self.menuBar().addMenu("")  # dummy parent not used
        tray_menu.menuAction().setVisible(False)
        # Use standalone menu via QMenu import lazily
        from PyQt6.QtWidgets import QMenu
        menu = QMenu()
        show_action = menu.addAction("Show Game Troll Buster")
        show_action.triggered.connect(self.show_and_raise)
        pause_action = menu.addAction("Pause / Resume responder")
        pause_action.triggered.connect(self.toggle_pause)
        menu.addSeparator()
        quit_action = menu.addAction("Exit")
        quit_action.triggered.connect(QApplication.instance().quit)
        self.tray.setContextMenu(menu)
        self.tray.setToolTip(APP_NAME)
        self.tray.activated.connect(lambda reason: self.show_and_raise() if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None)
        self.tray.show()

    # ---------------- Settings ----------------

    def open_options(self):
        original = dict(self.config)
        dlg = OptionsDialog(self.config, self)
        dlg.settings_changed.connect(self.apply_options)
        result = dlg.exec()
        if result != QDialog.DialogCode.Accepted:
            self.config = original
            self.apply_theme(self.config.get("theme", "Cyber Dark"))
            self.apply_engine_mode()
            self.update_mode_labels()

    def apply_options(self, values: dict):
        self.config.update(values)
        self.apply_theme(self.config.get("theme", "Cyber Dark"))
        self.apply_engine_mode()
        self.update_mode_labels()
        save_config(self.config)

    def apply_engine_mode(self):
        label = self.config.get("eliza_mode", "Classic ELIZA")
        mode_map = {
            "Classic ELIZA": "classic",
            "Dry Counter-Questions": "dry",
            "Persistent Mirror": "persistent",
        }
        self.engine.set_mode(mode_map.get(label, "classic"))

    def apply_theme(self, name: str):
        theme = THEMES.get(name, THEMES["Cyber Dark"])
        QApplication.instance().setStyleSheet(theme)

    def update_mode_labels(self):
        self.mode_value.setText(
            f"Responder: {self.config.get('eliza_mode', 'Classic ELIZA')}\n"
            f"Theme: {self.config.get('theme', 'Cyber Dark')}\n"
            f"Delay: {self.config.get('delay_min', 15)}–{self.config.get('delay_max', 90)} sec"
        )

    # ---------------- Contacts ----------------

    def _load_demo_contacts(self):
        self.contacts = {
            "demo-troll": {"name": "Random Troll [DEMO]", "enabled": True, "replies": 0},
            "demo-friend": {"name": "Normal Friend [DEMO]", "enabled": False, "replies": 0},
        }
        self.refresh_contact_list()
        if self.contact_list.count():
            self.contact_list.setCurrentRow(0)

    def selected_steam_id(self):
        item = self.contact_list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def refresh_contact_list(self):
        selected = self.selected_steam_id()
        self.contact_list.blockSignals(True)
        self.contact_list.clear()
        for sid, data in sorted(self.contacts.items(), key=lambda kv: kv[1]["name"].lower()):
            state = "▶" if data.get("enabled") else "○"
            item = QListWidgetItem(f"{state} {data['name']}")
            item.setData(Qt.ItemDataRole.UserRole, sid)
            self.contact_list.addItem(item)
            if sid == selected:
                self.contact_list.setCurrentItem(item)
        self.contact_list.blockSignals(False)

        if self.contact_list.currentItem() is None and self.contact_list.count():
            self.contact_list.setCurrentRow(0)
        self.on_contact_selected(self.contact_list.currentItem(), None)

    def on_contact_selected(self, current, previous):
        sid = self.selected_steam_id()
        if not sid:
            self.chat_title.setText("No contact selected")
            return
        data = self.contacts[sid]
        self.enable_contact.blockSignals(True)
        self.enable_contact.setChecked(bool(data.get("enabled")))
        self.enable_contact.blockSignals(False)
        self.contact_stats.setText(f"Replies this session: {data.get('replies', 0)}")
        self.chat_title.setText(data["name"])
        self.render_transcript(sid)

    def toggle_selected_contact(self):
        sid = self.selected_steam_id()
        if not sid:
            return

        desired = self.enable_contact.isChecked()
        if desired and self.config.get("confirm_before_enable", False):
            answer = QMessageBox.question(
                self,
                "Enable ELIZA?",
                f"Enable automatic ELIZA replies for\n{self.contacts[sid]['name']}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                self.enable_contact.blockSignals(True)
                self.enable_contact.setChecked(False)
                self.enable_contact.blockSignals(False)
                return

        self.contacts[sid]["enabled"] = desired
        self.save_contact_settings()
        self.refresh_contact_list()

    def save_contact_settings(self):
        self.config["contact_configs"] = {
            sid: {"enabled": bool(data.get("enabled", False)), "name": data.get("name", sid)}
            for sid, data in self.contacts.items()
            if not sid.startswith("demo-")
        }
        save_config(self.config)

    # ---------------- Chat ----------------

    def render_transcript(self, sid: str):
        pieces = []
        for ts, who, text in self.transcripts.get(sid, []):
            label = "Troll" if who == "in" else "ELIZA"
            badge = "▶" if who == "out" else "●"
            pieces.append(
                f"<div style='margin:8px 2px 14px 2px;'>"
                f"<b>{badge} {html.escape(label)}</b>"
                f"<span style='opacity:0.65;'> &nbsp; {html.escape(ts)}</span><br>"
                f"<span>{html.escape(text)}</span></div>"
            )
        self.chat.setHtml("".join(pieces) or "<i>No messages yet.</i>")
        self.chat.verticalScrollBar().setValue(self.chat.verticalScrollBar().maximum())

    def simulate_incoming(self):
        text = self.sim_input.text().strip()
        if not text:
            return
        sid = self.selected_steam_id() or "demo-troll"
        name = self.contacts.get(sid, {}).get("name", sid)
        self.sim_input.clear()
        self.on_incoming(sid, name, text, immediate_demo=True)

    def on_incoming(self, sid: str, name: str, text: str, immediate_demo: bool = False):
        digest = hashlib.sha256(f"{sid}\0{text}\0{int(time.time() // 2)}".encode()).hexdigest()
        if digest in self.seen_messages:
            return
        self.seen_messages.add(digest)

        if sid not in self.contacts:
            saved = self.config.get("contact_configs", {}).get(sid, {})
            self.contacts[sid] = {
                "name": name or sid,
                "enabled": bool(saved.get("enabled", False)),
                "replies": 0,
            }
            self.refresh_contact_list()
        elif name and self.contacts[sid]["name"] == sid:
            self.contacts[sid]["name"] = name

        self.add_transcript(sid, "in", text)
        self.write_log(sid, "in", text)

        cfg = self.contacts[sid]
        if self.paused:
            self.set_status(f"Incoming message from {cfg['name']} — responder is paused.")
            return
        if not cfg.get("enabled", False):
            self.set_status(f"Incoming message from {cfg['name']} — ELIZA is disabled for this contact.")
            return
        if cfg.get("replies", 0) >= int(self.config.get("max_replies", 250)):
            cfg["enabled"] = False
            self.refresh_contact_list()
            self.set_status(f"Reply limit reached for {cfg['name']}. ELIZA disabled.")
            return

        elapsed_h = (time.time() - self.session_started) / 3600
        if elapsed_h >= int(self.config.get("auto_stop_hours", 12)):
            cfg["enabled"] = False
            self.refresh_contact_list()
            self.set_status("Session auto-stop reached. ELIZA disabled for this contact.")
            return

        reply = self.engine.respond(text)
        if immediate_demo and self.demo_mode:
            delay_ms = 450
        else:
            lo = int(self.config.get("delay_min", 15))
            hi = int(self.config.get("delay_max", 90))
            delay_ms = random.randint(min(lo, hi), max(lo, hi)) * 1000

        self.set_status(f"ELIZA reply queued for {cfg['name']} (~{delay_ms/1000:.0f}s).")
        QTimer.singleShot(delay_ms, lambda s=sid, r=reply: self.send_eliza_reply(s, r))

    def send_eliza_reply(self, sid: str, reply: str):
        cfg = self.contacts.get(sid)
        if self.paused or not cfg or not cfg.get("enabled", False):
            return
        if cfg.get("replies", 0) >= int(self.config.get("max_replies", 250)):
            cfg["enabled"] = False
            self.refresh_contact_list()
            return

        try:
            if not self.demo_mode:
                self.backend.send_message(sid, reply)
            self.add_transcript(sid, "out", reply)
            self.write_log(sid, "out", reply)
            cfg["replies"] = cfg.get("replies", 0) + 1
            if sid == self.selected_steam_id():
                self.contact_stats.setText(f"Replies this session: {cfg['replies']}")
            self.set_status(f"ELIZA replied to {cfg['name']}.")
        except SteamBackendError as exc:
            self.set_status(f"Failed to send message: {exc}")

    def add_transcript(self, sid: str, who: str, text: str):
        stamp = datetime.now().strftime("%H:%M:%S")
        self.transcripts.setdefault(sid, []).append((stamp, who, text))
        self.transcripts[sid] = self.transcripts[sid][-500:]
        if sid == self.selected_steam_id():
            self.render_transcript(sid)

    def write_log(self, sid: str, direction: str, text: str):
        if not self.config.get("store_logs", True):
            return
        name = self.contacts.get(sid, {}).get("name", sid)
        append_chat_log(
            sid,
            name,
            direction,
            text,
            show_timestamp=bool(self.config.get("show_timestamps", False)),
        )

    # ---------------- Steam ----------------

    def connect_steam(self):
        if not SteamBackend.dependency_available():
            QMessageBox.warning(
                self,
                "Steam module missing",
                "The Python package 'steam' is not installed.\n\n"
                "Run install_and_run.bat to install the project-local dependencies.",
            )
            return

        dlg = SteamLoginDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        username, password, code = dlg.values()
        if not username or not password:
            QMessageBox.warning(self, "Missing credentials", "Account name and password are required.")
            return
        self.last_credentials = (username, password)

        try:
            self.backend.connect(username, password, code)
            self.connection_value.setText("Steam: connecting …")
        except SteamBackendError as exc:
            QMessageBox.critical(self, "Steam", str(exc))

    def populate_friends(self, friends):
        self.demo_mode = False
        old = self.contacts
        saved_all = self.config.get("contact_configs", {})
        self.contacts = {}
        for sid, name in friends:
            saved = saved_all.get(sid, {}) if isinstance(saved_all, dict) else {}
            self.contacts[sid] = {
                "name": name,
                "enabled": bool(saved.get("enabled", False)),
                "replies": int(old.get(sid, {}).get("replies", 0)),
            }
        self.refresh_contact_list()
        self.update_mode_labels()
        self.status_badge.setText("STEAM ONLINE")
        self.connection_value.setText(f"Steam: connected — {len(friends)} friends loaded")
        self.set_status(f"Steam connected. Loaded {len(friends)} contacts.")

    def on_auth_required(self, kind: str):
        if not self.last_credentials:
            return
        username, password = self.last_credentials
        code, ok = self._code_dialog(
            "Steam Guard",
            "Steam Guard email code:" if kind == "email" else "Steam Guard 2FA code:",
        )
        if ok and code:
            QTimer.singleShot(300, lambda: self._retry_auth(kind, username, password, code))

    def _retry_auth(self, kind: str, username: str, password: str, code: str):
        try:
            if kind == "email":
                self.backend.connect_with_email_code(username, password, code)
            else:
                self.backend.connect(username, password, code)
        except Exception as exc:
            self.set_status(f"Steam Guard retry failed: {exc}")

    def _code_dialog(self, title: str, label: str):
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        layout = QFormLayout(dlg)
        edit = QLineEdit()
        layout.addRow(label, edit)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addRow(buttons)
        ok = dlg.exec() == QDialog.DialogCode.Accepted
        return edit.text().strip(), ok

    def disconnect_steam(self):
        self.backend.disconnect()
        self.demo_mode = True
        self.status_badge.setText("DEMO MODE")
        self.connection_value.setText("Steam: disconnected")
        self._load_demo_contacts()
        self.set_status("Steam disconnected. Demo mode is active.")

    # ---------------- Commands ----------------

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_btn.setText("RESUME RESPONDER" if self.paused else "PAUSE RESPONDER")
        self.status_badge.setText("RESPONDER PAUSED" if self.paused else ("DEMO MODE" if self.demo_mode else "STEAM ONLINE"))
        self.set_status("Responder paused." if self.paused else "Responder resumed.")

    def open_logs(self):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(LOG_DIR)))

    def show_and_raise(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def set_status(self, text: str):
        self.status.showMessage(text)
        if not self.demo_mode and "connected" in text.lower():
            self.connection_value.setText(text)

    def show_about(self):
        QMessageBox.information(
            self,
            APP_NAME,
            f"{APP_NAME} v{VERSION}\n\n"
            "A PyQt6 ELIZA auto-responder for selected incoming Steam friend chats.\n\n"
            "No LLM required. ELIZA processing is local. Chat transcripts are saved "
            "as plain text when logging is enabled.",
        )

    def closeEvent(self, event: QCloseEvent):
        self.save_contact_settings()
        self.backend.disconnect()
        self.tray.hide()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("Game Troll Buster")
    app.setQuitOnLastWindowClosed(True)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
