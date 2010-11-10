"""The purpose of this Exaile plugin is to quiz the listener on selected music.

It randomly selects and plays a short clip from each song and presents the
user with a bank of answers.  Solutions are given at the end of the quiz.

"""

from random import randrange, sample
from time import sleep
from logging import getLogger

from xl import player

#TODO: select random clips from tracks,
#	create answer bank, show user answer bank after each clip, track
#	correct/incorrect responses, and show results at end of quiz.

log = getLogger(__name__)
_pl_name = 'lq2'
_clip_length = 20 # seconds
QUIZZER_PLUGIN = None


def enable(exaile):
	if (exaile.loading):
		event.add_callback(_enable, 'exaile_loaded')
	else:
		_enable(None, exaile, None)


def disable(exaile):
	log.info('It is a good day to die.')


def _enable(eventname, exaile, nothing):
	global QUIZZER_PLUGIN
	log.info('Battlecru- er, plugin operational!')
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
		log.debug("Quizzer plugin loaded.")

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
		log.debug("Clip starts: %s" % clipStarts)
		self.answers = [{'artist': _artist(i), 'title': _title(i),
			'genre': _genre(i), 'year': _year(i)} for i in subset]
		self.responses = []

		for clip in subset:
			log.info("playing clip!")
			player.QUEUE.play(clip)
			player.PLAYER.unpause() # without this, seek fails.
			player.PLAYER.seek(clipStarts.pop(0))
			sleep(_clip_length)
			self.exaile.player.stop()
			log.info("done playing clip.")
			print "Artists:"
			for i, ans in zip(range(1, num_songs+1), self.answers):
				print "{0}. {1}".format(i, ans['artist'])
			a = raw_input("Choose an artist: ")
			a = self.answers[int(a)-1]['artist']
			print "Titles:"
			for i, ans in zip(range(1, num_songs+1), self.answers):
				print "{0}. {1}".format(i, ans['title'])
			t = raw_input("Choose a title: ")
			t = self.answers[int(t)-1]['title']
			print "Genres:"
			for i, ans in zip(range(1, num_songs+1), self.answers):
				print "{0}. {1}".format(i, ans['genre'])
			g = raw_input("Choose a genre: ")
			g = self.answers[int(g)-1]['genre']
			print "Years:"
			for i, ans in zip(range(1, num_songs+1), self.answers):
				print "{0}. {1}".format(i, ans['year'])
			y = raw_input("Choose a year: ")
			y = self.answers[int(y)-1]['year']
			self.responses.append({'artist':a, 'title':t,
				'genre':g, 'year':y})
			# TODO: show answer bank; prompt choices.

		for i in xrange(num_songs):
			print "Correct answer:"
			print self.answers[i]
			print "Your answer:"
			print self.responses[i]
		# TODO: show results.
