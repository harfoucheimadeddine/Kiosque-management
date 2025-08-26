# ui_main.py - Modern UI with Purchase Price Feature and Revenue/Profit Tracking
from PyQt5.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QDoubleSpinBox, QFileDialog, QTableWidget, QTableWidgetItem,
    QGroupBox, QMessageBox, QHeaderView, QAbstractItemView, QFrame, QTextEdit,
    QSizePolicy, QSpacerItem, QCheckBox, QGridLayout, QDialog, QDialogButtonBox,
    QScrollArea # Import QScrollArea
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QFont, QIcon, QFontDatabase

# --- New ItemScanDialog Class ---
class ItemScanDialog(QDialog):
    def __init__(self, parent=None, item_data=None, currency="د.ج"):
        super().__init__(parent)
        self.setWindowTitle("تفاصيل الصنف")
        self.setModal(True)
        self.setLayoutDirection(Qt.RightToLeft)
        self.currency = currency
        self.item_data = item_data
        self.is_new_item = (item_data is None)
        self._setup_arabic_fonts()
        self.setFont(self._arabic_font) # Apply Arabic font to dialog

        self.original_item_id = -1 # Default for new/custom items, will be actual item_id for existing

        self._init_ui()
        self._populate_fields()
        self._connect_signals()

    def _setup_arabic_fonts(self):
        """Setup proper Arabic font support for the dialog."""
        arabic_fonts = [
            "Tahoma",           # Good Arabic support
            "Arial Unicode MS", # Comprehensive Unicode support
            "Segoe UI",         # Windows default with Arabic
            "DejaVu Sans",      # Linux Arabic support
            "Noto Sans Arabic", # Google Noto Arabic
            "Arial"             # Fallback
        ]
        
        self._arabic_font = None
        font_db = QFontDatabase()
        available_fonts = font_db.families()
        for font_name in arabic_fonts:
            if font_name in available_fonts:
                self._arabic_font = QFont(font_name, 11)
                self._arabic_font.setStyleHint(QFont.System)
                break
        if not self._arabic_font:
            self._arabic_font = QFont("Arial", 11)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)

        form_layout = QGridLayout()
        form_layout.setSpacing(10)

        # Item Name
        self.lbl_item_name = QLabel("اسم الصنف:")
        self.in_item_name = QLineEdit()
        self.in_item_name.setMinimumHeight(40)
        form_layout.addWidget(self.lbl_item_name, 0, 0)
        form_layout.addWidget(self.in_item_name, 0, 1, 1, 3) # Span across more columns

        # Barcode (read-only for existing, editable for new/custom)
        self.lbl_barcode = QLabel("الباركود:")
        self.in_barcode = QLineEdit()
        self.in_barcode.setMinimumHeight(40)
        self.in_barcode.setReadOnly(not self.is_new_item) # Editable only for new items
        form_layout.addWidget(self.lbl_barcode, 1, 0)
        form_layout.addWidget(self.in_barcode, 1, 1, 1, 3)

        # Available Stock (only for existing items)
        self.lbl_available_stock = QLabel("المخزون المتاح:")
        self.display_available_stock = QLabel("0")
        self.display_available_stock.setObjectName("KPI")
        self.display_available_stock.setFont(QFont(self._arabic_font.family(), 12, QFont.Bold))
        form_layout.addWidget(self.lbl_available_stock, 2, 0)
        form_layout.addWidget(self.display_available_stock, 2, 1)

        # Price
        self.lbl_price = QLabel(f"السعر ({self.currency}):")
        self.in_price = QDoubleSpinBox()
        self.in_price.setMaximum(10**9)
        self.in_price.setDecimals(2)
        self.in_price.setMinimumHeight(40)
        self.in_price.setPrefix(f"({self.currency}) ")
        self.in_price.setEnabled(False) # Initially disabled, controlled by checkbox
        form_layout.addWidget(self.lbl_price, 3, 0)
        form_layout.addWidget(self.in_price, 3, 1)

        # Manual Price Checkbox
        self.chk_manual_price = QCheckBox("سعر يدوي")
        self.chk_manual_price.setMinimumHeight(40)
        form_layout.addWidget(self.chk_manual_price, 3, 2, 1, 2, Qt.AlignLeft) # Span and align left

        # Quantity
        self.lbl_qty = QLabel("الكمية:")
        self.in_qty = QDoubleSpinBox()
        self.in_qty.setMaximum(10**9)
        self.in_qty.setDecimals(3)
        self.in_qty.setValue(1.0) # Default quantity
        self.in_qty.setMinimumHeight(40)
        form_layout.addWidget(self.lbl_qty, 4, 0)
        form_layout.addWidget(self.in_qty, 4, 1)
        
        main_layout.addLayout(form_layout)

        # Buttons
        self.button_box = QDialogButtonBox(Qt.Horizontal)
        self.add_button = self.button_box.addButton("إضافة إلى الفاتورة", QDialogButtonBox.AcceptRole)
        self.cancel_button = self.button_box.addButton("إلغاء", QDialogButtonBox.RejectRole)
        self.save_to_db_button = QPushButton("حفظ المنتج في المخزون")
        self.save_to_db_button.setVisible(self.is_new_item) # Only visible for new items
        self.button_box.addButton(self.save_to_db_button, QDialogButtonBox.ActionRole)
        
        main_layout.addWidget(self.button_box)

    def _populate_fields(self):
        if self.item_data:
            self.original_item_id = self.item_data.get("id", -1)
            self.in_item_name.setText(self.item_data.get("name", ""))
            self.in_item_name.setReadOnly(True) # Existing items: name is read-only
            self.in_barcode.setText(self.item_data.get("barcode", ""))
            self.in_price.setValue(float(self.item_data.get("price", 0.0)))
            available_stock = max(0, self.item_data.get("stock_count", 0))
            self.display_available_stock.setText(f"{available_stock:.0f}" if available_stock == int(available_stock) else f"{available_stock:.1f}")
            self.lbl_available_stock.setVisible(True)
            self.display_available_stock.setVisible(True)
            self.save_to_db_button.setVisible(False) # Not visible for existing items
        else: # New/Custom Item
            self.in_item_name.setPlaceholderText("اسم المنتج المخصص")
            self.in_item_name.setReadOnly(False)
            self.in_barcode.setPlaceholderText("باركود (اختياري)")
            self.in_barcode.setReadOnly(False)
            self.in_price.setValue(0.0)
            self.in_price.setEnabled(True) # Manual price by default for new items
            self.chk_manual_price.setChecked(True)
            self.lbl_available_stock.setVisible(False)
            self.display_available_stock.setVisible(False)
            self.save_to_db_button.setVisible(True)

    def _connect_signals(self):
        self.chk_manual_price.stateChanged.connect(self.in_price.setEnabled)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.save_to_db_button.clicked.connect(self.accept_and_save)

    def get_item_details(self):
        return {
            "id": self.original_item_id, # Use original ID if existing, otherwise -1
            "name": self.in_item_name.text().strip(),
            "barcode": self.in_barcode.text().strip(),
            "price": self.in_price.value(),
            "qty": self.in_qty.value(),
            "is_manual_price": self.chk_manual_price.isChecked(),
            "is_new_item": self.is_new_item,
            "save_to_db": False # Default, will be set to True if save_to_db_button is pressed
        }
    
    def accept_and_save(self):
        # This will set a flag in the returned details
        details = self.get_item_details()
        details["save_to_db"] = True
        self._return_details = details # Store for later retrieval
        self.accept()

    def done(self, r):
        # Override done to return our custom details if accept_and_save was used
        if hasattr(self, '_return_details') and r == QDialog.Accepted:
            self.setResult(QDialog.Accepted)
            super().done(r)
        elif r == QDialog.Accepted:
            details = self.get_item_details()
            # If it's a new item and not explicitly saved, treat as custom for the bill
            if details["is_new_item"] and not details["save_to_db"]:
                 details["id"] = -1 # Ensure it's marked as custom for bill
            self._return_details = details
            super().done(r)
        else:
            super().done(r)


class MainUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام إدارة المتجر")
        # Ensure the system title bar is always visible
        self.setWindowFlags(self.windowFlags() & ~Qt.FramelessWindowHint)
        self.resize(1400, 900)
        self.setMinimumSize(1000, 700) # A more flexible minimum size
        self.setLayoutDirection(Qt.RightToLeft)

        self._setup_arabic_fonts()
        self.setWindowIcon(QIcon("assets/logo/app_icon.png"))

        main = QVBoxLayout(self)
        main.setContentsMargins(12, 12, 12, 12)
        main.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(10)
        
        self.lbl_title = QLabel("نظام إدارة المتجر")
        self.lbl_title.setObjectName("HeaderTitle")
        header.addWidget(self.lbl_title)
        header.addStretch(1)
        
        main.addLayout(header)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main.addWidget(line)

        # Create QTabWidget instance
        self.tabs = QTabWidget()
        self.tabs.setLayoutDirection(Qt.RightToLeft)
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.tabBar().setElideMode(Qt.ElideRight)
        self.tabs.tabBar().setMinimumWidth(0)
        self.tabs.tabBar().setTabsClosable(False)
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(True)
        self.tabs.tabBar().setExpanding(True)

        # Create a QScrollArea and set the QTabWidget as its widget
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame) # No extra border for scroll area
        scroll_area.setWidget(self.tabs) # self.tabs is now the widget inside the scroll area
        
        main.addWidget(scroll_area, 1) # Give scroll area a stretch factor

        # Build tabs - these methods now operate on `self.tabs`
        self._build_bill_tab()
        self._build_stock_tab()
        self._build_sales_tab()
        self._build_settings_tab()

        # Tab icons
        try:
            self.tabs.setTabIcon(0, QIcon("assets/logo/tab_bill.png"))
            self.tabs.setTabIcon(1, QIcon("assets/logo/tab_stock.png"))
            self.tabs.setTabIcon(2, QIcon("assets/logo/tab_sales.png"))
            self.tabs.setTabIcon(3, QIcon("assets/logo/tab_settings.png"))
            self.tabs.setIconSize(QSize(24, 24))
        except:
            pass  # Icons are optional

    def _setup_arabic_fonts(self):
        """Setup proper Arabic font support"""
        arabic_fonts = [
            "Tahoma",           # Good Arabic support
            "Arial Unicode MS", # Comprehensive Unicode support
            "Segoe UI",         # Windows default with Arabic
            "DejaVu Sans",      # Linux Arabic support
            "Noto Sans Arabic", # Google Noto Arabic
            "Arial"             # Fallback
        ]
        
        self._arabic_font = None

        font_db = QFontDatabase()
        available_fonts = font_db.families()
        
        for font_name in arabic_fonts:
            if font_name in available_fonts:
                self._arabic_font = QFont(font_name, 11)
                self._arabic_font.setStyleHint(QFont.System)

                break
        
        if not self._arabic_font:
            self._arabic_font = QFont("Arial", 11)
        
        # Set application-wide font
        self.setFont(self._arabic_font)

        
    def resizeEvent(self, event):
        """Handle window resize events to maintain responsive layout"""
        super().resizeEvent(event)
        try:
            # Auto-resize table columns when window is resized
            if hasattr(self, 'tbl_bill'):
                self.tbl_bill.resizeColumnsToContents()
            if hasattr(self, 'tbl_stock'):
                self.tbl_stock.resizeColumnsToContents()
            if hasattr(self, 'tbl_sales'):
                self.tbl_sales.resizeColumnsToContents()
            if hasattr(self, 'tbl_sale_details'):
                self.tbl_sale_details.resizeColumnsToContents()
        except:
            pass

    # ---------- Current Bill Tab ----------
    def _build_bill_tab(self):
        tab_content = QWidget() # New widget to hold tab content
        outer = QVBoxLayout(tab_content)
        outer.setSpacing(12)

        # Input section with better spacing and sizing
        input_group = QGroupBox("إدخال المنتجات")
        input_layout = QVBoxLayout(input_group)
        
        # First row - Barcode and basic info
        row1 = QHBoxLayout()
        row1.setSpacing(10)

        # Barcode field - bigger and more prominent
        self.in_barcode = QLineEdit()
        self.in_barcode.setObjectName("barcode_field")
        self.in_barcode.setPlaceholderText("مسح الباركود أو إدخال يدوي (EAN-13, UPC-A, EAN-8)")
        self.in_barcode.setMinimumHeight(50)
        self.in_barcode.setMinimumWidth(300)
        self.in_barcode.setClearButtonEnabled(True)
        barcode_font = QFont("Courier New", 14, QFont.Bold)  # Monospace for barcodes
        self.in_barcode.setFont(barcode_font)

        # Find button
        # This button's functionality is now handled by the ItemScanDialog
        self.btn_bill_find = QPushButton("بحث")
        self.btn_bill_find.setMinimumHeight(50)
        self.btn_bill_find.setMinimumWidth(80)

        # Hardware scanner info button
        self.btn_scanner_info = QPushButton("معلومات الماسح")
        self.btn_scanner_info.setObjectName("secondary")
        self.btn_scanner_info.setMinimumHeight(50)
        self.btn_scanner_info.setMinimumWidth(120)

        row1.addWidget(QLabel("الباركود:"), 0)
        row1.addWidget(self.in_barcode, 3)
        row1.addWidget(self.btn_bill_find, 0)
        row1.addWidget(self.btn_scanner_info, 0)
        input_layout.addLayout(row1)

        # Second row - Product name (bigger and more prominent)
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        
        self.in_name = QLineEdit()
        self.in_name.setObjectName("name_field")
        self.in_name.setPlaceholderText("اسم المنتج")
        self.in_name.setMinimumHeight(50)
        self.in_name.setMinimumWidth(400)
        name_font = QFont(self.arabic_font.family(), 14, QFont.Bold)
        self.in_name.setFont(name_font)

        row2.addWidget(QLabel("اسم المنتج:"), 0)
        row2.addWidget(self.in_name, 1)
        input_layout.addLayout(row2)

        # Third row - Price, Quantity, Unit, Manual price option
        row3 = QHBoxLayout()
        row3.setSpacing(10)

        self.in_price = QDoubleSpinBox()
        self.in_price.setMaximum(10**9)
        self.in_price.setDecimals(2)
        self.in_price.setMinimumHeight(45)
        self.in_price.setMinimumWidth(120)
        self.in_price.setEnabled(False)  # Initially disabled

        self.in_qty = QDoubleSpinBox()
        self.in_qty.setMaximum(10**9)
        self.in_qty.setDecimals(3)
        self.in_qty.setValue(1.0)
        self.in_qty.setMinimumHeight(45)
        self.in_qty.setMinimumWidth(100)

        self.in_unit = QComboBox()
        self.in_unit.addItems(["حبة", "علبة/عبوة", "كيلو", "متر"])
        self.in_unit.setMinimumHeight(45)
        self.in_unit.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.in_unit.setMinimumWidth(100)

        # Manual price checkbox instead of combobox
        self.chk_manual = QCheckBox("سعر يدوي")
        self.chk_manual.setMinimumHeight(45)
        self.chk_manual.setMinimumWidth(100)

        row3.addWidget(QLabel("السعر:"), 0)
        row3.addWidget(self.in_price, 1)
        row3.addWidget(QLabel("الكمية:"), 0)
        row3.addWidget(self.in_qty, 1)
        row3.addWidget(QLabel("الوحدة:"), 0)
        row3.addWidget(self.in_unit, 1)
        row3.addWidget(self.chk_manual, 1)
        input_layout.addLayout(row3)

        # Add search hint label
        hint_label = QLabel("💡 نصيحة: يمكنك البحث بالباركود أو كتابة أول كلمة من اسم المنتج")
        hint_label.setStyleSheet("color: #60a5fa; font-size: 10pt; font-style: italic;")
        input_layout.addWidget(hint_label)

        # Action buttons row
        row4 = QHBoxLayout()
        row4.setSpacing(10)

        # This button's functionality is now primarily handled by the ItemScanDialog
        self.btn_bill_add = QPushButton("إضافة إلى الفاتورة")
        self.btn_bill_add.setMinimumHeight(45)
        self.btn_bill_add.setMinimumWidth(150)

        self.btn_bill_remove = QPushButton("حذف المحدد")
        self.btn_bill_remove.setObjectName("danger")
        self.btn_bill_remove.setMinimumHeight(45)
        self.btn_bill_remove.setMinimumWidth(120)

        self.btn_bill_save = QPushButton("حفظ الفاتورة")
        self.btn_bill_save.setObjectName("secondary")
        self.btn_bill_save.setMinimumHeight(45)
        self.btn_bill_save.setMinimumWidth(130)

        row4.addWidget(self.btn_bill_add)
        row4.addWidget(self.btn_bill_remove)
        row4.addStretch()
        row4.addWidget(self.btn_bill_save)
        input_layout.addLayout(row4)

        outer.addWidget(input_group) 

        # Bill table with better responsiveness
        table_group = QGroupBox("عناصر الفاتورة الحالية")
        table_layout = QVBoxLayout(table_group)
        
        self.tbl_bill = QTableWidget(0, 6)
        self.tbl_bill.setHorizontalHeaderLabels([
            "الباركود", "الاسم", "سعر الوحدة", "الكمية", "الإجمالي", "ID"
        ])
        
        # Hide ID column
        self.tbl_bill.horizontalHeader().setSectionHidden(5, True)
        # Hide barcode column for cleaner bill display
        self.tbl_bill.horizontalHeader().setSectionHidden(0, True)
        
        # Set responsive column behavior
        header = self.tbl_bill.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Name (stretches)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Price
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Quantity
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Total
        
        self.tbl_bill.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_bill.setAlternatingRowColors(True)
        self.tbl_bill.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # Ensure it expands vertically
        
        table_layout.addWidget(self.tbl_bill)
        outer.addWidget(table_group, 1) # Give table_group a stretch factor to take available space

        # Footer with total and print button
        footer = QHBoxLayout()
        footer.setSpacing(15)
        
        self.btn_print_bill = QPushButton("طباعة الفاتورة")
        self.btn_print_bill.setObjectName("warning")
        self.btn_print_bill.setMinimumHeight(45)
        self.btn_print_bill.setMinimumWidth(130)
        
        footer.addWidget(self.btn_print_bill)
        footer.addStretch(1)
        
        self.lbl_total = QLabel("الإجمالي: 0.00")
        self.lbl_total.setObjectName("KPI")
        total_font = QFont(self.arabic_font.family(), 16, QFont.Bold)
        self.lbl_total.setFont(total_font)
        
        footer.addWidget(self.lbl_total)
        outer.addLayout(footer)

        self.tabs.addTab(tab_content, "الفاتورة الحالية") # Add the content widget to the QTabWidget

        # Font for bill table names
        self.bill_name_font = QFont(self._arabic_font.family(), 13, QFont.Bold)

    # ---------- Stock Tab ----------
    def _build_stock_tab(self):
        tab_content = QWidget() # New widget to hold tab content
        outer = QVBoxLayout(tab_content)
        outer.setSpacing(12)

        # Stock form
        form_group = QGroupBox("بيانات الصنف")
        form_layout = QVBoxLayout(form_group)
        
        # First row - Name and Barcode
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        
        self.stk_name = QLineEdit()
        self.stk_name.setPlaceholderText("اسم الصنف")
        self.stk_name.setMinimumHeight(45)
        self.stk_name.setMinimumWidth(300)
        name_font = QFont(self.arabic_font.family(), 12, QFont.Bold)
        self.stk_name.setFont(name_font)

        self.stk_barcode = QLineEdit()
        self.stk_barcode.setPlaceholderText("الباركود (EAN-13, UPC-A, EAN-8)")
        self.stk_barcode.setMinimumHeight(45)
        self.stk_barcode.setMinimumWidth(200)
        barcode_font = QFont("Courier New", 12, QFont.Bold)
        self.stk_barcode.setFont(barcode_font)

        row1.addWidget(QLabel("اسم الصنف:"), 0)
        row1.addWidget(self.stk_name, 2)
        row1.addWidget(QLabel("الباركود:"), 0)
        row1.addWidget(self.stk_barcode, 1)
        form_layout.addLayout(row1)

        # Second row - Price, Purchase Price, Quantity, Category
        row2 = QHBoxLayout()
        row2.setSpacing(10)

        self.stk_price = QDoubleSpinBox()
        self.stk_price.setMaximum(10**9)
        self.stk_price.setDecimals(2)
        self.stk_price.setMinimumHeight(45)

        # NEW: Purchase price field
        self.stk_purchase_price = QDoubleSpinBox()
        self.stk_purchase_price.setMaximum(10**9)
        self.stk_purchase_price.setDecimals(2)
        self.stk_purchase_price.setMinimumHeight(45)

        self.stk_qty = QDoubleSpinBox()
        self.stk_qty.setMaximum(10**9)
        self.stk_qty.setDecimals(3)
        self.stk_qty.setMinimumHeight(45)

        row2.addWidget(QLabel("السعر:"), 0)
        row2.addWidget(self.stk_price, 1)
        row2.addWidget(QLabel("سعر الشراء:"), 0)
        row2.addWidget(self.stk_purchase_price, 1)
        row2.addWidget(QLabel("المخزون:"), 0)
        row2.addWidget(self.stk_qty, 1)
        form_layout.addLayout(row2)

        # Third row - Category
        row3 = QHBoxLayout()
        row3.setSpacing(10)

        self.stk_cat = QComboBox()
        self.stk_cat.setMinimumHeight(45)
        self.stk_cat.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        self.btn_stk_new_cat = QPushButton("تصنيف جديد")
        self.btn_stk_new_cat.setMinimumHeight(45)
        self.btn_stk_new_cat.setMinimumWidth(100)

        row3.addWidget(QLabel("التصنيف:"), 0)
        row3.addWidget(self.stk_cat, 2)
        row3.addWidget(self.btn_stk_new_cat, 0)
        form_layout.addLayout(row3)

        # Fourth row - Photo path and buttons
        row4 = QHBoxLayout()
        row4.setSpacing(10)

        self.stk_photo = QLineEdit()
        self.stk_photo.setPlaceholderText("مسار الصورة")
        self.stk_photo.setMinimumHeight(45)

        self.btn_stk_browse = QPushButton("اختيار صورة")
        self.btn_stk_browse.setMinimumHeight(45)
        self.btn_stk_browse.setMinimumWidth(100)

        self.btn_stk_camera = QPushButton("التقاط من الكاميرا")
        self.btn_stk_camera.setObjectName("secondary")
        self.btn_stk_camera.setMinimumHeight(45)
        self.btn_stk_camera.setMinimumWidth(140)

        # Preview image
        self.lbl_preview = QLabel("لا توجد صورة")
        self.lbl_preview.setFixedSize(120, 120)
        self.lbl_preview.setStyleSheet("""
            border: 2px solid #64748b; 
            border-radius: 8px; 
            background-color: #334155;
            color: #cbd5e1;
        """)
        self.lbl_preview.setAlignment(Qt.AlignCenter)

        row4.addWidget(QLabel("الصورة:"), 0)
        row4.addWidget(self.stk_photo, 2)
        row4.addWidget(self.btn_stk_browse, 0)
        row4.addWidget(self.btn_stk_camera, 0)
        row4.addWidget(self.lbl_preview, 0)
        form_layout.addLayout(row4)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_stk_add = QPushButton("إضافة")
        self.btn_stk_add.setMinimumHeight(45)
        self.btn_stk_add.setMinimumWidth(80)

        self.btn_stk_update = QPushButton("تعديل")
        self.btn_stk_update.setObjectName("secondary")
        self.btn_stk_update.setMinimumHeight(45)
        self.btn_stk_update.setMinimumWidth(80)

        self.btn_stk_delete = QPushButton("حذف")
        self.btn_stk_delete.setObjectName("danger")
        self.btn_stk_delete.setMinimumHeight(45)
        self.btn_stk_delete.setMinimumWidth(80)

        self.btn_stk_refresh = QPushButton("تحديث")
        self.btn_stk_refresh.setObjectName("warning")
        self.btn_stk_refresh.setMinimumHeight(45)
        self.btn_stk_refresh.setMinimumWidth(80)

        btn_row.addWidget(self.btn_stk_add)
        btn_row.addWidget(self.btn_stk_update)
        btn_row.addWidget(self.btn_stk_delete)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_stk_refresh)
        form_layout.addLayout(btn_row)

        outer.addWidget(form_group)

        # Stock table with purchase price column
        table_group = QGroupBox("قائمة المخزون")
        table_layout = QVBoxLayout(table_group)

        self.tbl_stock = QTableWidget(0, 11)
        self.tbl_stock.setHorizontalHeaderLabels([
            "ID", "الاسم", "التصنيف", "الباركود", "السعر", 
            "المخزون", "الحالة", "الصورة", "تاريخ الإضافة", "cat_id", "سعر الشراء"
        ])
        
        # Hide unnecessary columns
        self.tbl_stock.horizontalHeader().setSectionHidden(0, True)
        self.tbl_stock.horizontalHeader().setSectionHidden(7, True)
        self.tbl_stock.horizontalHeader().setSectionHidden(9, True)
        self.tbl_stock.horizontalHeader().setSectionHidden(10, True)
        
        # Set responsive behavior
        header = self.tbl_stock.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)
        
        self.tbl_stock.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_stock.setAlternatingRowColors(True)
        self.tbl_stock.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Disable auto-selection on double-click for better editing experience
        self.tbl_stock.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        table_layout.addWidget(self.tbl_stock)
        outer.addWidget(table_group, 1)

        self.tabs.addTab(tab_content, "المخزون")

    # ---------- Sales Tab ----------
    def _build_sales_tab(self):
        tab_content = QWidget() # New widget to hold tab content
        outer = QVBoxLayout(tab_content)
        outer.setSpacing(12)

        # KPI Section
        kpi_group = QGroupBox("ملخص المبيعات")
        kpi_layout = QGridLayout(kpi_group)
        kpi_layout.setSpacing(15)

        # First row of KPIs
        self.lbl_total_sales = QLabel("إجمالي المبيعات (إيرادات): 0.00")
        self.lbl_total_sales.setObjectName("KPI")
        self.lbl_total_sales.setMinimumWidth(200)
        
        self.lbl_total_profit_all_time = QLabel("إجمالي الربح الكلي: 0.00")
        self.lbl_total_profit_all_time.setObjectName("KPI")
        self.lbl_total_profit_all_time.setMinimumWidth(200)
        
        kpi_layout.addWidget(self.lbl_total_sales, 0, 0)
        kpi_layout.addWidget(self.lbl_total_profit_all_time, 0, 1)
        kpi_layout.setColumnStretch(2, 1)
        
        # Second row of KPIs (Today's Sales and Profit)
        self.lbl_today_sales = QLabel("مبيعات اليوم (إيرادات): 0.00")
        self.lbl_today_sales.setObjectName("KPI")
        self.lbl_today_sales.setMinimumWidth(200)
        
        self.lbl_today_profit = QLabel("ربح اليوم: 0.00")
        self.lbl_today_profit.setObjectName("KPI")
        self.lbl_today_profit.setMinimumWidth(200)

        kpi_layout.addWidget(self.lbl_today_sales, 1, 0)
        kpi_layout.addWidget(self.lbl_today_profit, 1, 1)
        
        # Third row for latest sale (separate line to prevent overlap)
        self.lbl_latest_sale = QLabel("آخر عملية: -")
        self.lbl_latest_sale.setObjectName("KPI")
        self.lbl_latest_sale.setMinimumWidth(400)
        self.lbl_latest_sale.setWordWrap(True)

        kpi_layout.addWidget(self.lbl_latest_sale, 2, 0, 1, 2)
        
        outer.addWidget(kpi_group)

        # Sales table
        sales_group = QGroupBox("قائمة المبيعات")
        sales_layout = QVBoxLayout(sales_group)

        self.tbl_sales = QTableWidget(0, 3)
        self.tbl_sales.setHorizontalHeaderLabels([
            "رقم العملية", "التاريخ والوقت", "الإجمالي"
        ])
        
        # Set responsive behavior
        header = self.tbl_sales.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        self.tbl_sales.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_sales.setAlternatingRowColors(True)
        self.tbl_sales.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        sales_layout.addWidget(self.tbl_sales)

        # Sales action buttons
        sales_btn_row = QHBoxLayout()
        sales_btn_row.setSpacing(10)

        self.btn_sale_view = QPushButton("عرض تفاصيل العملية المحددة")
        self.btn_sale_view.setObjectName("secondary")
        self.btn_sale_view.setMinimumHeight(40)

        self.btn_sale_delete = QPushButton("حذف العملية المحددة (مع إرجاع المخزون)")
        self.btn_sale_delete.setObjectName("danger")
        self.btn_sale_delete.setMinimumHeight(40)

        self.btn_sale_refresh = QPushButton("تحديث")
        self.btn_sale_refresh.setObjectName("warning")
        self.btn_sale_refresh.setMinimumHeight(40)
        self.btn_sale_refresh.setMinimumWidth(80)

        sales_btn_row.addWidget(self.btn_sale_view)
        sales_btn_row.addWidget(self.btn_sale_delete)
        sales_btn_row.addStretch()
        sales_btn_row.addWidget(self.btn_sale_refresh)
        sales_layout.addLayout(sales_btn_row)

        outer.addWidget(sales_group, 1)

        # Sale details table with purchase price and profit columns
        details_group = QGroupBox("تفاصيل العملية المحددة")
        details_layout = QVBoxLayout(details_group)

        self.tbl_sale_details = QTableWidget(0, 9)
        self.tbl_sale_details.setHorizontalHeaderLabels([
            "ID Det", "الاسم", "الكمية", "سعر البيع", "الإجمالي", "سعر الشراء", "الربح", "item_id", "sale_id"
        ])
        
        # Hide ID columns for cleaner display
        self.tbl_sale_details.horizontalHeader().setSectionHidden(0, True)
        self.tbl_sale_details.horizontalHeader().setSectionHidden(7, True)
        self.tbl_sale_details.horizontalHeader().setSectionHidden(8, True)
        
        # Set responsive behavior
        header2 = self.tbl_sale_details.horizontalHeader()
        header2.setSectionResizeMode(1, QHeaderView.Stretch)
        header2.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header2.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header2.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header2.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header2.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        self.tbl_sale_details.setAlternatingRowColors(True)
        self.tbl_sale_details.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        details_layout.addWidget(self.tbl_sale_details)
        
        # Revenue and Profit Summary Section
        summary_group = QGroupBox("ملخص الربح والإيرادات للعملية المحددة")
        summary_layout = QGridLayout(summary_group)
        summary_layout.setSpacing(15)
        
        # Revenue label for selected sale
        self.lbl_total_revenue = QLabel("إجمالي الإيرادات: 0.00")
        self.lbl_total_revenue.setObjectName("KPI")
        self.lbl_total_revenue.setMinimumHeight(40)
        
        # Profit label for selected sale
        self.lbl_total_profit = QLabel("إجمالي الربح: 0.00")
        self.lbl_total_profit.setObjectName("KPI")
        self.lbl_total_profit.setMinimumHeight(40)
        
        # Profit margin label for selected sale
        self.lbl_profit_margin = QLabel("هامش الربح: 0%")
        self.lbl_profit_margin.setObjectName("KPI")
        self.lbl_profit_margin.setMinimumHeight(40)
        
        # Add to grid layout
        summary_layout.addWidget(self.lbl_total_revenue, 0, 0)
        summary_layout.addWidget(self.lbl_total_profit, 0, 1)
        summary_layout.addWidget(self.lbl_profit_margin, 0, 2)
        
        details_layout.addWidget(summary_group)
        
        # Sale details action buttons
        details_btn_row = QHBoxLayout()
        details_btn_row.setSpacing(10)
        
        self.btn_sale_update_item = QPushButton("تعديل كمية الصنف المحدد")
        self.btn_sale_update_item.setObjectName("secondary")
        self.btn_sale_update_item.setMinimumHeight(40)
        
        self.btn_sale_delete_item = QPushButton("حذف الصنف المحدد من العملية")
        self.btn_sale_delete_item.setObjectName("danger")
        self.btn_sale_delete_item.setMinimumHeight(40)
        
        details_btn_row.addWidget(self.btn_sale_update_item)
        details_btn_row.addWidget(self.btn_sale_delete_item)
        details_btn_row.addStretch()
        
        details_layout.addLayout(details_btn_row)
        outer.addWidget(details_group, 1)

        self.tabs.addTab(tab_content, "المبيعات")

    # ---------- Settings Tab ----------
    def _build_settings_tab(self):
        tab_content = QWidget() # New widget to hold tab content
        outer = QVBoxLayout(tab_content)
        outer.setSpacing(15)

        # Settings form
        settings_group = QGroupBox("إعدادات المتجر")
        form_layout = QVBoxLayout(settings_group)
        form_layout.setSpacing(15)

        # Shop name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("اسم المتجر:"), 0)
        self.sett_shop_name = QLineEdit()
        self.sett_shop_name.setPlaceholderText("اسم المتجر (يظهر في عنوان التطبيق والفاتورة)")
        self.sett_shop_name.setMinimumHeight(45)
        name_layout.addWidget(self.sett_shop_name, 1)
        form_layout.addLayout(name_layout)

        # Contact
        contact_layout = QHBoxLayout()
        contact_layout.addWidget(QLabel("معلومات الاتصال:"), 0)
        self.sett_contact = QLineEdit()
        self.sett_contact.setPlaceholderText("هاتف / بريد إلكتروني")
        self.sett_contact.setMinimumHeight(45)
        contact_layout.addWidget(self.sett_contact, 1)
        form_layout.addLayout(contact_layout)

        # Location
        location_layout = QHBoxLayout()
        location_layout.addWidget(QLabel("الموقع:"), 0)
        self.sett_location = QLineEdit()
        self.sett_location.setPlaceholderText("العنوان / الموقع")
        self.sett_location.setMinimumHeight(45)
        location_layout.addWidget(self.sett_location, 1)
        form_layout.addLayout(location_layout)

        # Currency
        currency_layout = QHBoxLayout()
        currency_layout.addWidget(QLabel("العملة:"), 0)
        self.sett_currency = QLineEdit()
        self.sett_currency.setPlaceholderText("العملة (مثال: د.ج ، ر.س ، د.ك ، MAD ، USD)")
        self.sett_currency.setMinimumHeight(45)
        currency_layout.addWidget(self.sett_currency, 1)
        form_layout.addLayout(currency_layout)

        # Save button
        self.btn_settings_save = QPushButton("حفظ الإعدادات")
        self.btn_settings_save.setObjectName("secondary")
        self.btn_settings_save.setMinimumHeight(50)
        self.btn_settings_save.setMinimumWidth(150)
        
        save_layout = QHBoxLayout()
        save_layout.addStretch()
        save_layout.addWidget(self.btn_settings_save)
        save_layout.addStretch()
        form_layout.addLayout(save_layout)

        outer.addWidget(settings_group)
        outer.addStretch(1)

        self.tabs.addTab(tab_content, "الإعدادات") # Add the content widget to the QTabWidget

    # ---------- Helper Methods ----------
    def msg(self, title, text):
        """Show information message"""
        QMessageBox.information(self, title, text)

    def set_preview_image(self, path: str):
        """Set preview image in stock tab"""
        if path and len(path.strip()) > 0:
            try:
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        self.lbl_preview.width() - 4, 
                        self.lbl_preview.height() - 4, 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    self.lbl_preview.setPixmap(scaled_pixmap)
                    return
            except:
                pass
        
        self.lbl_preview.clear()
        self.lbl_preview.setText("لا توجد صورة")
