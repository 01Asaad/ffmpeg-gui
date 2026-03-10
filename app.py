import sys

import PySide6
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QCheckBox, QComboBox, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QListView, QListWidget, QListWidgetItem, QMainWindow, QProgressBar, QPushButton, QSpinBox, QTabWidget, QVBoxLayout, QWidget, QSlider, QTextEdit

from OptionalArg import OptionalArg
from VideoListItemWidget import Video, VideoListItemWidget
from gui_utils import get_items_of_QListWidget, group_wids


class MainWindow(QMainWindow) :
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
		if file_path:
			item = QListWidgetItem()
			item.setSizeHint(QSize(200, 40))
			self.input_videos.addItem(item)
			
			widget = VideoListItemWidget(file_path)
			
			widget.delete_btn.clicked.connect(
				lambda: self.delete_video_item(item)
			)
			
			self.input_videos.setItemWidget(item, widget)
	def is_all_videos_same_aspect_ratio(self) : return False
	def set_res_input_enabled(self, val : bool) :
			self.res_width_input.setEnabled(val)
			self.res_height_input.setEnabled(val)
			self.res_keep_aspectratio_checkbox.setEnabled(val)
		
	def selected_video_updated(self) :
		current_item = self.input_videos.currentItem()
		self.text_field.setText(self.input_videos.itemWidget(current_item).video.get_description() if current_item else "No video selected")
	def maintain_aspect_ratio(self, val, controller) :
			if self.res_keep_aspectratio_checkbox.isChecked() :
				if controller == "width" :
					pass
				else :
					pass
	def start_encoding(self) :
		if not self.input_videos.count() :
			raise Exception("No videos to process")
		for item in get_items_of_QListWidget(self.input_videos) :
			vid : Video = item.video
	def __init__(self) :
		super().__init__()
		self.setWindowTitle("Video Formatter")
		self.resize(QSize(600,500))
		layout = QVBoxLayout()
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
		self.crf_slider = QSlider(Qt.Horizontal)
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

		# resLayout = QHBoxLayout()
		self.res_checkbox = QCheckBox("Change Resolution")
		self.res_keep_aspectratio_checkbox = QCheckBox("maintain aspect ratio")
		self.res_keep_aspectratio_checkbox.setChecked(True)

		self.res_width_input = QSpinBox(minimum=1, maximum=1000000)
		self.res_height_input = QSpinBox(minimum=1, maximum=1000000)
		self.res_width_input.valueChanged.connect(lambda x : self.maintain_aspect_ratio(x, "width"))
		self.res_height_input.valueChanged.connect(lambda x : self.maintain_aspect_ratio(x, "height"))
		self.set_res_input_enabled(False)
		self.res_checkbox.toggled.connect(self.set_res_input_enabled)
		settings_layout.addWidget(self.res_checkbox)
		settings_layout.addLayout(group_wids(QHBoxLayout, [self.res_width_input, self.res_height_input]))
		settings_layout.addWidget(self.res_keep_aspectratio_checkbox)

		self.progress_bar = QProgressBar()
		layout.addWidget(self.progress_bar)
		
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()