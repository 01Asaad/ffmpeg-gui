from enum import StrEnum
from typing import List, TYPE_CHECKING
if TYPE_CHECKING :
	from MainWindow import MainWindow
from VideoListItemWidget import Video
from utils import make_even


class Codecs(StrEnum) :
	H264 = "h264"
	H265 = "h265"

codec_names = {
	"h264" : "libx264",
	"h265" : "libx265"
}

class Preset(StrEnum) :
	ULTRAFAST = "ultrafast"
	SUPERFAST = "superfast"
	VERYFAST = "veryfast"
	FASTER = "faster"
	FAST = "fast"
	MEDIUM = "medium"
	SLOW = "slow"
	SLOWER = "slower"
	VERYSLOW = "veryslow"
	PLACEBO = "placebo"


class Settings :
	def __init__(self, codec, vids, crf, convert_to_sdr, maxrate, max_fps, res, preset = Preset.MEDIUM, destination = None) -> None:
		self.codec : Codecs = codec
		self.destination = destination
		self.vids : List[Video] = vids
		self.crf = crf
		self.convert_to_sdr : bool = convert_to_sdr
		self.maxrate = maxrate
		self.max_fps = max_fps
		self.res = res
		self.preset = preset
	@classmethod
	def from_mainwindow(cls, window : MainWindow) :
		codec = Codecs(window.codec_selection.currentText())
		vids = list((itemVid.video for itemVid in window.video_list_wid.itemWids))
		crf = window.crf_input.value()
		convert_to_sdr = window.convert_to_sdr_checkbox.isChecked()
		maxrate = window.maxrate_input.text() if window.maxrate_box.checkbox_wid.isChecked() else None
		max_fps = window.maxFPS_input.text() if window.max_fps_box.checkbox_wid.isChecked() else None
		res = (make_even(window.res_widget.width), make_even(window.res_widget.height)) if window.res_widget.custom_res else (None, None)
		return Settings(codec, vids, crf,  convert_to_sdr, maxrate, max_fps, res)