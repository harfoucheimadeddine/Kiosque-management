# controllers.py (fixed custom price calculation and added purchase price feature)
import os
from datetime import datetime
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QMessageBox, QInputDialog, QCompleter
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QTextDocument

from ui_main import MainUI
import models

try:
    import cv2
except Exception:
    cv2 = None

try:
    from pyzbar.pyzbar import decode as zbar_decode
except Exception:
    zbar_decode = None

ASSETS_PHOTOS_DIR = os.path.join("assets", "photos")
os.makedirs(ASSETS_PHOTOS_DIR, exist_ok=True)

ALLOWED_BARCODE_LENGTHS = {8, 12, 13}

def is_valid_barcode(code: str) -> bool:
    return code.isdigit() and (len(code) in ALLOWED_BARCODE_LENGTHS)

def fmt_qty(val):
    return f"{val:.0f}" if val == int(val) else f"{val:.1f}"

def fmt_money(val):
    return f"{val:.0f}" if val == int(val) else f"{val:.2f}"

class Controller(MainUI):
    def __init__(self):
        super().__init__()

        self.currency = "د.ج"
        self.current_bill_items = []  # List to track items in the current bill

        # Setup window controls
        self.btn_min.clicked.connect(self.showMinimized)
        self.btn_max.clicked.connect(self._toggle_max_restore)
        self.btn_close.clicked.connect(self.close)

        # Load settings
        self._load_settings_or_first_run()

        # Initialize tabs
        self._load_categories()
        self._load_stock_table()
        self._load_sales_tab()
        self._apply_currency_to_inputs()

        # Bill signals
        self.btn_bill_find.clicked.connect(self._bill_find)
        self.btn_bill_add.clicked.connect(self._bill_add)
        self.btn_bill_remove.clicked.connect(self._bill_remove_selected)
        self.btn_bill_save.clicked.connect(self._bill_save)
        self.btn_print_bill.clicked.connect(self._bill_print)
        self.btn_scanner_info.clicked.connect(self._show_scanner_info)
        self.btn_add_custom.clicked.connect(self._add_custom_item)

        # Manual price checkbox signal
        self.chk_manual.stateChanged.connect(self._toggle_manual_price)

        # Autocomplete feature
        self.in_name.textChanged.connect(self._on_name_text_changed)
        self._setup_autocomplete()

        self.in_barcode.returnPressed.connect(self._handle_scanned_barcode)

        # Stock signals
        self.btn_stk_browse.clicked.connect(self._browse_photo)
        self.btn_stk_camera.clicked.connect(self._capture_photo)
        self.btn_stk_new_cat.clicked.connect(self._add_new_category)
        self.btn_stk_add.clicked.connect(self._stock_add)
        self.btn_stk_update.clicked.connect(self._stock_update)
        self.btn_stk_delete.clicked.connect(self._stock_delete)
        self.btn_stk_refresh.clicked.connect(self._load_stock_table)
        self.tbl_stock.clicked.connect(self._stock_fill_form_from_selection)

        # Sales signals
        self.btn_sale_refresh.clicked.connect(self._load_sales_tab)
        self.btn_sale_view.clicked.connect(self._sales_view_selected)
        self.btn_sale_delete.clicked.connect(self._sales_delete_selected)
        self.btn_sale_delete_item.clicked.connect(self._sales_delete_item)
        self.btn_sale_update_item.clicked.connect(self._sales_update_item)
        self.tbl_sales.itemSelectionChanged.connect(self._sales_view_selected)

        # Settings
        self.btn_settings_save.clicked.connect(self._save_settings_from_tab)

        # Responsive tables
        self._setup_responsive_tables()

    def _setup_autocomplete(self):
        # Setup autocomplete with just product names, not barcodes
        all_items = models.get_items()
        suggestions = [item['name'] for item in all_items if item['name']]
        completer = QCompleter(suggestions)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)  # Allow partial matching
        self.in_name.setCompleter(completer)
        
        # Connect completer selection to fill other fields
        completer.activated.connect(self._on_autocomplete_selected)

    def _toggle_max_restore(self):
        if self.isMaximized():
            self.showNormal()
            self.btn_max.setText("⬜")
        else:
            self.showMaximized()
            self.btn_max.setText("❐")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_table_responsiveness()

    def _setup_responsive_tables(self):
        tables = [self.tbl_bill, self.tbl_stock, self.tbl_sales, self.tbl_sale_details]
        for table in tables:
            if table:
                table.horizontalHeader().setStretchLastSection(False)
                table.setWordWrap(True)

    def _update_table_responsiveness(self):
        try:
            tables = [
                (self.tbl_bill, [2, 3, 4]),
                (self.tbl_stock, [2, 3, 4, 5, 6, 8]),
                (self.tbl_sales, [0, 1, 2]),
                (self.tbl_sale_details, [2, 3, 4, 5])
            ]
            for table, cols in tables:
                if table and table.rowCount() > 0:
                    for col in cols:
                        if col < table.columnCount():
                            table.resizeColumnToContents(col)
        except Exception:
            pass

    # Settings
    def _load_settings_or_first_run(self):
        s = models.get_settings()
        if not s:
            QMessageBox.information(self, "الإعداد الأول", "مرحبًا! برجاء إدخال معلومات المتجر أولًا.")
            shop_name, ok1 = QInputDialog.getText(self, "اسم المتجر", "اسم المتجر:")
            if not ok1 or not shop_name.strip():
                shop_name = "متجري"
            contact, _ = QInputDialog.getText(self, "معلومات الاتصال", "هاتف / بريد إلكتروني (اختياري):")
            location, _ = QInputDialog.getText(self, "الموقع", "العنوان / الموقع (اختياري):")
            currency, ok4 = QInputDialog.getText(self, "العملة", "اكتب رمز العملة (مثال: د.ج ، ر.س ، MAD ، USD):")
            if not ok4 or not currency.strip():
                currency = "د.ج"
            models.save_settings(shop_name.strip(), (contact or "").strip(), (location or "").strip(), currency.strip())
            s = models.get_settings()
        self._apply_settings_to_ui(s)

    def _apply_settings_to_ui(self, s):
        self.lbl_title.setText(s["shop_name"])
        self.setWindowTitle(s["shop_name"])
        self.sett_shop_name.setText(s["shop_name"])
        self.sett_contact.setText(s["contact"] or "")
        self.sett_location.setText(s["location"] or "")
        self.sett_currency.setText(s["currency"])
        self.currency = s["currency"]

    def _save_settings_from_tab(self):
        shop_name = self.sett_shop_name.text().strip() or "متجري"
        contact = self.sett_contact.text().strip()
        location = self.sett_location.text().strip()
        currency = self.sett_currency.text().strip() or "د.ج"
        models.save_settings(shop_name, contact, location, currency)
        s = models.get_settings()
        self._apply_settings_to_ui(s)
        self._apply_currency_to_inputs()
        self.msg("تم", "تم حفظ الإعدادات.")

    def _apply_currency_to_inputs(self):
        self.in_price.setPrefix(f"السعر ({self.currency}): ")
        self.stk_price.setPrefix(f"السعر ({self.currency}): ")
        self.stk_purchase_price.setPrefix(f"سعر الشراء ({self.currency}): ")
        self.stk_qty.setPrefix("المخزون: ")
        self.in_qty.setPrefix("الكمية: ")
        self._bill_recalc_total()
        self._load_sales_tab()

    # Categories
    def _load_categories(self):
        cats = models.get_categories()
        self.stk_cat.clear()
        for c in cats:
            self.stk_cat.addItem(c["name"], c["id"])

    def _add_new_category(self):
        name, ok = QInputDialog.getText(self, "تصنيف جديد", "اسم التصنيف:")
        if ok and name.strip():
            try:
                models.add_category(name.strip())
                self._load_categories()
                self.msg("تم", "تم إضافة التصنيف.")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"تعذر إضافة التصنيف:\n{e}")

    # Stock Methods
    def _browse_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "اختر صورة", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.stk_photo.setText(path)
            self.set_preview_image(path)

    def _capture_photo(self):
        if cv2 is None:
            QMessageBox.warning(self, "الكاميرا", "OpenCV غير مثبت.")
            return
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            QMessageBox.warning(self, "الكاميرا", "تعذر فتح الكاميرا.")
            return
        QMessageBox.information(self, "التقاط", "سيتم فتح نافذة الكاميرا.")
        path_saved = None
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("Camera - Press C to capture, Q to cancel", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c'):
                fname = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                path_saved = os.path.join(ASSETS_PHOTOS_DIR, fname)
                cv2.imwrite(path_saved, frame)
                break
            elif key == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        if path_saved:
            self.stk_photo.setText(path_saved)
            self.set_preview_image(path_saved)
            self.msg("تم", f"تم حفظ الصورة: {path_saved}")

    def _stock_add(self):
        try:
            name = self.stk_name.text().strip()
            if not name:
                self.msg("تنبيه", "الرجاء إدخال الاسم.")
                return
            barcode = self.stk_barcode.text().strip()
            if barcode and not is_valid_barcode(barcode):
                self.msg("خطأ", "الباركود غير صالح")
                return
            cat_id = self.stk_cat.currentData()
            price = float(self.stk_price.value())
            purchase_price = float(self.stk_purchase_price.value())
            qty = float(self.stk_qty.value())
            
            # Prevent negative stock
            if qty < 0:
                self.msg("خطأ", "لا يمكن إضافة كمية مخزون سالبة.")
                return
                
            photo = self.stk_photo.text().strip() or None
            models.add_item(name, cat_id, barcode or None, price, qty, photo, purchase_price=purchase_price)
            self._load_stock_table()
            self.msg("تم", "تمت إضافة الصنف.")
            self._clear_stock_form()
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"تعذر إضافة الصنف:\n{e}")

    def _stock_update(self):
        row = self._selected_row(self.tbl_stock)
        if row is None:
            self.msg("تنبيه", "اختر صفًا للتعديل.")
            return
        item_id = int(self.tbl_stock.item(row, 0).text())
        try:
            name = self.stk_name.text().strip()
            if not name:
                self.msg("تنبيه", "الرجاء إدخال الاسم.")
                return
            barcode = self.stk_barcode.text().strip()
            if barcode and not is_valid_barcode(barcode):
                self.msg("خطأ", "الباركود غير صالح")
                return
            cat_id = self.stk_cat.currentData()
            price = float(self.stk_price.value())
            purchase_price = float(self.stk_purchase_price.value())
            qty = float(self.stk_qty.value())
            
            # Prevent negative stock
            if qty < 0:
                self.msg("خطأ", "لا يمكن إضافة كمية مخزون سالبة.")
                return
                
            photo = self.stk_photo.text().strip() or None
            models.update_item(item_id, name, cat_id, barcode or None, price, qty, photo, purchase_price=purchase_price)
            self._load_stock_table()
            self.msg("تم", "تم تعديل الصنف.")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"تعذر تعديل الصنف:\n{e}")

    def _stock_delete(self):
        row = self._selected_row(self.tbl_stock)
        if row is None:
            self.msg("تنبيه", "اختر صفًا للحذف.")
            return
        item_id = int(self.tbl_stock.item(row, 0).text())
        confirm = QMessageBox.question(self, "تأكيد", "سيتم حذف الصنف وجميع تفاصيل البيع المرتبطة به.\nهل أنت متأكد؟")
        if confirm == QMessageBox.Yes:
            try:
                models.delete_item(item_id)
                self._load_stock_table()
                self.msg("تم", "تم حذف الصنف.")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"تعذر حذف الصنف:\n{e}")

    def _clear_stock_form(self):
        self.stk_name.clear()
        self.stk_barcode.clear()
        self.stk_price.setValue(0)
        self.stk_purchase_price.setValue(0)
        self.stk_qty.setValue(0)
        self.stk_photo.clear()
        self.set_preview_image("")

    def _stock_fill_form_from_selection(self):
        row = self._selected_row(self.tbl_stock)
        if row is None:
            return
        self.stk_name.setText(self.tbl_stock.item(row, 1).text())
        cat_name = self.tbl_stock.item(row, 2).text()
        idx = self.stk_cat.findText(cat_name)
        if idx >= 0:
            self.stk_cat.setCurrentIndex(idx)
        self.stk_barcode.setText(self.tbl_stock.item(row, 3).text())
        self.stk_price.setValue(float(self.tbl_stock.item(row, 4).text()))
        self.stk_qty.setValue(float(self.tbl_stock.item(row, 5).text()))
        # Get purchase price from column 10 (hidden)
        if self.tbl_stock.columnCount() > 10:
            purchase_price = float(self.tbl_stock.item(row, 10).text() or "0")
            self.stk_purchase_price.setValue(purchase_price)
        self.stk_photo.setText(self.tbl_stock.item(row, 7).text())
        self.set_preview_image(self.tbl_stock.item(row, 7).text())

    def _load_stock_table(self):
        items = models.get_items()
        self.tbl_stock.setRowCount(0)
        for r in items:
            row = self.tbl_stock.rowCount()
            self.tbl_stock.insertRow(row)
            self.tbl_stock.setItem(row, 0, QTableWidgetItem(str(r["id"])))
            name_item = QTableWidgetItem(r["name"])
            name_item.setFont(QFont(self.arabic_font.family(), 13, QFont.Bold))
            self.tbl_stock.setItem(row, 1, name_item)
            self.tbl_stock.setItem(row, 2, QTableWidgetItem(r["category_name"] or "غير مصنّف"))
            self.tbl_stock.setItem(row, 3, QTableWidgetItem(r["barcode"] or ""))
            self.tbl_stock.setItem(row, 4, QTableWidgetItem(fmt_money(r['price'])))
            
            # Ensure stock is never negative
            stock_count = max(0, r['stock_count'] or 0)
            stock_item = QTableWidgetItem(fmt_qty(stock_count))
            if stock_count <= 0:
                stock_item.setForeground(Qt.red)
            self.tbl_stock.setItem(row, 5, stock_item)
            
            status_text = "نفد المخزون" if stock_count <= 0 else "متاح"
            status_item = QTableWidgetItem(status_text)
            if stock_count <= 0:
                status_item.setForeground(Qt.red)
            self.tbl_stock.setItem(row, 6, status_item)
            self.tbl_stock.setItem(row, 7, QTableWidgetItem(r["photo_path"] or ""))
            self.tbl_stock.setItem(row, 8, QTableWidgetItem(r["add_date"] or ""))
            self.tbl_stock.setItem(row, 9, QTableWidgetItem(str(r["category_id"] or "")))
            # Add purchase price column (hidden)
            self.tbl_stock.setItem(row, 10, QTableWidgetItem(str(r["purchase_price"] or "0")))
            self.tbl_stock.setRowHeight(row, 40)
        self._update_table_responsiveness()

    # Bill Methods
    def _handle_scanned_barcode(self):
        barcode = self.in_barcode.text().strip()
        if not barcode:
            return
        self._bill_find()

    def _on_autocomplete_selected(self, text):
        """Handle when user selects an item from autocomplete"""
        # Find the item by name
        items = models.search_items_by_name(text)
        if items:
            item = items[0]
            # Fill barcode field (not name field)
            self.in_barcode.setText(item["barcode"] or "")
            # Set price if not in manual mode
            if not self.chk_manual.isChecked():
                self.in_price.setValue(float(item["price"]))

    def _on_name_text_changed(self, text):
        # Auto-search when typing in name field - only fill other fields
        if len(text) > 2 and not text.endswith(' | '):  # Avoid triggering on old autocomplete format
            items = models.search_items_by_name(text)
            if items:
                # Only set barcode and price, never touch the name field
                self.in_barcode.setText(items[0]["barcode"] or "")
                if not self.chk_manual.isChecked():
                    self.in_price.setValue(float(items[0]["price"]))

    def _toggle_manual_price(self, state):
        """Enable/disable price field based on manual price checkbox"""
        self.in_price.setEnabled(state == Qt.Checked)

    def _bill_find(self):
        barcode = self.in_barcode.text().strip()
        name = self.in_name.text().strip()
        
        item = None
        if barcode:
            item = models.get_item_by_barcode(barcode)
        elif name:
            items = models.search_items_by_name(name)
            if items:
                item = items[0]
        
        if item:
            # FIXED: Use dictionary-style access for sqlite3.Row objects
            current_name = self.in_name.text().strip()
            item_barcode = item["barcode"] if "barcode" in item.keys() else ""
            
            # Only set name if field is empty or contains a barcode
            if not current_name or current_name == item_barcode:
                self.in_name.setText(item["name"])
            
            # Always update barcode field
            self.in_barcode.setText(item_barcode)
            
            # Set price based on manual mode
            if not self.chk_manual.isChecked():
                self.in_price.setValue(float(item["price"]))
                
            # Show stock information
            stock = max(0, item["stock_count"] or 0)  # Ensure stock is never negative
            if stock == int(stock):
                stock_text = f"{stock:.0f}"
            else:
                stock_text = f"{stock:.1f}"
            self.msg("معلومات المخزون", f"المتاح في المخزون: {stock_text}")
        else:
            # Item not found, allow adding as custom item
            if barcode or name:
                reply = QMessageBox.question(
                    self, 
                    "منتج غير موجود", 
                    "المنتج غير موجود في قاعدة البيانات. هل تريد إضافه إلى الفاتورة كمنتج مخصص؟",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    # Enable manual price for custom item
                    self.chk_manual.setChecked(True)
                    self.in_price.setEnabled(True)
                    self.in_price.setValue(0)
                    self.in_price.setFocus()


    def _add_custom_item(self):
        """Add a custom item to the database from bill tab"""
        name = self.in_name.text().strip()
        barcode = self.in_barcode.text().strip()
        price = float(self.in_price.value())
        
        if not name:
            self.msg("خطأ", "الرجاء إدخال اسم المنتج.")
            return
        
        if not barcode:
            # Generate a temporary barcode for custom items
            from datetime import datetime
            barcode = f"TEMP_{datetime.now().strftime('%H%M%S')}"
        
        # Ask if user wants to save to database
        reply = QMessageBox.question(
            self,
            "حفظ المنتج",
            "هل تريد حفظ هذا المنتج في قاعدة البيانات؟",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Save to database
            try:
                # Get default category (uncategorized)
                default_cat = models.get_category_by_name("غير مصنّف")
                cat_id = default_cat["id"] if default_cat else None
                
                # Add to database
                models.add_item(name, cat_id, barcode or None, price, 0, None)
                self.msg("تم", "تم حفظ المنتج في قاعدة البيانات.")
                self._load_stock_table()
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"تعذر حفظ المنتج:\n{e}")
                return
        
        # Add to bill even if not saved to database
        self._bill_add_custom_item(name, barcode, price)

    def _bill_add_custom_item(self, name, barcode, price):
        """Add custom item to bill (not in database)"""
        qty = float(self.in_qty.value())
        
        if not name or qty <= 0:
            self.msg("خطأ", "الرجاء إدخال اسم المنتج وكمية صحيحة.")
            return
        
        # Add to bill table
        row = self.tbl_bill.rowCount()
        self.tbl_bill.insertRow(row)
        
        # Calculate total
        total = price * qty
        
        # Add items to table
        self.tbl_bill.setItem(row, 0, QTableWidgetItem(barcode or ""))
        name_item = QTableWidgetItem(name)
        name_item.setFont(self._bill_name_font)
        self.tbl_bill.setItem(row, 1, name_item)
        self.tbl_bill.setItem(row, 2, QTableWidgetItem(fmt_money(price)))
        self.tbl_bill.setItem(row, 3, QTableWidgetItem(fmt_qty(qty)))
        self.tbl_bill.setItem(row, 4, QTableWidgetItem(fmt_money(total)))
        self.tbl_bill.setItem(row, 5, QTableWidgetItem("CUSTOM"))  # Mark as custom item
        
        # Add to internal tracking
        self.current_bill_items.append({
            "id": -1,  # Custom items have negative ID
            "name": name,
            "barcode": barcode,
            "price": price,
            "qty": qty,
            "total": total,
            "is_custom": True
        })
        
        # Recalculate total
        self._bill_recalc_total()
        
        # Clear input fields for next item
        self.in_barcode.clear()
        self.in_name.clear()
        self.in_qty.setValue(1.0)
        self.in_price.setValue(0.0)
        self.chk_manual.setChecked(False)
        
        # Set focus back to barcode field
        self.in_barcode.setFocus()

    def _bill_add(self):
        # Get item details
        barcode = self.in_barcode.text().strip()
        name = self.in_name.text().strip()
        price = float(self.in_price.value())
        qty = float(self.in_qty.value())
        
        if not name or qty <= 0:
            self.msg("خطأ", "الرجاء إدخال اسم المنتج وكمية صحيحة.")
            return
        
        # Check if item exists in database
        item = None
        if barcode:
            item = models.get_item_by_barcode(barcode)
        if not item and name:
            items = models.search_items_by_name(name)
            if items:
                item = items[0]
        
        if not item:
            # Item not in database, add as custom item
            self._bill_add_custom_item(name, barcode, price)
            return
        
        # Check stock availability
        available_stock = max(0, item["stock_count"] or 0)  # Ensure stock is never negative
        if qty > available_stock:
            self.msg("خطأ", f"الكمية المطلوبة ({qty}) أكبر من المخزون المتاح ({available_stock}).")
            return
        
        # Add to bill table
        row = self.tbl_bill.rowCount()
        self.tbl_bill.insertRow(row)
        
        # Calculate total
        total = price * qty
        
        # Add items to table
        self.tbl_bill.setItem(row, 0, QTableWidgetItem(barcode or ""))
        name_item = QTableWidgetItem(name)
        name_item.setFont(self._bill_name_font)
        self.tbl_bill.setItem(row, 1, name_item)
        self.tbl_bill.setItem(row, 2, QTableWidgetItem(fmt_money(price)))
        self.tbl_bill.setItem(row, 3, QTableWidgetItem(fmt_qty(qty)))
        self.tbl_bill.setItem(row, 4, QTableWidgetItem(fmt_money(total)))
        self.tbl_bill.setItem(row, 5, QTableWidgetItem(str(item["id"])))  # Store item ID
        
        # Add to internal tracking
        self.current_bill_items.append({
            "id": item["id"],
            "name": name,
            "barcode": barcode,
            "price": price,
            "qty": qty,
            "total": total,
            "is_custom": False
        })
        
        # Recalculate total
        self._bill_recalc_total()
        
        # Clear input fields for next item
        self.in_barcode.clear()
        self.in_name.clear()
        self.in_qty.setValue(1.0)
        self.in_price.setValue(0.0)
        self.chk_manual.setChecked(False)
        
        # Set focus back to barcode field
        self.in_barcode.setFocus()

    def _bill_remove_selected(self):
        row = self._selected_row(self.tbl_bill)
        if row is None:
            self.msg("تنبيه", "اختر صفًا للحذف.")
            return
        self.tbl_bill.removeRow(row)
        if row < len(self.current_bill_items):
            self.current_bill_items.pop(row)
        self._bill_recalc_total()

    def _bill_recalc_total(self):
        total = 0
        for i in range(self.tbl_bill.rowCount()):
            total += float(self.tbl_bill.item(i, 4).text())
        self.lbl_total.setText(f"{fmt_money(total)} {self.currency}")

    def _bill_save(self):
        if self.tbl_bill.rowCount() == 0:
            self.msg("تنبيه", "لا توجد أصناف في الفاتورة.")
            return
        try:
            # Create sale record
            total = sum(float(self.tbl_bill.item(i, 4).text()) for i in range(self.tbl_bill.rowCount()))
            sale_id = models.add_sale(total)
            
            # Add sale details
            for i in range(self.tbl_bill.rowCount()):
                item_id = self.tbl_bill.item(i, 5).text()
                if item_id == "CUSTOM":
                    continue  # Skip custom items (not in database)
                
                price_each = float(self.tbl_bill.item(i, 2).text())
                quantity = float(self.tbl_bill.item(i, 3).text())
                models.add_sale_detail(sale_id, int(item_id), quantity, price_each)
            
            # Clear bill
            self.tbl_bill.setRowCount(0)
            self.current_bill_items.clear()
            self._bill_recalc_total()
            
            # Show success message
            self.msg("تم", f"تم حفظ الفاتورة رقم {sale_id}.")
            
            # Refresh sales tab
            self._load_sales_tab()
            
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"تعذر حفظ الفاتورة:\n{e}")

    def _bill_print(self):
        if self.tbl_bill.rowCount() == 0:
            self.msg("تنبيه", "لا توجد أصناف في الفاتورة للطباعة.")
            return
        
        # Create printer and dialog
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() != QPrintDialog.Accepted:
            return
        
        # Create HTML content for receipt
        html = f"""
        <html>
        <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; direction: rtl; text-align: right; }}
            .header {{ text-align: center; margin-bottom: 20px; }}
            .shop-name {{ font-size: 20px; font-weight: bold; }}
            .contact {{ font-size: 14px; }}
            .receipt-info {{ margin: 10px 0; }}
            .items-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            .items-table th, .items-table td {{ border: 1px solid #000; padding: 5px; }}
            .total {{ font-weight: bold; font-size: 16px; margin-top: 10px; }}
            .footer {{ margin-top: 20px; text-align: center; font-size: 12px; }}
        </style>
        </head>
        <body>
            <div class="header">
                <div class="shop-name">{self.lbl_title.text()}</div>
                <div class="contact">{self.sett_contact.text()}</div>
                <div class="contact">{self.sett_location.text()}</div>
            </div>
            
            <div class="receipt-info">
                <div>التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
            
            <table class="items-table">
                <tr>
                    <th>الصنف</th>
                    <th>السعر</th>
                    <th>الكمية</th>
                    <th>المجموع</th>
                </tr>
        """
        
        # Add items to receipt
        for i in range(self.tbl_bill.rowCount()):
            name = self.tbl_bill.item(i, 1).text()
            price = self.tbl_bill.item(i, 2).text()
            qty = self.tbl_bill.item(i, 3).text()
            total = self.tbl_bill.item(i, 4).text()
            
            html += f"""
                <tr>
                    <td>{name}</td>
                    <td>{price}</td>
                    <td>{qty}</td>
                    <td>{total}</td>
                </tr>
            """
        
        # Add total
        total = self.lbl_total.text()
        html += f"""
            </table>
            
            <div class="total">الإجمالي: {total}</div>
            
            <div class="footer">
                شكرًا لزيارتكم<br>
                {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </body>
        </html>
        """
        
        # Print the document
        doc = QTextDocument()
        doc.setHtml(html)
        doc.print_(printer)

    def _show_scanner_info(self):
        info = """
        دعم الباركود:
        - يمكنك مسح الباركود مباشرة في حقل الباركود
        - يدعم النظام الباركود بطول 8، 12، 13 رقمًا
        - اضغط Enter بعد مسح الباركود للبحث تلقائيًا
        
        خيارات البحث:
        - البحث بالباركود (الأولوية)
        - البحث بالاسم (إذا لم يتم إدخال باركود)
        - الضغط على زر البحث أو Enter للبحث
        
        إضافة صنف مخصص:
        - إذا لم يكن المنتج في قاعدة البيانات
        - يمكنك إضافته كمنتج مخصص
        - سيتم حفظه مؤقتًا في الفاتورة فقط
        """
        QMessageBox.information(self, "معلومات الماسح الضوئي", info)

    # Sales Methods
    def _load_sales_tab(self):
        sales = models.get_sales()
        self.tbl_sales.setRowCount(0)
        
        # Update KPIs
        total_sales = models.get_sales_total()
        today_sales = models.get_sales_summary_today()
        latest_sale = models.get_latest_sale()
        
        self.lbl_total_sales.setText(f"إجمالي المبيعات: {fmt_money(total_sales)} {self.currency}")
        self.lbl_today_sales.setText(f"مبيعات اليوم: {fmt_money(today_sales)} {self.currency}")
        
        if latest_sale:
            latest_text = f"آخر عملية: #{latest_sale['id']} - {latest_sale['datetime']} - {fmt_money(latest_sale['total_price'])} {self.currency}"
            self.lbl_latest_sale.setText(latest_text)
        else:
            self.lbl_latest_sale.setText("آخر عملية: لا توجد مبيعات")
        
        # Load sales table
        for r in sales:
            row = self.tbl_sales.rowCount()
            self.tbl_sales.insertRow(row)
            self.tbl_sales.setItem(row, 0, QTableWidgetItem(str(r["id"])))
            self.tbl_sales.setItem(row, 1, QTableWidgetItem(r["datetime"]))
            self.tbl_sales.setItem(row, 2, QTableWidgetItem(f"{fmt_money(r['total_price'])} {self.currency}"))
            self.tbl_sales.setRowHeight(row, 35)
        self._update_table_responsiveness()

    def _sales_view_selected(self):
        row = self._selected_row(self.tbl_sales)
        if row is None:
            self.tbl_sale_details.setRowCount(0)
            return
        sale_id = int(self.tbl_sales.item(row, 0).text())
        details = models.get_sale_details(sale_id)
        self.tbl_sale_details.setRowCount(0)
        for r in details:
            row_det = self.tbl_sale_details.rowCount()
            self.tbl_sale_details.insertRow(row_det)
            self.tbl_sale_details.setItem(row_det, 0, QTableWidgetItem(str(r["id"])))
            self.tbl_sale_details.setItem(row_det, 1, QTableWidgetItem(r["item_name"]))
            self.tbl_sale_details.setItem(row_det, 2, QTableWidgetItem(fmt_qty(r["quantity"])))
            self.tbl_sale_details.setItem(row_det, 3, QTableWidgetItem(fmt_money(r["price_each"])))
            self.tbl_sale_details.setItem(row_det, 4, QTableWidgetItem(fmt_money(r["price_each"] * r["quantity"])))
            # Add purchase price column (visible in sales tab)
            purchase_price = r.get("purchase_price", 0) or 0
            self.tbl_sale_details.setItem(row_det, 5, QTableWidgetItem(fmt_money(purchase_price)))
            # Calculate profit
            profit = (r["price_each"] - purchase_price) * r["quantity"]
            profit_item = QTableWidgetItem(fmt_money(profit))
            if profit < 0:
                profit_item.setForeground(Qt.red)
            else:
                profit_item.setForeground(Qt.green)
            self.tbl_sale_details.setItem(row_det, 6, QTableWidgetItem(str(r["item_id"])))
            self.tbl_sale_details.setItem(row_det, 7, QTableWidgetItem(str(r["sale_id"])))
            self.tbl_sale_details.setRowHeight(row_det, 35)
        self._update_table_responsiveness()

    def _sales_delete_selected(self):
        row = self._selected_row(self.tbl_sales)
        if row is None:
            self.msg("تنبيه", "اختر فاتورة للحذف.")
            return
        sale_id = int(self.tbl_sales.item(row, 0).text())
        confirm = QMessageBox.question(self, "تأكيد", "سيتم حذف الفاتورة وكل تفاصيلها.\nهل أنت متأكد؟")
        if confirm == QMessageBox.Yes:
            try:
                models.delete_sale(sale_id)
                self._load_sales_tab()
                self.tbl_sale_details.setRowCount(0)
                self.msg("تم", "تم حذف الفاتورة.")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"تعذر حذف الفاتورة:\n{e}")

    def _sales_delete_item(self):
        row = self._selected_row(self.tbl_sale_details)
        if row is None:
            self.msg("تنبيه", "اختر صنفًا للحذف.")
            return
        detail_id = int(self.tbl_sale_details.item(row, 0).text())
        confirm = QMessageBox.question(self, "تأكيد", "هل تريد حذف هذا الصنف من الفاتورة؟")
        if confirm == QMessageBox.Yes:
            try:
                models.delete_sale_detail(detail_id)
                self._sales_view_selected()  # Refresh
                self.msg("تم", "تم حذف الصنف.")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"تعذر حذف الصنف:\n{e}")

    def _sales_update_item(self):
        row = self._selected_row(self.tbl_sale_details)
        if row is None:
            self.msg("تنبيه", "اختر صنفًا للتعديل.")
            return
        detail_id = int(self.tbl_sale_details.item(row, 0).text())
        item_id = int(self.tbl_sale_details.item(row, 6).text())
        sale_id = int(self.tbl_sale_details.item(row, 7).text())
        
        # Get current values
        current_qty = float(self.tbl_sale_details.item(row, 2).text())
        current_price = float(self.tbl_sale_details.item(row, 3).text())
        
        # Show dialog for new values
        new_qty, ok1 = QInputDialog.getDouble(self, "الكمية الجديدة", "الكمية:", current_qty, 0.1, 1000, 1)
        new_price, ok2 = QInputDialog.getDouble(self, "السعر الجديد", f"السعر ({self.currency}):", current_price, 0.01, 100000, 2)
        
        if ok1 and ok2:
            try:
                models.update_sale_detail(detail_id, new_qty, new_price)
                models.update_sale_total(sale_id)
                self._load_sales_tab()
                self._sales_view_selected()
                self.msg("تم", "تم تعديل الصنف.")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"تعذر تعديل الصنف:\n{e}")

    # Utility
    def _selected_row(self, table):
        selected = table.selectedItems()
        if not selected:
            return None
        return selected[0].row()

    def msg(self, title, text):
        QMessageBox.information(self, title, text)

    def set_preview_image(self, path):
        if not path or not os.path.exists(path):
            self.lbl_preview.setText("(لا توجد صورة)")
            self.lbl_preview.setStyleSheet("color: gray;")
            return
        self.lbl_preview.setText(f"📷 {os.path.basename(path)}")
        self.lbl_preview.setStyleSheet("color: blue; text-decoration: underline;")