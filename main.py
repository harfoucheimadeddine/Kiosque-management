import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import setup_database
from controllers import Controller
from qss import APP_QSS

def setup_application():
    """Setup application with enhanced configuration"""
    app = QApplication(sys.argv)
    
    # Application metadata
    app.setApplicationName("Store Manager (Arabic)")
    app.setApplicationDisplayName("نظام إدارة المتجر")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Store Management Solutions")
    
    # FIXED: Move high DPI scaling setup BEFORE QApplication creation
    # This should be done before creating QApplication, but since we already created it,
    # we'll set the attributes that can still be set
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Enhanced Arabic font support
    from PyQt5.QtGui import QFontDatabase
    
    # Try to load system Arabic fonts
    arabic_fonts = [
        "Tahoma",           # Good Arabic support
        "Arial Unicode MS", # Comprehensive Unicode support
        "Segoe UI",         # Windows default with Arabic
        "DejaVu Sans",      # Linux Arabic support
        "Noto Sans Arabic", # Google Noto Arabic
        "Arial"             # Fallback
    ]
    
    font_db = QFontDatabase()
    available_fonts = font_db.families()
    
    selected_font = None
    for font_name in arabic_fonts:
        if font_name in available_fonts:
            selected_font = QFont(font_name, 11)
            selected_font.setStyleHint(QFont.System)
            break
    
    if not selected_font:
        selected_font = QFont("Arial", 11)
    
    app.setFont(selected_font)
    
    # Apply modern dark theme stylesheet
    app.setStyleSheet(APP_QSS)
    
    return app

def create_required_directories():
    """Create necessary directories for the application"""
    directories = [
        "assets",
        "assets/logo", 
        "assets/photos"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    """Main application entry point"""
    # FIXED: Set high DPI scaling BEFORE creating QApplication
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Setup database
    setup_database()
    
    # Create required directories
    create_required_directories()
    
    # Setup and configure application
    app = setup_application()
    
    # Create and show main window
    window = Controller()
    window.show()
    
    # Center window on screen
    screen = app.primaryScreen().geometry()
    window_size = window.geometry()
    x = (screen.width() - window_size.width()) // 2
    y = (screen.height() - window_size.height()) // 2
    window.move(x, y)
    
    # Start application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()