from enum import StrEnum
from typing import List

import PySide6
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QLabel, QProgressBar

from FFmpegProgressThread import FFmpegProgressThread
from Settings import Settings
from VideoListItemWidget import Video
from VideoListWidget import VideoListWidget
from utils import notify
class Codecs(StrEnum) :
	H264 = "h264"
	H265 = "h265"

codec_names = {
	"h264" : "libx264",
	"h265" : "libx265"
}


class VideoEncoder(QObject) :
	def __init__(self, progress_bar : QProgressBar, progress_label : QLabel, video_list_wid : VideoListWidget) :
		super().__init__()
		self.progress_label = progress_label
		self.video_list_wid = video_list_wid
		self.progress_bar = progress_bar
		self.ffmpeg_thread = None
	def update_progress(self, value):
		self.progress_bar.setValue(value)
	def update_video_running(self) :
		self.current_processing_video +=1
		self.progress_label.setText(f"Video : {self.current_processing_video}/{self.video_list_wid.input_videos.count()}")
		
	def on_encoding_finished(self, success, th_message):
		is_multiple = "s" if self.video_list_wid.input_videos.count() > 1 else ''
		if success:
			self.progress_bar.setValue(100)
			message = f"successfully finished {self.video_list_wid.input_videos.count()} video{is_multiple}"
		else:
			self.progress_bar.setValue(0)
			message = f"failed processing video{is_multiple}\n{th_message}"
		notify("Video formatting finished", message, 10)
	def get_command(self, settings : Settings) :
		return " ".join(((word if " " not in word else '"' + word + '"') for word in self.generate_command(Video("./input.mp4", False), settings)))
	def start_encoding(self, settings : Settings) :
		if not settings.vids :
			raise Exception("no videos to process")
		commands : list[list[str]]= []
		self.current_processing_video = 0
		for video in settings.vids :
			commands.append(self.generate_command(video, settings))
			if settings.keep_file_date :
				commands.append(["touch", "-r", str(video.path), str(self.get_destination(video, settings))])
		self.ffmpeg_thread = FFmpegProgressThread(commands)
		self.ffmpeg_thread.progress_updated.connect(self.update_progress)
		self.ffmpeg_thread.command_process_updated.connect(self.update_video_running)
		self.ffmpeg_thread.encoding_finished.connect(self.on_encoding_finished)
		
		self.progress_bar.setValue(0)
		self.progress_bar.setRange(0, 100)
		
		self.ffmpeg_thread.start()
	def cancel_encoding(self):
		if self.ffmpeg_thread and self.ffmpeg_thread.isRunning():
			self.ffmpeg_thread.stop()
			self.ffmpeg_thread.wait()
	def get_destination(self, video : Video, settings: Settings) :
		return (settings.destination if settings.destination else video.path.parent) / (video.path.name.split(".")[-2] + "_re." + video.path.name.split(".")[-1])
	def generate_command(self, video: Video, settings: Settings) -> List[str]:
		destination = self.get_destination(video, settings)
		
		filter_chain = []
		
		if settings.convert_to_sdr:
			filter_chain.append('zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p')
		
		if settings.res and all(settings.res):
			filter_chain.append(f'scale={settings.res[0]}:{settings.res[1]}')
		
		if settings.max_fps:
			filter_chain.append(f'fps={settings.max_fps}')
		
		VIDEO_FILTERS = []
		if filter_chain:
			if len(filter_chain) == 1:
				VIDEO_FILTERS = ['-vf', filter_chain[0]]
			else:
				chain = ','.join(filter_chain)
				VIDEO_FILTERS = ['-filter_complex', f'[0:v]{chain}[vout]']
		
		codec_value = codec_names[settings.codec.value]
		
		MAXRATE = ["-maxrate", settings.maxrate + settings.maxrate_unit.value, "-bufsize", settings.maxrate*2 + settings.maxrate_unit.value] if settings.maxrate else []
		
		command = [
			"ffmpeg",
			"-y",
			"-i", str(video.path),
			*VIDEO_FILTERS,
			"-map", ("[vout]" if len(filter_chain) > 1 else "0:v"),
			"-map", "0:a?",
			"-map", "0:s?",
			"-c:v", codec_value,
			"-crf", settings.crf,
			"-preset", settings.preset.value,
			*MAXRATE,
			"-c:a", "copy",
			"-c:s", "copy",
			str(destination)
		]
		
		return [str(i) for i in command]
		