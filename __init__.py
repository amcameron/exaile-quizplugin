"""The purpose of this Exaile plugin is to quiz the listener on selected music.

It randomly selects and plays a short clip from each song and presents the
user with a bank of answers.  Solutions are given at the end of the quiz.

"""

from random import randrange, sample
from time import sleep

from xl import player

#TODO: select random clips from tracks,
#	create answer bank, show user answer bank after each clip, track
#	correct/incorrect responses, and show results at end of quiz.

_pl_name = 'lq2'
_clip_length = 20 # seconds
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
		self.answers = [{'artist': _artist(i), 'title': _title(i),
			'genre': _genre(i), 'year': _year(i)} for i in
			self.playlist]
		print "Loaded.  First five answers:"
		print self.answers[:5]

	def quiz(self, num_songs=None):
		"""Quiz the user on a random subset of the playlist.

		num_songs (optional): the number of songs to select. Default
			is min(5, len(playlist)).

		"""
		if num_songs is None:
			num_songs = min(len(self.playlist), 5)

		subset = sample(self.playlist, num_songs)
		clipStarts = [randrange(0, int(_length(i)) - _clip_length, 1)
			for i in subset]
		print clipStarts

		for clip in subset:
			print "playing clip!"
			player.QUEUE.play(clip)
			player.PLAYER.unpause() # without this, seek fails.
			player.PLAYER.seek(clipStarts.pop(0))
			sleep(_clip_length)
			self.exaile.player.stop()
			print "done playing clip."
			# TODO: show answer bank; prompt choices.

		# TODO: show results.
