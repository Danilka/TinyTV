#!/usr/bin/python3

import subprocess, os, signal, random, time, sys
from pathlib import Path
from omxplayer.player import OMXPlayer
import RPi.GPIO as GPIO


STATIC = Path('/home/pi/Videos/static.mp4')
FOLDERS = [
	'/home/pi/Videos/looney_tunes/',
	'/home/pi/Videos/chaplin/',
	'/home/pi/Videos/shorts/',
	'/home/pi/Videos/random/',
	]
player = None
static_player = None
old_players = []
current_channel = random.randint(0, len(FOLDERS)-1)
lock = False

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Read the folder with videos.
files = []
for folder in FOLDERS:
	files.append([os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])

def grab_lock():
	global lock
	i = 0
	while lock:
		i += 1
		if i > 100000:
			lock = False
	lock = True

def release_lock():
	global lock
	lock = False

def get_file_path(channel=0):
	global FOLDERS
	global STATIC

	if random.randint(0, 20) == 7:
		return STATIC

	if channel > len(FOLDERS):
		channel = [0]
	return Path(files[channel][random.randint(0, len(files[channel])-1)])

def play_static():
	grab_lock()
	global static_player
	try:
		static_player.load(STATIC)
	except Exception:
		try:
			static_player.quit()
		except Exception:
			pass
		static_player = OMXPlayer(STATIC)
	release_lock()

def play_video():
	grab_lock()
	global player
	global current_channel
	try:
		player.stop()
	except Exception:
		pass
	player.load(get_file_path(current_channel))
	release_lock()

def start_player():
	grab_lock()
	global player
	global current_channel
	global old_players
	# play_static()
	video_file = get_file_path(current_channel)
	try:
		try:
			player.stop()
		except Exception:
			pass
		player.load(video_file)
	except Exception:
		try:
			player.quit()
		except Exception:
			pass
		if player:
			old_players.append(player)
		player = OMXPlayer(video_file)
	time.sleep(5)
	release_lock()

def exit_program():
	global player
	global old_players
	player.quit()
	for old_player in old_players:
		try:
			old_player.quit()
		except Exception:
			pass
	sys.exit()

def set_channel_0(*args, **kwargs):
	global current_channel
	current_channel = 0
	start_player()

def set_channel_1(*args, **kwargs):
	global current_channel
	current_channel = 1
	start_player()

def set_channel_2(*args, **kwargs):
	global current_channel
	current_channel = 2
	start_player()

def set_channel_3(*args, **kwargs):
	global current_channel
	current_channel = 3
	start_player()

GPIO.add_event_detect(17,GPIO.RISING,callback=set_channel_0)
GPIO.add_event_detect(22,GPIO.RISING,callback=set_channel_1)
GPIO.add_event_detect(23,GPIO.RISING,callback=set_channel_2)
GPIO.add_event_detect(27,GPIO.RISING,callback=set_channel_3)

i = 0
while True:
	i += 1

	if not lock:
		try:
			if not player.is_playing():
				play_video()
		except Exception:
			start_player()

	if i == 5:
		for old_player_i in range(len(old_players)):
			try:
				old_player[old_player_i].stop()
			except Exception:
				pass
			try:
				old_player[old_player_i].quit()
			except Exception:
				pass

	if i > 20:
		i = 0
