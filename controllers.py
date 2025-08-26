# controllers.py (fixed custom price calculation and added purchase price feature)
import os
from datetime import datetime
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QMessageBox, QInputDialog, QCompleter
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QTextDocument

from ui_main import MainUI, ItemScanDialog # Import ItemScanDialog
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

        # Load settings
        self._load_settings_or_first_run()

        # Initialize tabs
        self._load_categories()
        self._load_stock_table()
        self._load_sales_tab()
        self._apply_currency_to_inputs()

        # Bill signals
        self.btn_bill_find.clicked.connect(self._bill_find_and_add_item_dialog) # Now uses the new dialog flow
        self.btn_bill_add.clicked.connect(self._bill_find_and_add_item_dialog)  # Also uses the new dialog flow
        self.btn_bill_remove.clicked.connect(self._bill_remove_selected)
        self.btn_bill_save.clicked.connect(self._bill_save)
        self.btn_print_bill.clicked.connect(self._bill_print)
        self.btn_scanner_info.clicked.connect(self._show_scanner_info)

        # Autocomplete feature for manual entry (if not using scanner)
        self.in_name.textChanged.connect(self._on_name_text_changed)
        self._setup_autocomplete()

        # Barcode return pressed now directly triggers the interactive dialog
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
        # This function is no longer needed as window controls are removed from UI
        pass 

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_table_responsiveness()

    def keyPressEvent(self, event):
        """Handle key press events for maximized toggle (F12) and restore (F11)."""
        if event.key() == Qt.Key_F12:
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized() # Use showMaximized to keep window decorations
        elif event.key() == Qt.Key_F11: # Changed from Escape to F11
            self.showNormal()
        super().keyPressEvent(event)

    def _setup_responsive_tables(self):
        tables = [self.tbl_bill, self.tbl_stock, self.tbl_sales, self.tbl_sale_details]
        for table in tables:
            if table:
                table.horizontalHeader().setStretchLastSection(False)
                table.setWordWrap(True)

    def _update_table_responsiveness(self):
        try:
            tables = [
                (self.tbl_bill, [2, 3, 4]), # Columns for price, qty, total
                (self.tbl_stock, [2, 3, 4, 5, 6, 8]), # Columns for category, barcode, price, stock, status, add_date
                (self.tbl_sales, [0, 1, 2]), # Columns for sale_id, datetime, total_price
                (self.tbl_sale_details, [2, 3, 4, 5]) # Columns for price_each, quantity, subtotal, purchase_price_each
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
            # Refresh autocomplete suggestions
            self._setup_autocomplete()
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
            # Refresh autocomplete suggestions
            self._setup_autocomplete()
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"تعذر تعديل الصنف:\n{e}")

    def _stock_delete(self):
        row = self._selected_row(self.tbl_stock)
        if row is None:
            self.msg("تنبيه", "اختر صفًا للحذف.")
            return
        item_id = int(self.tbl_stock.item(row, 0).text())
        confirm = QMessageBox.question(self, "تأكيد", "سيتم حذف الصنف وجميع تفاصيل البيع المرتبطة به.\nهل أنت متأكد؟", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                models.delete_item(item_id)
                self._load_stock_table()
                self.msg("تم", "تم حذف الصنف.")
                # Refresh autocomplete suggestions and sales tab as data might have changed
                self._setup_autocomplete()
                self._load_sales_tab()
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
        if self.tbl_stock.columnCount() > 10: # Ensure the column exists
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
            name_item.setFont(QFont(self._arabic_font.family(), 13, QFont.Bold))
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
    def _process_item_from_dialog_result(self, item_details):
        if item_details["save_to_db"]:
            # Logic to save new item to database
            name = item_details["name"]
            barcode_to_save = item_details["barcode"]
            price = item_details["price"]
            qty = item_details["qty"]

            if not name:
                self.msg("خطأ", "اسم المنتج مطلوب لحفظه في المخزون.")
                return False
            if barcode_to_save and not is_valid_barcode(barcode_to_save):
                self.msg("خطأ", "الباركود غير صالح لحفظ المنتج.")
                return False

            try:
                # Get default category (uncategorized)
                default_cat = models.get_category_by_name("غير مصنّف")
                cat_id = default_cat["id"] if default_cat else None
                
                models.add_item(name, cat_id, barcode_to_save or None, price, qty, None, purchase_price=price)
                self.msg("تم", f"تم حفظ المنتج '{name}' في قاعدة البيانات.")
                self._load_stock_table()
                self._setup_autocomplete() # Refresh autocomplete
                
                # Now add it to the bill as a regular item
                item_from_db = models.get_item_by_barcode(barcode_to_save) or models.search_items_by_name(name)[0]
                return self._add_item_to_current_bill(
                    item_from_db["id"], 
                    item_from_db["name"], 
                    item_from_db["barcode"], 
                    item_from_db["price"], # Use DB price or dialog price if manual
                    item_details["qty"], 
                    item_from_db["purchase_price"]
                )
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"تعذر حفظ المنتج:\n{e}")
                return False
        else: # Add to bill without saving to database (could be existing or custom for bill only)
            item = None
            if item_details["id"] != -1:
                # Fetch all items and find the specific one
                all_items = models.get_items()
                item = next((dict(i) for i in all_items if i['id'] == item_details["id"]), None)

            purchase_price = item["purchase_price"] if item else item_details["price"]

            return self._add_item_to_current_bill(
                item_details["id"], 
                item_details["name"], 
                item_details["barcode"], 
                item_details["price"], 
                item_details["qty"], 
                purchase_price,
                is_custom=(item_details["id"] == -1)
            )

    def _handle_scanned_barcode(self):
        barcode = self.in_barcode.text().strip()
        self.in_barcode.clear() # Clear for next scan immediately
        
        if not barcode:
            return
        
        item_row = models.get_item_by_barcode(barcode)
        item_data_dict = dict(item_row) if item_row else None # Convert to dict here

        dialog = ItemScanDialog(self, item_data=item_data_dict, currency=self.currency)
        
        # If item is new, prefill barcode in dialog if available
        if item_data_dict is None:
            dialog.in_barcode.setText(barcode)

        result = dialog.exec_()
        
        if result == ItemScanDialog.Accepted:
            item_details = dialog._return_details # Access the stored return details
            self._process_item_from_dialog_result(item_details)
        
        # Always set focus back to barcode for next scan
        self.in_barcode.setFocus()

    def _bill_find_and_add_item_dialog(self):
        """Unified method for 'بحث' and 'إضافة إلى الفاتورة' buttons."""
        barcode = self.in_barcode.text().strip()
        name = self.in_name.text().strip()

        item_row = None
        if barcode:
            item_row = models.get_item_by_barcode(barcode)
        elif name:
            items_found = models.search_items_by_name(name)
            if items_found:
                item_row = items_found[0]
        
        item_data_dict = dict(item_row) if item_row else None # Convert to dict here

        dialog = ItemScanDialog(self, item_data=item_data_dict, currency=self.currency)

        if not item_data_dict and barcode: # If barcode was entered but not found, prefill dialog's barcode
            dialog.in_barcode.setText(barcode)
        elif not item_data_dict and name: # If name was entered but not found, prefill dialog's name
            dialog.in_item_name.setText(name)
            dialog.in_item_name.setReadOnly(False) # Allow editing the name for new item
            dialog.chk_manual_price.setChecked(True) # Assume manual price for not found items
            dialog.in_price.setEnabled(True)
        elif not item_data_dict and not barcode and not name: # If all fields are empty, start with a blank new item dialog
            dialog = ItemScanDialog(self, item_data=None, currency=self.currency)


        result = dialog.exec_()
        
        if result == ItemScanDialog.Accepted:
            item_details = dialog._return_details
            self._process_item_from_dialog_result(item_details)
        
        # Clear main bill input fields and set focus after dialog interaction
        self.in_barcode.clear()
        self.in_name.clear()
        self.in_price.setValue(0.0)
        self.in_qty.setValue(1.0)
        # The chk_manual and in_price.setEnabled are controlled by the dialog, 
        # so no need to explicitly reset here unless we want to force initial state
        # self.chk_manual.setChecked(False) 
        # self.in_price.setEnabled(False)
        self.in_barcode.setFocus()


    def _on_autocomplete_selected(self, text):
        """Handle when user selects an item from autocomplete (for manual entry)"""
        # This will be used for typing in the 'in_name' field, not for barcode scans
        items_found = models.search_items_by_name(text)
        if items_found:
            item = dict(items_found[0]) # Convert to dict here
            # Fill barcode field and other main bill tab fields
            self.in_barcode.setText(item["barcode"] or "")
            self.in_price.setValue(float(item["price"]))
            self.in_qty.setValue(1.0) # Default quantity
            # If item selected from autocomplete, it's likely an existing item,
            # so disable manual price for a moment to show DB price.
            # User can still check "سعر يدوي" later.
            self.chk_manual.setChecked(False) 
            self.in_price.setEnabled(False) 
            self.in_qty.setFocus() # Move focus to quantity

    def _on_name_text_changed(self, text):
        # Auto-search when typing in name field for suggestions (only if not empty)
        # The QCompleter is handling suggestions, no need for direct search here.
        pass
        

    def _add_item_to_current_bill(self, item_id, name, barcode, price, qty, purchase_price, is_custom=False):
        """Helper to add an item to the current bill table and internal list"""
        # Check for stock before adding, even if it's an existing item from the dialog
        # For custom items, no stock check is needed.
        if not is_custom and item_id != -1:
            db_item = None
            # Fetch all items and find the specific one
            all_items = models.get_items()
            db_item = next((dict(i) for i in all_items if i['id'] == item_id), None)

            if db_item:
                available_stock = max(0, db_item["stock_count"] or 0)
                if qty > available_stock:
                    self.msg("خطأ", f"الكمية المطلوبة ({qty}) أكبر من المخزون المتاح ({available_stock}) للصنف {name}.")
                    return False # Indicate failure due to insufficient stock
            else:
                self.msg("خطأ", f"تعذر العثور على الصنف {name} في المخزون للتحقق من الكمية.")
                return False

        # Add to bill table
        row = self.tbl_bill.rowCount()
        self.tbl_bill.insertRow(row)
        
        total = price * qty
        
        self.tbl_bill.setItem(row, 0, QTableWidgetItem(barcode or ""))
        name_item = QTableWidgetItem(name)
        name_item.setFont(self.bill_name_font)
        self.tbl_bill.setItem(row, 1, name_item)
        self.tbl_bill.setItem(row, 2, QTableWidgetItem(fmt_money(price)))
        self.tbl_bill.setItem(row, 3, QTableWidgetItem(fmt_qty(qty)))
        self.tbl_bill.setItem(row, 4, QTableWidgetItem(fmt_money(total)))
        self.tbl_bill.setItem(row, 5, QTableWidgetItem(str(item_id if not is_custom else "CUSTOM")))  # Store item ID or "CUSTOM"
        
        # Add to internal tracking
        self.current_bill_items.append({
            "id": item_id,
            "name": name,
            "barcode": barcode,
            "price": price,
            "qty": qty,
            "total": total,
            "purchase_price": purchase_price, # Store purchase price for bill saving
            "is_custom": is_custom
        })
        
        self._bill_recalc_total()
        self._update_table_responsiveness() # Ensure table adjusts
        return True # Indicate success

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
        total_price = 0
        total_purchase_price = 0
        for item_data in self.current_bill_items:
            total_price += item_data["total"]
            total_purchase_price += item_data["qty"] * item_data["purchase_price"] # Calculate for bill items
        
        self.lbl_total.setText(f"الإجمالي: {fmt_money(total_price)} {self.currency}")
        # Store total purchase price temporarily if needed for printing/display before saving
        self._current_bill_total_purchase_price = total_purchase_price

    def _bill_save(self):
        if not self.current_bill_items:
            self.msg("تنبيه", "لا توجد أصناف في الفاتورة.")
            return
        try:
            total_sale_price = 0
            total_sale_purchase_price = 0
            items_to_save_details = []

            for item_data in self.current_bill_items:
                if not item_data["is_custom"]: # Only save items that are in the database
                    total_sale_price += item_data["total"]
                    total_sale_purchase_price += item_data["qty"] * item_data["purchase_price"]
                    items_to_save_details.append(item_data)
            
            if not items_to_save_details:
                self.msg("تنبيه", "لا توجد أصناف قابلة للحفظ في الفاتورة (جميعها منتجات مخصصة وغير محفوظة).")
                return

            # Create sale record
            sale_id = models.add_sale(total_sale_price, total_sale_purchase_price)
            
            # Add sale details
            for item_data in items_to_save_details:
                models.add_sale_detail(
                    sale_id, 
                    item_data["id"], 
                    item_data["qty"], 
                    item_data["price"], 
                    item_data["purchase_price"]
                )
            
            # Clear bill
            self.tbl_bill.setRowCount(0)
            self.current_bill_items.clear()
            self._bill_recalc_total()
            
            # Show success message
            self.msg("تم", f"تم حفظ الفاتورة رقم {sale_id}.")
            
            # Refresh sales tab
            self._load_sales_tab()
            # Refresh stock table as stock counts would have changed
            self._load_stock_table()
            
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"تعذر حفظ الفاتورة:\n{e}")

    def _bill_print(self):
        if not self.current_bill_items:
            self.msg("تنبيه", "لا توجد أصناف في الفاتورة للطباعة.")
            return
        
        # Create printer and dialog
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() != QPrintDialog.Accepted:
            return
        
        settings = models.get_settings()
        shop_name = settings["shop_name"] if settings else "متجري"
        contact = settings["contact"] if settings else ""
        location = settings["location"] if settings else ""

        # Create HTML content for receipt
        html = f"""
        <html>
        <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; direction: rtl; text-align: right; margin: 20px; font-size: 14px; }} /* Base font size increased */
            .header {{ text-align: center; margin-bottom: 20px; border-bottom: 1px dashed #000; padding-bottom: 10px; }}
            .shop-name {{ font-size: 28px; font-weight: bold; margin-bottom: 5px; }} /* Increased font size */
            .contact {{ font-size: 16px; margin-bottom: 2px; }} /* Increased font size */
            .receipt-info {{ margin: 15px 0; border-bottom: 1px dashed #000; padding-bottom: 10px; }}
            .info-line {{ margin-bottom: 5px; font-size: 16px; }} /* Increased font size */
            .items-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            .items-table th, .items-table td {{ border: 1px solid #000; padding: 8px; text-align: right; font-size: 14px; }} /* Increased font size */
            .items-table th {{ background-color: #f2f2f2; font-weight: bold; }}
            .total-row {{ font-weight: bold; font-size: 18px; text-align: left; padding-top: 10px; }} /* Increased font size */
            .footer {{ margin-top: 30px; text-align: center; font-size: 14px; border-top: 1px dashed #000; padding-top: 10px; }} /* Increased font size */
        </style>
        </head>
        <body>
            <div class="header">
                <div class="shop-name">{shop_name}</div>
                <div class="contact">{contact}</div>
                <div class="contact">{location}</div>
            </div>
            
            <div class="receipt-info">
                <div class="info-line">التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                <div class="info-line">رقم الفاتورة: (لم تحفظ بعد)</div>
            </div>
            
            <table class="items-table">
                <thead>
                    <tr>
                        <th>الصنف</th>
                        <th>السعر ({self.currency})</th>
                        <th>الكمية</th>
                        <th>المجموع ({self.currency})</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add items to receipt
        current_total_price = 0
        for item_data in self.current_bill_items:
            name = item_data["name"]
            price = item_data["price"]
            qty = item_data["qty"]
            total = item_data["total"]
            current_total_price += item_data["total"]
            
            html += f"""
                    <tr>
                        <td>{name}</td>
                        <td>{fmt_money(price)}</td>
                        <td>{fmt_qty(qty)}</td>
                        <td>{fmt_money(total)}</td>
                    </tr>
            """
        
        html += f"""
                </tbody>
            </table>
            
            <div class="total-row">الإجمالي: {fmt_money(current_total_price)} {self.currency}</div>
            
            <div class="footer">
                شكرًا لزيارتكم<br>
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
        - عند مسح باركود أو البحث عن منتج (باستخدام زر 'بحث' أو 'إضافة إلى الفاتورة' في تبويب الفاتورة)، ستظهر نافذة منبثقة تفاعلية.
        - في هذه النافذة، يمكنك تعديل الكمية والسعر (يدويًا أو من قاعدة البيانات).
        - إذا كان المنتج غير موجود، سيتم تقديم خيارين:
          - "إضافة إلى الفاتورة": لإضافة المنتج كصنف مخصص للفاتورة الحالية فقط.
          - "حفظ المنتج في المخزون": لإضافة المنتج إلى قاعدة البيانات ليصبح متوفرًا دائمًا، ثم يضاف إلى الفاتورة.
        """
        QMessageBox.information(self, "معلومات الماسح الضوئي", info)

    # Sales Methods
    def _load_sales_tab(self):
        sales = models.get_sales()
        self.tbl_sales.setRowCount(0)
        
        # Update Global KPIs (Revenue & Profit for all time and today)
        all_time_kpis = models.get_revenue_and_profit_all_time()
        today_kpis = models.get_revenue_and_profit_today()

        total_sales_revenue = all_time_kpis["total_revenue"]
        total_sales_profit = all_time_kpis["total_profit"]
        today_sales_revenue = today_kpis["total_revenue"]
        today_sales_profit = today_kpis["total_profit"]

        self.lbl_total_sales.setText(f"إجمالي المبيعات (إيرادات): {fmt_money(total_sales_revenue)} {self.currency}")
        self.lbl_total_profit_all_time.setText(f"إجمالي الربح الكلي: {fmt_money(total_sales_profit)} {self.currency}")
        
        self.lbl_today_sales.setText(f"مبيعات اليوم (إيرادات): {fmt_money(today_sales_revenue)} {self.currency}")
        self.lbl_today_profit.setText(f"ربح اليوم: {fmt_money(today_sales_profit)} {self.currency}")

        latest_sale = models.get_latest_sale()
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
            self.lbl_total_revenue.setText(f"إجمالي الإيرادات: 0.00 {self.currency}")
            self.lbl_total_profit.setText(f"إجمالي الربح: 0.00 {self.currency}")
            self.lbl_profit_margin.setText(f"هامش الربح: 0%")
            return
        sale_id = int(self.tbl_sales.item(row, 0).text())
        details = models.get_sale_details(sale_id)
        self.tbl_sale_details.setRowCount(0)
        
        total_revenue_for_sale = 0
        total_profit_for_sale = 0
        
        for r in details:
            row = self.tbl_sale_details.rowCount()
            self.tbl_sale_details.insertRow(row)
            self.tbl_sale_details.setItem(row, 0, QTableWidgetItem(str(r["id"])))
            self.tbl_sale_details.setItem(row, 1, QTableWidgetItem(r["item_name"]))
            self.tbl_sale_details.setItem(row, 2, QTableWidgetItem(fmt_qty(r["quantity"]))) # Quantity first
            self.tbl_sale_details.setItem(row, 3, QTableWidgetItem(fmt_money(r["price_each"]))) # Sale price
            self.tbl_sale_details.setItem(row, 4, QTableWidgetItem(fmt_money(r["subtotal"])))
            
            purchase_price_at_sale = r["purchase_price_each"] if "purchase_price_each" in r.keys() else 0
            if purchase_price_at_sale is None:
                purchase_price_at_sale = 0
            
            profit_per_item = (r["price_each"] - purchase_price_at_sale) * r["quantity"]
            
            total_revenue_for_sale += r["subtotal"]
            total_profit_for_sale += profit_per_item
            
            self.tbl_sale_details.setItem(row, 5, QTableWidgetItem(fmt_money(purchase_price_at_sale)))
            self.tbl_sale_details.setItem(row, 6, QTableWidgetItem(fmt_money(profit_per_item)))
            self.tbl_sale_details.setItem(row, 7, QTableWidgetItem(str(r["item_id"]))) # Hidden item_id
            self.tbl_sale_details.setItem(row, 8, QTableWidgetItem(str(r["sale_id"]))) # Hidden sale_id
            self.tbl_sale_details.setRowHeight(row, 35)
        
        # Update profit labels for the selected sale
        self.lbl_total_revenue.setText(f"إجمالي الإيرادات: {fmt_money(total_revenue_for_sale)} {self.currency}")
        self.lbl_total_profit.setText(f"إجمالي الربح: {fmt_money(total_profit_for_sale)} {self.currency}")
        
        profit_margin = (total_profit_for_sale / total_revenue_for_sale * 100) if total_revenue_for_sale > 0 else 0
        self.lbl_profit_margin.setText(f"هامش الربح: {fmt_money(profit_margin)}%")
        
        self._update_table_responsiveness()

    def _sales_delete_selected(self):
        row = self._selected_row(self.tbl_sales)
        if row is None:
            self.msg("تنبيه", "اختر عملية بيع للحذف.")
            return
        sale_id = int(self.tbl_sales.item(row, 0).text())
        confirm = QMessageBox.question(self, "تأكيد", "سيتم حذف عملية البيع بالكامل وستتم إعادة الأصناف إلى المخزون.\nهل أنت متأكد؟", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                models.delete_sale(sale_id)
                self._load_sales_tab()
                self.tbl_sale_details.setRowCount(0)
                self.msg("تم", "تم حذف عملية البيع.")
                # Refresh stock table as well, since items were returned
                self._load_stock_table()
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"تعذر حذف عملية البيع:\n{e}")

    def _sales_delete_item(self):
        row = self._selected_row(self.tbl_sale_details)
        if row is None:
            self.msg("تنبيه", "اختر صنفًا للحذف.")
            return
        detail_id = int(self.tbl_sale_details.item(row, 0).text())
        confirm = QMessageBox.question(self, "تأكيد", "سيتم حذف هذا الصنف من عملية البيع وستتم إعادته إلى المخزون.\nهل أنت متأكد؟", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                models.delete_sale_detail(detail_id)
                # Refresh the view of the current sale and overall sales/stock
                selected_sale_row = self._selected_row(self.tbl_sales)
                if selected_sale_row is not None:
                    self._sales_view_selected() # Refresh details
                self._load_sales_tab() # Refresh overall sales KPIs
                self._load_stock_table() # Refresh stock
                self.msg("تم", "تم حذف الصنف من عملية البيع.")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"تعذر حذف الصنف:\n{e}")

    def _sales_update_item(self):
        row = self._selected_row(self.tbl_sale_details)
        if row is None:
            self.msg("تنبيه", "اختر صنفًا للتعديل.")
            return
        detail_id = int(self.tbl_sale_details.item(row, 0).text())
        current_qty = float(self.tbl_sale_details.item(row, 2).text())
        current_price = float(self.tbl_sale_details.item(row, 3).text())
        
        # Get new values
        new_qty, ok1 = QInputDialog.getDouble(self, "تعديل الكمية", "الكمية الجديدة:", current_qty, 0.1, 1000, 2)
        new_price, ok2 = QInputDialog.getDouble(self, "تعديل السعر", f"السعر الجديد ({self.currency}):", current_price, 0.01, 100000, 2)
        
        if ok1 and ok2:
            try:
                models.update_sale_detail(detail_id, new_qty, new_price)
                # Refresh the view of the current sale and overall sales/stock
                selected_sale_row = self._selected_row(self.tbl_sales)
                if selected_sale_row is not None:
                    self._sales_view_selected() # Refresh details
                self._load_sales_tab() # Refresh overall sales KPIs
                self._load_stock_table() # Refresh stock
                self.msg("تم", "تم تعديل الصنف.")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"تعذر تعديل الصنف:\n{e}")

    # Helper methods
    def _selected_row(self, table):
        selected = table.selectedItems()
        if not selected:
            return None
        return selected[0].row()

    def msg(self, title, text):
        QMessageBox.information(self, title, text)

    @property
    def arabic_font(self):
        return self.font()

    @property
    def _bill_name_font(self):
        font = QFont(self.arabic_font.family(), 12)
        font.setBold(True)
        return font
