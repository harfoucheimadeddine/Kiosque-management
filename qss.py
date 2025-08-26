# qss.py - Modern Dark Theme with Vibrant Colors
APP_QSS = """
/* Global Styles */
* { 
    font-family: 'Segoe UI', 'Tahoma', 'Arial'; 
    font-size: 11pt; 
    color: #f8fafc;
}

QWidget { 
    background-color: #0f172a; 
    color: #f8fafc; 
    border: none;
}

/* Main Window */
QMainWindow {
    background-color: #020617;
}

/* Tab Widget */
QTabWidget {
    background-color: #0f172a;
    border: none;
}

QTabWidget::pane { 
    border: 2px solid #1e293b; 
    border-radius: 16px;
    background-color: #0f172a;
    margin-top: 8px;
}

QTabBar {
    background-color: transparent;
}

QTabBar::tab { 
    padding: 14px 24px; 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e293b, stop:1 #0f172a);
    margin: 2px 6px; 
    border-radius: 16px;
    border: 2px solid #334155;
    color: #cbd5e1;
    font-weight: 600;
    min-width: 140px;
    font-size: 12pt;
}

QTabBar::tab:selected { 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3b82f6, stop:1 #1e40af);
    color: white;
    border: 2px solid #2563eb;
    transform: scale(1.02);
}

QTabBar::tab:hover:!selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #374151, stop:1 #1f2937);
    border: 2px solid #4b5563;
    color: #e5e7eb;
}

/* Group Boxes */
QGroupBox { 
    border: 2px solid #334155; 
    border-radius: 16px; 
    margin-top: 20px; 
    padding-top: 12px;
    background-color: #0f172a;
    font-weight: 700;
    font-size: 13pt;
    color: #f1f5f9;
}

QGroupBox::title { 
    subcontrol-origin: margin; 
    left: 20px; 
    padding: 6px 16px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #1e40af);
    border: none;
    border-radius: 8px;
    color: white;
    font-weight: 700;
}

/* Input Fields */
QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox {
    background-color: #1e293b; 
    border: 2px solid #475569; 
    border-radius: 12px; 
    padding: 10px 16px;
    color: #f8fafc;
    font-size: 12pt;
    selection-background-color: #3b82f6;
    font-weight: 500;
}

QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus {
    border: 2px solid #3b82f6;
    background-color: #1e293b;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

QLineEdit:hover, QComboBox:hover, QDoubleSpinBox:hover, QSpinBox:hover {
    border: 2px solid #60a5fa;
    background-color: #1e293b;
}

/* Special styling for barcode and name fields */
QLineEdit#barcode_field {
    font-size: 15pt;
    font-weight: 700;
    padding: 14px 20px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e40af, stop:1 #3730a3);
    border: 2px solid #3b82f6;
    color: white;
    border-radius: 16px;
}

QLineEdit#barcode_field:focus {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
    border: 2px solid #60a5fa;
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
}

QLineEdit#name_field {
    font-size: 15pt;
    font-weight: 700;
    padding: 14px 20px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #047857);
    border: 2px solid #10b981;
    color: white;
    border-radius: 16px;
}

QLineEdit#name_field:focus {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669);
    border: 2px solid #34d399;
    box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.2);
}

/* ComboBox Dropdown */
QComboBox::drop-down {
    border: none;
    width: 24px;
    border-radius: 8px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid #cbd5e1;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #1e293b;
    border: 2px solid #475569;
    border-radius: 12px;
    selection-background-color: #3b82f6;
    color: #f8fafc;
    padding: 4px;
}

QComboBox QAbstractItemView::item {
    padding: 8px 12px;
    border-radius: 8px;
    margin: 2px;
}

QComboBox QAbstractItemView::item:selected {
    background-color: #3b82f6;
    color: white;
}

/* Buttons */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #22c55e, stop:1 #16a34a);
    color: white; 
    border: none; 
    border-radius: 12px; 
    padding: 12px 20px;
    font-weight: 700;
    font-size: 12pt;
    min-height: 24px;
}

QPushButton:hover { 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #16a34a, stop:1 #15803d);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #15803d, stop:1 #166534);
    transform: translateY(0px);
}

QPushButton#danger { 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ef4444, stop:1 #dc2626);
}

QPushButton#danger:hover { 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #dc2626, stop:1 #b91c1c);
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

QPushButton#secondary { 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3b82f6, stop:1 #2563eb);
}

QPushButton#secondary:hover { 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2563eb, stop:1 #1d4ed8);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

QPushButton#warning {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f59e0b, stop:1 #d97706);
}

QPushButton#warning:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d97706, stop:1 #b45309);
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

/* Tables */
QTableWidget { 
    background-color: #1e293b; 
    gridline-color: #334155;
    border: 2px solid #475569;
    border-radius: 12px;
    selection-background-color: #3b82f6;
    alternate-background-color: #0f172a;
}

QTableWidget::item {
    padding: 10px 8px;
    border-bottom: 1px solid #334155;
    color: #f8fafc;
    font-weight: 500;
}

QTableWidget::item:selected {
    background-color: #3b82f6;
    color: white;
    font-weight: 600;
}

QTableWidget::item:hover {
    background-color: #334155;
}

QHeaderView::section { 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #475569, stop:1 #334155);
    padding: 12px 16px; 
    border: 1px solid #1e293b;
    color: #f8fafc;
    font-weight: 700;
    font-size: 12pt;
    border-radius: 0px;
}

QHeaderView::section:first {
    border-top-left-radius: 12px;
}

QHeaderView::section:last {
    border-top-right-radius: 12px;
}

QHeaderView::section:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #334155, stop:1 #1e293b);
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #1e293b;
    width: 14px;
    border-radius: 7px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #475569, stop:1 #64748b);
    border-radius: 7px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #64748b, stop:1 #475569);
}

QScrollBar:horizontal {
    background-color: #1e293b;
    height: 14px;
    border-radius: 7px;
    margin: 2px;
}

QScrollBar::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #475569, stop:1 #64748b);
    border-radius: 7px;
    min-width: 24px;
}

QScrollBar::handle:horizontal:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #64748b, stop:1 #475569);
}

QScrollBar::add-line, QScrollBar::sub-line {
    background: none;
    border: none;
}

/* Labels */
QLabel { 
    color: #f8fafc;
    background: transparent;
    font-weight: 500;
}

QLabel#HeaderTitle { 
    font-size: 22pt; 
    font-weight: 800; 
    color: #60a5fa;
    background: transparent;
    text-shadow: 0 2px 4px rgba(96, 165, 250, 0.3);
}

QLabel#OutOfStock { 
    color: #ef4444; 
    font-weight: 700; 
    background: transparent;
}

QLabel#KPI {
    font-size: 13pt;
    font-weight: 700;
    color: #22c55e;
    background: transparent;
    padding: 10px 12px;
    border-radius: 8px;
    background-color: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.2);
}

/* Frames and Lines */
QFrame {
    background-color: #1e293b;
}

QFrame[frameShape="4"] { /* HLine */
    color: #475569;
    background-color: #475569;
    max-height: 2px;
}

QFrame[frameShape="5"] { /* VLine */
    color: #475569;
    background-color: #475569;
    max-width: 2px;
}

/* Text Edit */
QTextEdit {
    background-color: #1e293b;
    border: 2px solid #475569;
    border-radius: 12px;
    color: #f8fafc;
    selection-background-color: #3b82f6;
    padding: 8px;
}

QTextEdit:focus {
    border: 2px solid #3b82f6;
}

/* Spin Box Buttons */
QDoubleSpinBox::up-button, QSpinBox::up-button {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #475569, stop:1 #334155);
    border: none;
    border-radius: 6px;
    width: 20px;
    margin: 2px;
}

QDoubleSpinBox::up-button:hover, QSpinBox::up-button:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #334155, stop:1 #1e293b);
}

QDoubleSpinBox::down-button, QSpinBox::down-button {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #475569, stop:1 #334155);
    border: none;
    border-radius: 6px;
    width: 20px;
    margin: 2px;
}

QDoubleSpinBox::down-button:hover, QSpinBox::down-button:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #334155, stop:1 #1e293b);
}

/* CheckBox */
QCheckBox {
    color: #f8fafc;
    font-weight: 600;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid #475569;
    background-color: #1e293b;
}

QCheckBox::indicator:checked {
    background-color: #3b82f6;
    border: 2px solid #2563eb;
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
}

QCheckBox::indicator:hover {
    border: 2px solid #60a5fa;
}

/* Message Box */
QMessageBox {
    background-color: #0f172a;
    color: #f8fafc;
    border: 2px solid #334155;
    border-radius: 16px;
}

QMessageBox QPushButton {
    min-width: 100px;
    padding: 10px 20px;
    margin: 4px;
}

QMessageBox QLabel {
    color: #f8fafc;
    font-size: 12pt;
    padding: 8px;
}

/* Progress Bar */
QProgressBar {
    background-color: #1e293b;
    border: 2px solid #475569;
    border-radius: 8px;
    text-align: center;
    color: #f8fafc;
    font-weight: 600;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #22c55e, stop:1 #16a34a);
    border-radius: 6px;
}

/* Tool Tips */
QToolTip {
    background-color: #0f172a;
    color: #f8fafc;
    border: 2px solid #475569;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 11pt;
}

/* Status Bar */
QStatusBar {
    background-color: #1e293b;
    color: #cbd5e1;
    border-top: 1px solid #334155;
}

/* Menu Bar */
QMenuBar {
    background-color: #1e293b;
    color: #f8fafc;
    border-bottom: 1px solid #334155;
}

QMenuBar::item {
    padding: 8px 16px;
    background: transparent;
    border-radius: 6px;
}

QMenuBar::item:selected {
    background-color: #3b82f6;
    color: white;
}

QMenu {
    background-color: #1e293b;
    border: 2px solid #475569;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 16px;
    border-radius: 6px;
}

QMenu::item:selected {
    background-color: #3b82f6;
    color: white;
}
"""