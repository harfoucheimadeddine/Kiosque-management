# ui_main.py (Part 1 - Stock Tab)
from PyQt5.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QDoubleSpinBox, QFileDialog, QTableWidget, QTableWidgetItem,
    QGroupBox, QMessageBox, QHeaderView, QAbstractItemView, QFrame, QTextEdit,
    QSizePolicy, QSpacerItem, QCheckBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QFont, QIcon, QFontDatabase

class MainUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام إدارة المتجر")
        self.resize(1400, 900)
        self.setMinimumSize(1200, 800)
        self.setLayoutDirection(Qt.RightToLeft)

        # Setup Arabic font support
        self._setup_arabic_fonts()

        # Custom app/taskbar icon (no default Python icon)
        self.setWindowIcon(QIcon("assets/logo/app_icon.png"))

        main = QVBoxLayout(self)
        main.setContentsMargins(12, 12, 12, 12)
        main.setSpacing(10)

        # Custom header (title right, window buttons left)
        header = QHBoxLayout()
        header.setSpacing(10)
        
        self.lbl_title = QLabel("نظام إدارة المتجر")
        self.lbl_title.setObjectName("HeaderTitle")
        header.addWidget(self.lbl_title)
        header.addStretch(1)
        
        # Window control buttons
        self.btn_min = QPushButton("—")
        self.btn_max = QPushButton("⬜")
        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("danger")
        
        for b in (self.btn_min, self.btn_max, self.btn_close):
            b.setFixedSize(40, 34)
            b.setFont(QFont("Arial", 12, QFont.Bold))
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(4)
        btn_layout.addWidget(self.btn_min)
        btn_layout.addWidget(self.btn_max)
        btn_layout.addWidget(self.btn_close)
        header.addLayout(btn_layout)
        main.addLayout(header)

        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main.addWidget(line)

        # Main tabs
        self.tabs = QTabWidget()
        self.tabs.setLayoutDirection(Qt.RightToLeft)
        self.tabs.setTabPosition(QTabWidget.North)
        main.addWidget(self.tabs)

        # Build tabs
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
        
        self.arabic_font = None
        font_db = QFontDatabase()
        available_fonts = font_db.families()
        
        for font_name in arabic_fonts:
            if font_name in available_fonts:
                self.arabic_font = QFont(font_name, 11)
                self.arabic_font.setStyleHint(QFont.System)
                break
        
        if not self.arabic_font:
            self.arabic_font = QFont("Arial", 11)
        
        # Set application-wide font
        self.setFont(self.arabic_font)
        
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
        tab = QWidget()
        outer = QVBoxLayout(tab)
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

        # New button for adding custom items
        self.btn_add_custom = QPushButton("إضافة منتج جديد")
        self.btn_add_custom.setObjectName("warning")
        self.btn_add_custom.setMinimumHeight(45)
        self.btn_add_custom.setMinimumWidth(150)

        row4.addWidget(self.btn_bill_add)
        row4.addWidget(self.btn_bill_remove)
        row4.addStretch()
        row4.addWidget(self.btn_add_custom)
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
        self.tbl_bill.setMinimumHeight(300)
        self.tbl_bill.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        table_layout.addWidget(self.tbl_bill)
        outer.addWidget(table_group)

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

        self.tabs.addTab(tab, "الفاتورة الحالية")

        # Font for bill table names
        self._bill_name_font = QFont(self.arabic_font.family(), 13, QFont.Bold)

    # ---------- Stock Tab ----------
    def _build_stock_tab(self):
        tab = QWidget()
        outer = QVBoxLayout(tab)
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

        # Second row - Price, Quantity, Category
        row2 = QHBoxLayout()
        row2.setSpacing(10)

        self.stk_price = QDoubleSpinBox()
        self.stk_price.setMaximum(10**9)
        self.stk_price.setDecimals(2)
        self.stk_price.setMinimumHeight(45)

        self.stk_qty = QDoubleSpinBox()
        self.stk_qty.setMaximum(10**9)
        self.stk_qty.setDecimals(3)
        self.stk_qty.setMinimumHeight(45)

        self.stk_cat = QComboBox()
        self.stk_cat.setMinimumHeight(45)

        self.btn_stk_new_cat = QPushButton("تصنيف جديد")
        self.btn_stk_new_cat.setMinimumHeight(45)
        self.btn_stk_new_cat.setMinimumWidth(100)

        row2.addWidget(QLabel("السعر:"), 0)
        row2.addWidget(self.stk_price, 1)
        row2.addWidget(QLabel("المخزون:"), 0)
        row2.addWidget(self.stk_qty, 1)
        row2.addWidget(QLabel("التصنيف:"), 0)
        row2.addWidget(self.stk_cat, 1)
        row2.addWidget(self.btn_stk_new_cat, 0)
        form_layout.addLayout(row2)

        # Third row - Photo path and buttons
        row3 = QHBoxLayout()
        row3.setSpacing(10)

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
        self.preview = QLabel("لا توجد صورة")
        self.preview.setFixedSize(120, 120)
        self.preview.setStyleSheet("""
            border: 2px solid #64748b; 
            border-radius: 8px; 
            background-color: #334155;
            color: #cbd5e1;
        """)
        self.preview.setAlignment(Qt.AlignCenter)

        row3.addWidget(QLabel("الصورة:"), 0)
        row3.addWidget(self.stk_photo, 2)
        row3.addWidget(self.btn_stk_browse, 0)
        row3.addWidget(self.btn_stk_camera, 0)
        row3.addWidget(self.preview, 0)
        form_layout.addLayout(row3)

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

        # Stock table with pagination
        table_group = QGroupBox("قائمة المخزون")
        table_layout = QVBoxLayout(table_group)

        self.tbl_stock = QTableWidget(0, 10)
        self.tbl_stock.setHorizontalHeaderLabels([
            "ID", "الاسم", "التصنيف", "الباركود", "السعر", 
            "المخزون", "الحالة", "الصورة", "تاريخ الإضافة", "cat_id"
        ])
        
        # Hide unnecessary columns
        self.tbl_stock.horizontalHeader().setSectionHidden(0, True)  # ID
        self.tbl_stock.horizontalHeader().setSectionHidden(7, True)  # Photo path
        self.tbl_stock.horizontalHeader().setSectionHidden(9, True)  # cat_id
        
        # Set responsive behavior
        header = self.tbl_stock.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Name stretches
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Category
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Barcode
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Price
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Stock
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents) # Status
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents) # Date
        
        self.tbl_stock.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_stock.setAlternatingRowColors(True)
        self.tbl_stock.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Disable auto-selection on double-click for better editing experience
        self.tbl_stock.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        table_layout.addWidget(self.tbl_stock)
        
        # Pagination controls for stock
        pagination_layout = QHBoxLayout()
        
        self.btn_stk_prev = QPushButton("السابق")
        self.btn_stk_prev.setObjectName("secondary")
        self.btn_stk_prev.setMinimumHeight(35)
        
        self.lbl_stk_page = QLabel("الصفحة 1 من 1")
        self.lbl_stk_page.setAlignment(Qt.AlignCenter)
        
        self.btn_stk_next = QPushButton("التالي")
        self.btn_stk_next.setObjectName("secondary")
        self.btn_stk_next.setMinimumHeight(35)
        
        pagination_layout.addWidget(self.btn_stk_prev)
        pagination_layout.addWidget(self.lbl_stk_page)
        pagination_layout.addWidget(self.btn_stk_next)
        
        table_layout.addLayout(pagination_layout)
        
        outer.addWidget(table_group)

        self.tabs.addTab(tab, "المخزون")
        # ui_main.py (Part 2 - Sales and Settings Tabs)
    # ---------- Sales Tab ----------
    def _build_sales_tab(self):
        tab = QWidget()
        outer = QVBoxLayout(tab)
        outer.setSpacing(12)

        # KPI Section
        kpi_group = QGroupBox("ملخص المبيعات")
        kpi_layout = QHBoxLayout(kpi_group)
        kpi_layout.setSpacing(20)

        # First row of KPIs
        kpi_row1 = QHBoxLayout()
        kpi_row1.setSpacing(20)
        
        self.lbl_total_sales = QLabel("إجمالي المبيعات: 0.00")
        self.lbl_total_sales.setObjectName("KPI")
        self.lbl_total_sales.setMinimumWidth(200)
        
        self.lbl_today_sales = QLabel("مبيعات اليوم: 0.00")
        self.lbl_today_sales.setObjectName("KPI")
        self.lbl_today_sales.setMinimumWidth(200)
        
        kpi_row1.addWidget(self.lbl_total_sales)
        kpi_row1.addWidget(self.lbl_today_sales)
        kpi_row1.addStretch()
        kpi_layout.addLayout(kpi_row1)
        
        # Second row for latest sale (separate line to prevent overlap)
        kpi_row2 = QHBoxLayout()
        kpi_row2.setSpacing(20)
        
        self.lbl_latest_sale = QLabel("آخر عملية: -")
        self.lbl_latest_sale.setObjectName("KPI")
        self.lbl_latest_sale.setMinimumWidth(400)
        self.lbl_latest_sale.setWordWrap(True)  # Allow text wrapping

        kpi_row2.addWidget(self.lbl_latest_sale)
        kpi_row2.addStretch()
        kpi_layout.addLayout(kpi_row2)
        
        outer.addWidget(kpi_group)

        # Sales table with pagination
        sales_group = QGroupBox("قائمة المبيعات")
        sales_layout = QVBoxLayout(sales_group)

        self.tbl_sales = QTableWidget(0, 3)
        self.tbl_sales.setHorizontalHeaderLabels([
            "رقم العملية", "التاريخ والوقت", "الإجمالي"
        ])
        
        # Set responsive behavior
        header = self.tbl_sales.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Fixed width for datetime
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        self.tbl_sales.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_sales.setAlternatingRowColors(True)
        self.tbl_sales.setMaximumHeight(250)
        
        sales_layout.addWidget(self.tbl_sales)

        # Pagination controls for sales
        sales_pagination_layout = QHBoxLayout()
        
        self.btn_sales_prev = QPushButton("السابق")
        self.btn_sales_prev.setObjectName("secondary")
        self.btn_sales_prev.setMinimumHeight(35)
        
        self.lbl_sales_page = QLabel("الصفحة 1 من 1")
        self.lbl_sales_page.setAlignment(Qt.AlignCenter)
        
        self.btn_sales_next = QPushButton("التالي")
        self.btn_sales_next.setObjectName("secondary")
        self.btn_sales_next.setMinimumHeight(35)
        
        sales_pagination_layout.addWidget(self.btn_sales_prev)
        sales_pagination_layout.addWidget(self.lbl_sales_page)
        sales_pagination_layout.addWidget(self.btn_sales_next)
        
        sales_layout.addLayout(sales_pagination_layout)

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

        outer.addWidget(sales_group)

        # Sale details table
        details_group = QGroupBox("تفاصيل العملية المحددة")
        details_layout = QVBoxLayout(details_group)

        self.tbl_sale_details = QTableWidget(0, 6)
        self.tbl_sale_details.setHorizontalHeaderLabels([
            "ID Det", "الاسم", "الكمية", "سعر الوحدة", "الإجمالي", "الباركود"
        ])
        
        # Hide ID and barcode columns for cleaner display
        self.tbl_sale_details.horizontalHeader().setSectionHidden(0, True)
        self.tbl_sale_details.horizontalHeader().setSectionHidden(5, True)
        
        # Set responsive behavior
        header2 = self.tbl_sale_details.horizontalHeader()
        header2.setSectionResizeMode(1, QHeaderView.Stretch)          # Name stretches
        header2.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Quantity
        header2.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Price each
        header2.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Total
        
        self.tbl_sale_details.setAlternatingRowColors(True)
        self.tbl_sale_details.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        details_layout.addWidget(self.tbl_sale_details)
        
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
        outer.addWidget(details_group)

        self.tabs.addTab(tab, "المبيعات")

    # ---------- Settings Tab ----------
    def _build_settings_tab(self):
        tab = QWidget()
        outer = QVBoxLayout(tab)
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

        self.tabs.addTab(tab, "الإعدادات")

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
                        self.preview.width() - 4, 
                        self.preview.height() - 4, 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    self.preview.setPixmap(scaled_pixmap)
                    return
            except:
                pass
        
        self.preview.clear()
        self.preview.setText("لا توجد صورة")