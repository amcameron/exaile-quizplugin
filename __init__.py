from xl import event

QUIZZER_PLUGIN = None

def enable(exaile):
	if (exaile.loading):
		event.add_callback(_enable, 'exaile_loaded')
	else:
		_enable(None, exaile, None)

def disable(exaile):
	print('It is a good day to die.')

def _enable(eventname, exaile, nothing):
	global QUIZZER_PLUGIN
	print('Battlecru- er, plugin operational!')
	QUIZZER_PLUGIN = Quizzer(exaile)



"""The purpose of this Exaile plugin is to quiz the listener on selected music.

It randomly selects and plays a short clip from each song and presents the
user with a bank of answers.  Solutions are given at the end of the quiz.

"""

from random import randrange
from xl import event
#TODO: select random clips from tracks,
#	create answer bank, show user answer bank after each clip, track
#	correct/incorrect responses, and show results at end of quiz.
_pl_name = 'lq2'
_clip_length = 20 # seconds


def _length(track):
	return track.get_tag_raw("__length")


def _artist(track):
	return track.get_tag_display("artist")


def _genre(track):
	return track.get_tag_display("genre")


def _title(track):
	return track.get_tag_display("title")


def _year(track):
	return track.get_tag_display("date")


class Quizzer(object):

	def __init__(self, exaile):
		self.exaile = exaile
		self.playlist = exaile.playlists.get_playlist(_pl_name)
		self.clipStarts = [randrange(0, int(_length(i)) - _clip_length,
			1) for i in self.playlist]
		self.answers = [{'artist': _artist(i), 'title': _title(i),
			'genre': _genre(i), 'year': _year(i)} for i in
			self.playlist]
		print "Loaded.  First five answers:"
		print self.answers[:5]
