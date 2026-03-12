import sys
from typing import List

import PySide6
from PySide6.QtWidgets import QApplication

from MainWindow import MainWindow



if __name__ == "__main__" :
	app = QApplication(sys.argv) 
	window = MainWindow()
	window.show()
	app.exec()