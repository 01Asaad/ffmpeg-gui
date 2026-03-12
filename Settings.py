from enum import StrEnum
from typing import List

from VideoListItemWidget import Video


class Codecs(StrEnum) :
	H264 = "h264"
	H265 = "h265"

codec_names = {
	"h264" : "libx264",
	"h265" : "libx265"
}

class Settings :
	def __init__(self, codec, vids, crf, convert_to_sdr, maxrate, max_fps, res, preset = "medium") -> None:
		self.codec : Codecs = codec
		self.vids : List[Video] = vids
		self.crf = crf
		self.convert_to_sdr : bool = convert_to_sdr
		self.maxrate = maxrate
		self.max_fps = max_fps
		self.res = res
		self.preset = preset