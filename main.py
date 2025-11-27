from frontend.dashboard import dashboard
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = dashboard()
    dashboard.show()
    sys.exit(app.exec_())
