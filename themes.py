from __future__ import annotations

THEMES: dict[str, str] = {
    "Cyber Dark": """
        QWidget { background-color: #0b0f16; color: #d9f7ff; font-family: "Segoe UI"; font-size: 10pt; }
        QMainWindow, QDialog { background-color: #080c12; }
        QMenuBar, QMenu { background-color: #101722; color: #d9f7ff; }
        QMenuBar::item:selected, QMenu::item:selected { background-color: #17384a; }
        QFrame#HeaderFrame { background-color: #101722; border: 1px solid #1e6679; border-radius: 8px; }
        QLabel#AppTitle { color: #70f2ff; font-size: 20pt; font-weight: 800; letter-spacing: 2px; }
        QLabel#TagLine { color: #84a7b2; }
        QLabel#StatusBadge { background-color: #112c35; color: #77f3aa; border: 1px solid #2aa36b; border-radius: 10px; padding: 4px 10px; font-weight: 700; }
        QGroupBox { border: 1px solid #1e6679; border-radius: 7px; margin-top: 12px; padding-top: 9px; font-weight: 700; color: #70f2ff; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        QListWidget, QTextBrowser, QLineEdit, QSpinBox, QComboBox {
            background-color: #0f1620; color: #e9fbff; border: 1px solid #244b5a;
            border-radius: 5px; padding: 5px; selection-background-color: #155d74;
        }
        QPushButton { background-color: #132b38; color: #baf8ff; border: 1px solid #2f98b4; border-radius: 5px; padding: 7px 11px; font-weight: 700; }
        QPushButton:hover { background-color: #19445a; border-color: #70f2ff; }
        QPushButton#DangerButton { background-color: #35151a; color: #ffc0c7; border-color: #9d3443; }
        QPushButton#PrimaryButton { background-color: #123b33; color: #b8ffe8; border-color: #2bb986; }
        QStatusBar { background-color: #101722; color: #9fc3cc; }
        QSplitter::handle { background-color: #162634; width: 2px; }
        QTabWidget::pane { border: 1px solid #244b5a; }
        QTabBar::tab { background: #101722; color: #9fc3cc; padding: 7px 12px; border: 1px solid #244b5a; }
        QTabBar::tab:selected { color: #70f2ff; background: #16303d; }
    """,
    "Neon Purple": """
        QWidget { background-color: #100b18; color: #f4e9ff; font-family: "Segoe UI"; font-size: 10pt; }
        QMainWindow, QDialog { background-color: #0d0813; }
        QMenuBar, QMenu { background-color: #1a1026; color: #f4e9ff; }
        QMenuBar::item:selected, QMenu::item:selected { background-color: #4d286d; }
        QFrame#HeaderFrame { background-color: #1a1026; border: 1px solid #813db0; border-radius: 8px; }
        QLabel#AppTitle { color: #d98cff; font-size: 20pt; font-weight: 800; letter-spacing: 2px; }
        QLabel#TagLine { color: #ba9dca; }
        QLabel#StatusBadge { background-color: #2a153b; color: #f0bdff; border: 1px solid #a04ed1; border-radius: 10px; padding: 4px 10px; font-weight: 700; }
        QGroupBox { border: 1px solid #704094; border-radius: 7px; margin-top: 12px; padding-top: 9px; font-weight: 700; color: #d98cff; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        QListWidget, QTextBrowser, QLineEdit, QSpinBox, QComboBox {
            background-color: #17101f; color: #fff7ff; border: 1px solid #57326e; border-radius: 5px; padding: 5px; selection-background-color: #653488;
        }
        QPushButton { background-color: #29163a; color: #f1cfff; border: 1px solid #8c49b5; border-radius: 5px; padding: 7px 11px; font-weight: 700; }
        QPushButton:hover { background-color: #44215f; border-color: #d98cff; }
        QPushButton#PrimaryButton { background-color: #302047; border-color: #c05df0; }
        QPushButton#DangerButton { background-color: #3b162e; color: #ffbfdc; border-color: #a64673; }
        QStatusBar { background-color: #1a1026; color: #baa7c6; }
    """,
    "Matrix": """
        QWidget { background-color: #050905; color: #8dff8d; font-family: "Consolas"; font-size: 10pt; }
        QMainWindow, QDialog { background-color: #030603; }
        QMenuBar, QMenu { background-color: #071007; color: #8dff8d; }
        QMenuBar::item:selected, QMenu::item:selected { background-color: #123512; }
        QFrame#HeaderFrame { background-color: #071007; border: 1px solid #267326; border-radius: 6px; }
        QLabel#AppTitle { color: #59ff59; font-size: 20pt; font-weight: 900; letter-spacing: 2px; }
        QLabel#TagLine { color: #6caf6c; }
        QLabel#StatusBadge { background-color: #0b210b; color: #72ff72; border: 1px solid #298329; border-radius: 10px; padding: 4px 10px; font-weight: 700; }
        QGroupBox { border: 1px solid #246524; border-radius: 5px; margin-top: 12px; padding-top: 9px; font-weight: 700; color: #59ff59; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        QListWidget, QTextBrowser, QLineEdit, QSpinBox, QComboBox {
            background-color: #061006; color: #aaffaa; border: 1px solid #1d551d; border-radius: 3px; padding: 5px; selection-background-color: #174917;
        }
        QPushButton { background-color: #0b210b; color: #8dff8d; border: 1px solid #278027; border-radius: 3px; padding: 7px 11px; font-weight: 700; }
        QPushButton:hover { background-color: #123a12; border-color: #59ff59; }
        QPushButton#DangerButton { background-color: #2a1010; color: #ff9d9d; border-color: #803030; }
        QStatusBar { background-color: #071007; color: #6caf6c; }
    """,
    "Light": """
        QWidget { background-color: #f5f7fa; color: #18202a; font-family: "Segoe UI"; font-size: 10pt; }
        QMainWindow, QDialog { background-color: #eef2f7; }
        QMenuBar, QMenu { background-color: #ffffff; color: #18202a; }
        QMenuBar::item:selected, QMenu::item:selected { background-color: #dcecf6; }
        QFrame#HeaderFrame { background-color: #ffffff; border: 1px solid #c7d3df; border-radius: 8px; }
        QLabel#AppTitle { color: #125a83; font-size: 20pt; font-weight: 800; letter-spacing: 1px; }
        QLabel#TagLine { color: #587083; }
        QLabel#StatusBadge { background-color: #e8f7ee; color: #17643a; border: 1px solid #6cbf8c; border-radius: 10px; padding: 4px 10px; font-weight: 700; }
        QGroupBox { border: 1px solid #c3d1de; border-radius: 7px; margin-top: 12px; padding-top: 9px; font-weight: 700; color: #125a83; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        QListWidget, QTextBrowser, QLineEdit, QSpinBox, QComboBox {
            background-color: #ffffff; color: #18202a; border: 1px solid #bdc9d4; border-radius: 5px; padding: 5px; selection-background-color: #cbe7f7;
        }
        QPushButton { background-color: #ffffff; color: #18394b; border: 1px solid #93b5c8; border-radius: 5px; padding: 7px 11px; font-weight: 700; }
        QPushButton:hover { background-color: #e6f2f8; }
        QPushButton#PrimaryButton { background-color: #e6f7ee; border-color: #6bb78c; }
        QPushButton#DangerButton { background-color: #fff0f1; color: #8a2c36; border-color: #d4959d; }
        QStatusBar { background-color: #ffffff; color: #587083; }
    """,
    "Hellfire": """
        QWidget { background-color: #130b08; color: #ffe4cd; font-family: "Segoe UI"; font-size: 10pt; }
        QMainWindow, QDialog { background-color: #0f0806; }
        QMenuBar, QMenu { background-color: #21100a; color: #ffe4cd; }
        QMenuBar::item:selected, QMenu::item:selected { background-color: #512514; }
        QFrame#HeaderFrame { background-color: #21100a; border: 1px solid #9d481e; border-radius: 8px; }
        QLabel#AppTitle { color: #ff8a36; font-size: 20pt; font-weight: 800; letter-spacing: 2px; }
        QLabel#TagLine { color: #c99d7d; }
        QLabel#StatusBadge { background-color: #381a0c; color: #ffd36b; border: 1px solid #b36d21; border-radius: 10px; padding: 4px 10px; font-weight: 700; }
        QGroupBox { border: 1px solid #82421f; border-radius: 7px; margin-top: 12px; padding-top: 9px; font-weight: 700; color: #ff9a4b; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        QListWidget, QTextBrowser, QLineEdit, QSpinBox, QComboBox {
            background-color: #1c100b; color: #ffe9d7; border: 1px solid #6f3820; border-radius: 5px; padding: 5px; selection-background-color: #673017;
        }
        QPushButton { background-color: #35190e; color: #ffd5b8; border: 1px solid #a75225; border-radius: 5px; padding: 7px 11px; font-weight: 700; }
        QPushButton:hover { background-color: #562513; border-color: #ff8a36; }
        QPushButton#PrimaryButton { background-color: #422414; border-color: #db7b32; }
        QPushButton#DangerButton { background-color: #451015; color: #ffc4c4; border-color: #ab3d45; }
        QStatusBar { background-color: #21100a; color: #c99d7d; }
    """,
}
