import logging
import math
from typing import TYPE_CHECKING

import PySide6
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QMessageBox, QSpinBox, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

from utils import make_even
if TYPE_CHECKING :
	from MainWindow import MainWindow
from gui_utils import group_wids

class Resolution_Widget(QWidget) :
	def __init__(self, mainwindow : MainWindow) :
		super().__init__()
		self.mainwindow = mainwindow
		layout = QVBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(layout)
		self.res_checkbox = QCheckBox("Change Resolution")
		self.res_keep_aspectratio_checkbox = QCheckBox("maintain aspect ratio")
		self.res_keep_aspectratio_checkbox.setChecked(True)
		self.res_keep_aspectratio_checkbox.checkStateChanged.connect(self.res_aspect_ratio_clicked)

		self.res_width_input = QSpinBox(minimum=1, maximum=1000000)
		self.res_height_input = QSpinBox(minimum=1, maximum=1000000)
		self.res_width_input.valueChanged.connect(lambda x: self.maintain_aspect_ratio(None))
		self.res_height_input.valueChanged.connect(lambda x: self.maintain_aspect_ratio(None))
		self.set_res_input_enabled(False)
		self.res_checkbox.toggled.connect(self.set_res_input_enabled)
		layout.addWidget(self.res_checkbox)
		layout.addLayout(group_wids(QHBoxLayout, [self.res_width_input, self.res_height_input]))
		layout.addWidget(self.res_keep_aspectratio_checkbox)
	@property
	def width(self) :
		return self.res_width_input.value()
	@property
	def height(self) :
		return self.res_height_input.value()
	@property
	def res(self) :
		return self.width, self.height
	@property
	def custom_res(self) :
		return self.res_checkbox.isChecked()
	
	def set_res_input_enabled(self, val : bool) :
			self.res_width_input.setEnabled(val)
			self.res_height_input.setEnabled(val)
			self.res_keep_aspectratio_checkbox.setEnabled(val)
	def maintain_aspect_ratio(self, controller : QSpinBox | None = None) :

			if self.mainwindow.video_list_wid.input_videos.count() == 0 : return

			if self.res_keep_aspectratio_checkbox.isChecked() and self.mainwindow.is_all_videos_same_aspect_ratio :
				aspect_ratio = [int(i) for i in next(self.mainwindow.video_list_wid.itemWids).video.aspect_ratio]
				controller = controller or (self.res_height_input if self.res_height_input.hasFocus() else self.res_width_input)
				val = make_even(controller.value())
				if controller is self.res_width_input :
					corresponding_val = val * (aspect_ratio[1] / aspect_ratio[0])
					set_to = self.res_height_input
				else :
					corresponding_val = val * (aspect_ratio[0] / aspect_ratio[1])
					set_to = self.res_width_input
				logging.debug(controller, aspect_ratio, val, corresponding_val)
				set_to.setValue(math.ceil(corresponding_val))
	def res_aspect_ratio_clicked(self, val : Qt.CheckState) :
		if val == Qt.CheckState.Checked :
			if self.mainwindow.is_all_videos_same_aspect_ratio :
				self.maintain_aspect_ratio(self.res_width_input)
			else :
				QMessageBox.warning(
					None, 
					"Error",
					"Can't maintain aspect ratio when videos with varying aspect ratio are selected"
				)