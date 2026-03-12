from traceback import format_exc

from PySide6.QtCore import QThread, Signal

import subprocess, re

class FFmpegProgressThread(QThread):
	progress_updated = Signal(int)
	command_process_updated = Signal(int)
	encoding_finished = Signal(bool, str)
	
	def __init__(self, commands, total_duration=None):
		super().__init__()
		self.commands = commands
		self.total_duration = total_duration
		self.process = None
		
	def run(self):
		try:
			for i, command in enumerate(self.commands) :
				print("executing\n", " ".join(command))
				self.command_process_updated.emit(i)
				self.process = subprocess.Popen(
					command,
					stderr=subprocess.PIPE,
					stdout=subprocess.PIPE,
					universal_newlines=True,
					bufsize=1
				)
				
				duration = None
				time_pattern = re.compile(r'time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})')
				duration_pattern = re.compile(r'Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})')
				
				while True:
					line = self.process.stderr.readline()
					if not line and self.process.poll() is not None:
						break
						
					if duration is None:
						duration_match = duration_pattern.search(line)
						if duration_match:
							h, m, s, ms = map(int, duration_match.groups())
							duration = h * 3600 + m * 60 + s + ms/100
							self.total_duration = duration
					
					time_match = time_pattern.search(line)
					if time_match and self.total_duration:
						h, m, s, ms = map(int, time_match.groups())
						current_time = h * 3600 + m * 60 + s + ms/100
						progress = int((current_time / self.total_duration) * 100)
						progress = min(progress, 100)  # Cap at 100%
						self.progress_updated.emit(progress)
						
				return_code = self.process.wait()
				print("finished command")
				
			
			if return_code == 0:
				self.progress_updated.emit(100)
				self.encoding_finished.emit(True, "Encoding completed successfully")
			else:
				self.encoding_finished.emit(False, f"Encoding failed with code {return_code}")
				
		except Exception as e:
			self.encoding_finished.emit(False, str(e))
			print(format_exc())
	
	def stop(self):
		if self.process:
			self.process.terminate()
			self.process.wait()