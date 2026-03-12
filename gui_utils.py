from typing import List, Type
from PySide6.QtWidgets import QListWidget, QWidget, QBoxLayout

def group_wids(layout : Type[QBoxLayout], wids : List[QWidget]) :
	lay = layout()
	for wid in wids :
		lay.addWidget(wid)
	return lay
def get_items_of_QListWidget(wid : QListWidget) :
	return (wid.item(i) for i in range(wid.count()))