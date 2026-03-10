from typing import List

from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox
class OptionalArg(QWidget) :
    def __init__(self, checkbox_label : str, input_wids : List[QWidget], default_enabled = False, contentLayout = QVBoxLayout) :
        super().__init__()
        layout = contentLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.checkbox_label = checkbox_label
        self.input_wids = input_wids
        self.default_enabled = default_enabled
        self.checkbox_wid = QCheckBox(checkbox_label)
        self.checkbox_wid.setChecked(default_enabled)
        layout.addWidget(self.checkbox_wid)
        for wid in self.input_wids :
            wid.setEnabled(default_enabled)
            self.checkbox_wid.toggled.connect(wid.setEnabled)
            layout.addWidget(wid)
        self.setLayout(layout)