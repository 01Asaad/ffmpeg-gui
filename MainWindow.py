import logging
from pathlib import Path
from typing import List

import PySide6
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QHBoxLayout, QLabel, QLineEdit,
							   QMainWindow, QProgressBar, QPushButton, QSpinBox,
							   QVBoxLayout, QWidget, QSlider, QTextEdit)

from OptionalArg import OptionalArg
from Resolution_Widget import Resolution_Widget
from Settings import Settings
import VideoEncoder
from VideoListWidget import VideoListWidget
from gui_utils import group_wids

class MainWindow(QMainWindow) :
	def __init__(self) :
		super().__init__()
		self.setWindowTitle("Video Formatter")
		self.resize(QSize(1280,720))
		self.current_processing_video = 0
		self.setup_ui()
		self.video_encoder = VideoEncoder.VideoEncoder(self.progress_bar, self.progress_label, self.video_list_wid)
		self.command_preview_field.setText(self.video_encoder.get_command(Settings.from_mainwindow(self)))
	def setup_ui(self) :
		layout = QVBoxLayout()
		self.main_layout = layout
		body_layout = QHBoxLayout()

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
		self.start_button.clicked.connect(lambda : self.video_encoder.start_encoding(Settings.from_mainwindow(self)))
		settings_layout.addLayout(group_wids(QHBoxLayout, [self.codec_selection, self.start_button]))
		self.codec_selection.setMaximumWidth(160)
		self.codec_selection.addItems(["h264", "h265"])
		self.codec_selection.currentIndexChanged.connect(self.settings_updated)
		self.video_list_wid = VideoListWidget()
		self.video_list_wid.input_videos.currentItemChanged.connect(self.selected_video_updated)
		settings_layout.addWidget(self.video_list_wid)

		self.text_field = QTextEdit("No video selected")
		self.text_field.setReadOnly(True)
		self.command_preview_field = QTextEdit()
		self.command_preview_field.setReadOnly(True)
		
		video_data_layout.addWidget(self.text_field)
		video_data_layout.addWidget(self.command_preview_field)

		self.crf_label = QLabel("CRF")
		settings_layout.addWidget(self.crf_label)
		self.crf_slider = QSlider(Qt.Orientation.Horizontal)
		self.crf_slider.setRange(0, 51)
		self.crf_input = QSpinBox(maximum=51, singleStep=1, minimum=0)
		self.crf_input.valueChanged.connect(lambda x : self.crf_slider.setValue(x))
		self.crf_slider.valueChanged.connect(lambda x : self.crf_input.setValue(x))

		self.crf_input.setValue(19)

		self.crf_slider.valueChanged.connect(self.settings_updated)
		
		settings_layout.addLayout(group_wids(QHBoxLayout, [self.crf_slider, self.crf_input]))

		self.convert_to_sdr_checkbox = QCheckBox("Convert to SDR")
		self.convert_to_sdr_checkbox.checkStateChanged.connect(self.settings_updated)
		settings_layout.addWidget(self.convert_to_sdr_checkbox)

		self.maxrate_input = QLineEdit(inputMask=None)
		self.maxrate_input.textChanged.connect(self.settings_updated)
		self.maxrate_box = OptionalArg("maxrate", [self.maxrate_input])
		settings_layout.addWidget(self.maxrate_box)

		self.maxFPS_input = QLineEdit(inputMask=None)
		self.maxFPS_input.textChanged.connect(self.settings_updated)
		self.max_fps_box = OptionalArg("Max FPS", [self.maxFPS_input])
		self.max_fps_box.checkbox_wid.clicked.connect(self.settings_updated)
		settings_layout.addWidget(self.max_fps_box)
		
		# self.custom_output_dir = QCheckBox("Custom Output dir")
		self.output_dir = QLineEdit(placeholderText="same as each video's path")
		self.output_dir.textChanged.connect(self.settings_updated)
		self.select_dir_button = QPushButton("select dir")
		self.select_dir_button.clicked.connect(self.open_directory_dialog)
		self.custom_output_dir = OptionalArg("Custom Output dir", [self.output_dir, self.select_dir_button])
		settings_layout.addWidget(self.custom_output_dir)

		self.res_widget = Resolution_Widget(self)
		settings_layout.addWidget(self.res_widget)

		self.keep_file_data_checkbox = QCheckBox("Keep video file modify and create date")
		settings_layout.addWidget(self.keep_file_data_checkbox)
		self.progress_label = QLabel("Idle")
		layout.addWidget(self.progress_label)
		self.progress_bar = QProgressBar()
		layout.addWidget(self.progress_bar)
	def open_directory_dialog(self):
		file_dialog = QFileDialog(self)
		directory_path = file_dialog.getExistingDirectory(
			self, "Select Directory", "", QFileDialog.DontResolveSymlinks
		)
		directory_path = Path(directory_path)
		self.output_dir.setText(str(directory_path))
		return directory_path
		
	@property
	def is_all_videos_same_aspect_ratio(self) :
		if self.video_list_wid.input_videos.count() == 0 : return True
		start_aspect_ratio = next(self.video_list_wid.itemWids).video.aspect_ratio
		return all(vidwid.video.aspect_ratio == start_aspect_ratio for vidwid in self.video_list_wid.itemWids)
	def settings_updated(self) :
		self.command_preview_field.setText(self.video_encoder.get_command(Settings.from_mainwindow(self)))
	def selected_video_updated(self) :
		current_item = self.video_list_wid.input_videos.currentItem()
		self.text_field.setText(self.video_list_wid.input_videos.itemWidget(current_item).video.get_description() if current_item else "No video selected")
	def input_videos_changed(self) :
		if not self.is_all_videos_same_aspect_ratio :
			self.res_widget.res_keep_aspectratio_checkbox.setChecked(False)
	