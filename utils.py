from __future__ import annotations


import math
import subprocess

def notify(title, text, duration = 2) :
	subprocess.run(['notify-send', '-t', str(duration*1000), title, text])

def make_even(num : int) :
	if num % 2 == 0 : return num
	return num - 1 if num % 10 == 1 else num + 1

def calculate_aspect_ratio(width, height):
    gcd = math.gcd(int(width), int(height))
    
    w_ratio = int(width) // gcd
    h_ratio = int(height) // gcd
    return w_ratio, h_ratio
