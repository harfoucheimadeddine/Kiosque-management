# qss.py (fixed)
# Dark theme with colorful accents - Professional look
APP_QSS = """
/* Global Styles */
* { 
    font-family: 'Segoe UI', 'Tahoma', 'Arial'; 
    font-size: 11pt; 
    color: #e2e8f0;
}

QWidget { 
    background-color: #1e293b; 
    color: #e2e8f0; 
    border: none;
}

/* Main Window */
QMainWindow {
    background-color: #0f172a;
}

/* Tab Widget */
QTabWidget {
    background-color: #1e293b;
    border: none;
}

QTabWidget::pane { 
    border: 2px solid #334155; 
    border-radius: 12px;
    background-color: #1e293b;
    margin-top: 8px;
}

QTabBar {
    background-color: transparent;
}

QTabBar::tab { 
    padding: 12px 20px; 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #334155, stop:1 #1e293b);
    margin: 2px 4px; 
    border-radius: 12px;
    border: 1px solid #475569;
    color: #cbd5e1;
    font-weight: 600;
    min-width: 120px;
}

QTabBar::tab:selected { 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3b82f6, stop:1 #1d4ed8);
    color: white;
    border: 1px solid #2563eb;
}

QTabBar::tab:hover:!selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #475569, stop:1 #334155);
    border: 1px solid #64748b;
}

/* Group Boxes */
QGroupBox { 
    border: 2px solid #475569; 
    border-radius: 12px; 
    margin-top: 16px; 
    padding-top: 8px;
    background-color: #1e293b;
    font-weight: 600;
    font-size: 12pt;
}

QGroupBox::title { 
    subcontrol-origin: margin; 
    left: 16px; 
    padding: 4px 12px;
    background-color: #334155;
    border: 1px solid #475569;
    border-radius: 6px;
    color: #f1f5f9;
}

/* Input Fields */
QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox {
    background-color: #475569; 
    border: 2px solid #64748b; 
    border-radius: 8px; 
    padding: 8px 12px;
    color: #f1f5f9;
    font-size: 11pt;
    selection-background-color: #3b82f6;
}

QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus {
    border: 2px solid #3b82f6;
    background-color: #334155;
}

QLineEdit:hover, QComboBox:hover, QDoubleSpinBox:hover, QSpinBox:hover {
    border: 2px solid #60a5fa;
}

/* Special styling for barcode and name fields */
QLineEdit#barcode_field {
    font-size: 14pt;
    font-weight: 600;
    padding: 12px 16px;
    background-color: #1e40af;
    border: 2px solid #3b82f6;
    color: white;
}

QLineEdit#name_field {
    font-size: 14pt;
    font-weight: 700;
    padding: 12px 16px;
    background-color: #059669;
    border: 2px solid #10b981;
    color: white;
}

/* ComboBox Dropdown */
QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #cbd5e1;
    margin-right: 5px;
}

QComboBox QAbstractItemView {
    background-color: #334155;
    border: 1px solid #64748b;
    selection-background-color: #3b82f6;
    color: #f1f5f9;
}

/* Buttons */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #22c55e, stop:1 #16a34a);
    color: white; 
    border: none; 
    border-radius: 10px; 
    padding: 10px 16px;
    font-weight: 600;
    font-size: 11pt;
    min-height: 20px;
}

QPushButton:hover { 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #16a34a, stop:1 #15803d);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #15803d, stop:1 #166534);
}

QPushButton#danger { 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ef4444, stop:1 #dc2626);
}

QPushButton#danger:hover { 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #dc2626, stop:1 #b91c1c);
}

QPushButton#secondary { 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3b82f6, stop:1 #2563eb);
}

QPushButton#secondary:hover { 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2563eb, stop:1 #1d4ed8);
}

QPushButton#warning {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f59e0b, stop:1 #d97706);
}

QPushButton#warning:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d97706, stop:1 #b45309);
}

/* Tables */
QTableWidget { 
    background-color: #334155; 
    gridline-color: #475569;
    border: 1px solid #64748b;
    border-radius: 8px;
    selection-background-color: #3b82f6;
    alternate-background-color: #2d3748;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #475569;
    color: #f1f5f9;
}

QTableWidget::item:selected {
    background-color: #3b82f6;
    color: white;
}

QTableWidget::item:hover {
    background-color: #475569;
}

QHeaderView::section { 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #64748b, stop:1 #475569);
    padding: 8px 12px; 
    border: 1px solid #334155;
    color: #f1f5f9;
    font-weight: 600;
    font-size: 11pt;
}

QHeaderView::section:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #475569, stop:1 #334155);
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #334155;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #64748b;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #475569;
}

QScrollBar:horizontal {
    background-color: #334155;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #64748b;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #475569;
}

/* Labels */
QLabel { 
    color: #f1f5f9;
    background: transparent;
}

QLabel#HeaderTitle { 
    font-size: 20pt; 
    font-weight: 700; 
    color: #60a5fa;
    background: transparent;
}

QLabel#OutOfStock { 
    color: #ef4444; 
    font-weight: 600; 
    background: transparent;
}

QLabel#KPI {
    font-size: 12pt;
    font-weight: 600;
    color: #22c55e;
    background: transparent;
    padding: 8px;
}

/* Frames and Lines */
QFrame {
    background-color: #334155;
}

QFrame[frameShape="4"] { /* HLine */
    color: #64748b;
    background-color: #64748b;
}

QFrame[frameShape="5"] { /* VLine */
    color: #64748b;
    background-color: #64748b;
}

/* Text Edit */
QTextEdit {
    background-color: #334155;
    border: 2px solid #64748b;
    border-radius: 8px;
    color: #f1f5f9;
    selection-background-color: #3b82f6;
}

/* Spin Box Buttons */
QDoubleSpinBox::up-button, QSpinBox::up-button {
    background-color: #64748b;
    border: none;
    border-radius: 4px;
    width: 16px;
}

QDoubleSpinBox::up-button:hover, QSpinBox::up-button:hover {
    background-color: #475569;
}

QDoubleSpinBox::down-button, QSpinBox::down-button {
    background-color: #64748b;
    border: none;
    border-radius: 4px;
    width: 16px;
}

QDoubleSpinBox::down-button:hover, QSpinBox::down-button:hover {
    background-color: #475569;
}

/* Message Box */
QMessageBox {
    background-color: #1e293b;
    color: #f1f5f9;
}

QMessageBox QPushButton {
    min-width: 80px;
    padding: 8px 16px;
}

/* Progress Bar */
QProgressBar {
    background-color: #334155;
    border: 1px solid #64748b;
    border-radius: 6px;
    text-align: center;
    color: #f1f5f9;
}

QProgressBar::chunk {
    background-color: #22c55e;
    border-radius: 6px;
}

/* Tool Tips */
QToolTip {
    background-color: #0f172a;
    color: #f1f5f9;
    border: 1px solid #64748b;
    border-radius: 6px;
    padding: 4px 8px;
}
"""