import logging
import math
import sys
from typing import List

import PySide6
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QCheckBox, QComboBox, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QListView, QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QProgressBar, QPushButton, QSpinBox, QTabWidget, QVBoxLayout, QWidget, QSlider, QTextEdit

from FFmpegProgressThread import FFmpegProgressThread
from OptionalArg import OptionalArg
from Settings import Codecs, Settings
from VideoListItemWidget import VideoListItemWidget
from gui_utils import get_items_of_QListWidget, group_wids

from utils import generate_command, notify


class MainWindow(QMainWindow) :
	def __init__(self) :
		super().__init__()
		self.setWindowTitle("Video Formatter")
		self.resize(QSize(600,500))
		layout = QVBoxLayout()
		self.main_layout = layout
		body_layout = QHBoxLayout()
		self.current_processing_video = 0

		settings_layout = QVBoxLayout()
		video_data_layout = QVBoxLayout()

		layout.addLayout(body_layout)
		
		body_layout.addLayout(settings_layout)
		body_layout.addLayout(video_data_layout)
		central_widget = QWidget()
		central_widget.setLayout(layout)
		self.setCentralWidget(central_widget)

		self.codec_selection = QComboBox()
		settings_layout.addWidget(self.codec_selection)
		self.start_button = QPushButton("Start")
		self.start_button.clicked.connect(self.start_encoding)
		settings_layout.addLayout(group_wids(QHBoxLayout, [self.codec_selection, self.start_button]))
		self.codec_selection.setMaximumWidth(160)
		self.codec_selection.addItems(["h264", "h265"])
		self.input_videos = QListWidget()
		self.input_videos.currentItemChanged.connect(self.selected_video_updated)
		settings_layout.addWidget(self.input_videos)

		self.text_field = QTextEdit("No video selected")
		video_data_layout.addWidget(self.text_field)

		self.select_video_button = QPushButton("Add video")
		self.select_video_button.clicked.connect(self.open_file_dialog)
		settings_layout.addWidget(self.select_video_button)

		self.crf_label = QLabel("CRF")
		settings_layout.addWidget(self.crf_label)
		self.crf_slider = QSlider(Qt.Orientation.Horizontal)
		self.crf_slider.setRange(0, 100)
		self.crf_input = QSpinBox(maximum=100, singleStep=1, minimum=0)
		self.crf_input.valueChanged.connect(lambda x : self.crf_slider.setValue(x))
		self.crf_slider.valueChanged.connect(lambda x : self.crf_input.setValue(x))
		
		settings_layout.addLayout(group_wids(QHBoxLayout, [self.crf_slider, self.crf_input]))

		self.convert_to_sdr_checkbox = QCheckBox("Convert to SDR")
		settings_layout.addWidget(self.convert_to_sdr_checkbox)

		self.maxrate_input = QLineEdit(inputMask=None)
		self.maxrate_box = OptionalArg("maxrate", [self.maxrate_input])
		settings_layout.addWidget(self.maxrate_box)

		self.maxFPS_input = QLineEdit(inputMask=None)
		self.max_fps_box = OptionalArg("Max FPS", [self.maxFPS_input])
		settings_layout.addWidget(self.max_fps_box)

		self.res_checkbox = QCheckBox("Change Resolution")
		self.res_keep_aspectratio_checkbox = QCheckBox("maintain aspect ratio")
		self.res_keep_aspectratio_checkbox.setChecked(True)
		self.res_keep_aspectratio_checkbox.checkStateChanged.connect(self.res_aspect_ratio_clicked)

		self.res_width_input = QSpinBox(minimum=1, maximum=1000000)
		self.res_height_input = QSpinBox(minimum=1, maximum=1000000)
		self.res_width_input.valueChanged.connect(self.maintain_aspect_ratio)
		self.res_height_input.valueChanged.connect(self.maintain_aspect_ratio)
		self.set_res_input_enabled(False)
		self.res_checkbox.toggled.connect(self.set_res_input_enabled)
		settings_layout.addWidget(self.res_checkbox)
		settings_layout.addLayout(group_wids(QHBoxLayout, [self.res_width_input, self.res_height_input]))
		settings_layout.addWidget(self.res_keep_aspectratio_checkbox)

		self.progress_label = QLabel("Idle")
		layout.addWidget(self.progress_label)
		self.progress_bar = QProgressBar()
		self.input_videos.itemChanged
		layout.addWidget(self.progress_bar)
	def get_settings(self) :
		codec = Codecs(self.codec_selection.currentText())
		vids = [self.input_videos.itemWidget(vid).video for vid in get_items_of_QListWidget(self.input_videos)]
		crf = self.crf_input.value()
		convert_to_sdr = self.convert_to_sdr_checkbox.isChecked()
		maxrate = self.maxrate_input.text() if self.maxrate_box.checkbox_wid.isChecked() else None
		max_fps = self.maxFPS_input.text() if self.max_fps_box.checkbox_wid.isChecked() else None
		res = (self.res_width_input.value(), self.res_height_input.value()) if self.res_checkbox.isChecked() else (None, None)
		return Settings(codec, vids, crf,  convert_to_sdr, maxrate, max_fps, res)

	def delete_video_item(self, item):
		row = self.input_videos.row(item)
		self.input_videos.takeItem(row)
	def open_file_dialog(self):
		file_dialog = QFileDialog(self)
		file_path, _ = file_dialog.getOpenFileName(
			self,
			"Select Video File",
			"",
			"Video Files (*.mp4 *.avi *.mkv *.mov)"
		)
		if file_path :
			item = QListWidgetItem()
			item.setSizeHint(QSize(200, 40))
			self.input_videos.addItem(item)
			
			widget = VideoListItemWidget(file_path)
			
			widget.delete_btn.clicked.connect(
				lambda: self.delete_video_item(item)
			)
			
			self.input_videos.setItemWidget(item, widget)
	def is_all_videos_same_aspect_ratio(self) :
		if self.input_videos.count() == 0 : return True
		start_aspect_ratio = self.input_videos.itemWidget(self.input_videos.item(0)).video.aspect_ratio
		return all(self.input_videos.itemWidget(vidwid).video.aspect_ratio == start_aspect_ratio for vidwid in get_items_of_QListWidget(self.input_videos))
	def set_res_input_enabled(self, val : bool) :
			self.res_width_input.setEnabled(val)
			self.res_height_input.setEnabled(val)
			self.res_keep_aspectratio_checkbox.setEnabled(val)

	def selected_video_updated(self) :
		current_item = self.input_videos.currentItem()
		self.text_field.setText(self.input_videos.itemWidget(current_item).video.get_description() if current_item else "No video selected")
	def maintain_aspect_ratio(self, controller : QSpinBox | None = None) :
			assert any(controller is i for i in (self.res_height_input, self.res_width_input))

			if self.input_videos.count() == 0 : return

			if self.res_keep_aspectratio_checkbox.isChecked() and self.is_all_videos_same_aspect_ratio() :
				aspect_ratio = [int(i) for i in self.input_videos.itemWidget(self.input_videos.item(0)).video.aspect_ratio]
				controller = controller or (self.res_height_input if self.res_height_input.hasFocus() else self.res_width_input)
				val = controller.value()
				if controller is self.res_width_input :
					corresponding_val = val * (aspect_ratio[1] / aspect_ratio[0])
					set_to = self.res_height_input
				else :
					corresponding_val = val * (aspect_ratio[0] / aspect_ratio[1])
					set_to = self.res_width_input
				logging.debug(controller, aspect_ratio, val, corresponding_val)
				set_to.setValue(math.ceil(corresponding_val))
	def start_encoding(self) :
		settings = self.get_settings()
		if not settings.vids :
			raise Exception("no videos to process")
		commands = []
		self.current_processing_video = 0
		for video in settings.vids :
			commands.append(generate_command(video, settings))
		self.ffmpeg_thread = FFmpegProgressThread(commands)
		self.ffmpeg_thread.progress_updated.connect(self.update_progress)
		self.ffmpeg_thread.command_process_updated.connect(self.update_video_running)
		self.ffmpeg_thread.encoding_finished.connect(self.on_encoding_finished)
		
		self.progress_bar.setValue(0)
		self.progress_bar.setRange(0, 100)
		
		self.ffmpeg_thread.start()
	def update_progress(self, value):
		self.progress_bar.setValue(value)
	def update_video_running(self) :
		self.current_processing_video +=1
		self.progress_label.setText(f"Video : {self.current_processing_video}/{self.input_videos.count()}")
		
	def on_encoding_finished(self, success, th_message):
		is_multiple = "s" if self.input_videos.count() > 1 else ''
		if success:
			self.progress_bar.setValue(100)
			message = f"successfully finished {self.input_videos.count()} video{is_multiple}"
		else:
			self.progress_bar.setValue(0)
			message = f"failed processing video{is_multiple}\n{th_message}"
		notify("Video formatting finished", message, 10)
	def cancel_encoding(self):
		if self.ffmpeg_thread and self.ffmpeg_thread.isRunning():
			self.ffmpeg_thread.stop()
			self.ffmpeg_thread.wait()
	def input_videos_changed(self) :
		if not self.is_all_videos_same_aspect_ratio() :
			self.res_keep_aspectratio_checkbox.setChecked(False)
	def res_aspect_ratio_clicked(self, val : Qt.CheckState) :
		if val == Qt.CheckState.Checked :
			if not self.is_all_videos_same_aspect_ratio() :
				QMessageBox.warning(
					None, 
					"Error",
					"Can't maintain aspect ratio when videos with varying aspect ratio are selected"
				)
			else :
				self.maintain_aspect_ratio(self.res_width_input)
app = QApplication(sys.argv) 
window = MainWindow()
window.show()
app.exec()