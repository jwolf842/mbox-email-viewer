import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from ui.main_window import MainWindow

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("MBOX Email Viewer")
    app.setOrganizationName("YourOrganization")
    
    # Set application icon if exists
    icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()