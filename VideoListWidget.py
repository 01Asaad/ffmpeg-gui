import PySide6
from PySide6.QtWidgets import QFileDialog, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import QSize

from VideoListItemWidget import VideoListItemWidget
from gui_utils import get_items_of_QListWidget

class VideoListWidget(QWidget) :
	def __init__(self) :
		super().__init__()
		layout = QVBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(layout)
		self.input_videos = QListWidget()
		
		self.select_video_button = QPushButton("Add video")
		self.select_video_button.clicked.connect(self.open_file_dialog)
		layout.addWidget(self.input_videos)
		layout.addWidget(self.select_video_button)
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
	@property
	def items(self) :
		return get_items_of_QListWidget(self.input_videos)
	@property
	def itemWids(self) :
		return (self.input_videos.itemWidget(vid) for vid in self.items)