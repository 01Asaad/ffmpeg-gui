from __future__ import annotations


import subprocess

def notify(title, text, duration = 2) :
	subprocess.run(['notify-send', '-t', str(duration*1000), title, text])

def make_even(num : int) :
	if num % 2 == 0 : return num
	return num - 1 if num % 10 in (6, 1) else num + 1