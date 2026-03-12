
import json
import re
import subprocess

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton

from pathlib import Path

class Video :
	def __init__(self, path : str | Path) -> None:
		self.path = Path(path)
		self.duration =None
		self.bitrate = None
		self.video_codec = None
		self.resolution = None, None
		self.fps = None
		self.aspect_ratio = None, None
		self.size = None
		self.data = None
		self.populate()
	def get_description(self) :
		return "\n".join((str(i) for i in [
			"duration : " + str(self.duration),
			"bitrate : " + str(self.bitrate),
			"codec : " + str(self.video_codec),
			"res : " + str(self.resolution[0]) + "x" + str(self.resolution[1]),
			"fps : " + str(eval(str(self.fps))),
			"size : " + str(self.size),
			"aspect ratio : " + ":".join((str(i) for i in self.aspect_ratio)),
		]))
	def populate(self) :
		text = subprocess.check_output(["ffprobe", str(self.path), "-print_format", "json", "-show_format", "-v", "quiet", "-show_streams"], text=True)
		self.data = json.loads(text)
		self.duration = self.data["format"]["duration"]
		self.size = self.data["format"]["size"]
		self.bitrate = self.data["format"]["bit_rate"]
		vstream = next((stream for stream in self.data["streams"] if stream["codec_type"] == "video"))
		self.video_codec = vstream["codec_name"]
		self.resolution = vstream["width"], vstream["height"]
		self.aspect_ratio = vstream["display_aspect_ratio"].split(":")
		self.fps = vstream["r_frame_rate"]
		
				


class VideoListItemWidget(QWidget):
	def __init__(self, file_path, parent=None):
		super().__init__(parent)
		layout = QHBoxLayout()
		layout.setContentsMargins(5, 2, 5, 2)
		self.video = Video(file_path)
		self.label = QLabel(Path(file_path).name)
		self.label.setToolTip(file_path)
		
		# Buttons
		self.delete_btn = QPushButton("❌")
		self.delete_btn.setFixedSize(25, 25)
		
		layout.addWidget(self.label, 1)
		layout.addWidget(self.delete_btn)
		
		self.setLayout(layout)
