"""The purpose of this Exaile plugin is to quiz the listener on selected music.

It randomly selects and plays a short clip from each song and presents the
user with a bank of answers.  Solutions are given at the end of the quiz.

"""

from random import randrange, sample
from time import sleep
from logging import getLogger
from threading import Thread

from xl import player
from xl.event import add_callback
from gtk import Button, Window, main_quit

#TODO: select random clips from tracks,
#	create answer bank, show user answer bank after each clip, track
#	correct/incorrect responses, and show results at end of quiz.

log = getLogger(__name__)
_pl_name = 'lq2'
_clip_length = 5 # seconds
_def_num_songs = 3
QUIZZER_PLUGIN = None


def enable(exaile):
	if (exaile.loading):
		add_callback(_enable, 'exaile_loaded')
	else:
		_enable(None, exaile, None)


def disable(exaile):
	global QUIZZER_PLUGIN
	log.info('It is a good day to die.')
	QUIZZER_PLUGIN = None


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
		self.num_songs = min(_def_num_songs, len(self.playlist))
		self.window = Window()

		# Prepare quiz to run in a separate thread.
		self.thread = Thread(target=self.quiz)

		# When closed, don't prompt the user, just close the window.
		self.window.connect("delete_event", lambda x,y: False)
		self.window.connect_object("destroy", Window.destroy,
			self.window)

		# Create a button to start the quiz.
		self.button = Button("Start quiz!")
		self.button.connect_object("clicked", Thread.run, self.thread)

		self.window.add(self.button)
		self.button.show()
		self.window.show()

		log.debug("Quizzer plugin loaded.")

	def quiz(self, widget=None):
		"""Quiz the user on a random subset of the playlist."""
		subset = sample(self.playlist, self.num_songs)
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
			for i, ans in zip(range(1, self.num_songs+1), self.answers):
				print "{0}. {1}".format(i, ans['artist'])
			a = raw_input("Choose an artist: ")
			a = self.answers[int(a)-1]['artist']
			print "Titles:"
			for i, ans in zip(range(1, self.num_songs+1), self.answers):
				print "{0}. {1}".format(i, ans['title'])
			t = raw_input("Choose a title: ")
			t = self.answers[int(t)-1]['title']
			print "Genres:"
			for i, ans in zip(range(1, self.num_songs+1), self.answers):
				print "{0}. {1}".format(i, ans['genre'])
			g = raw_input("Choose a genre: ")
			g = self.answers[int(g)-1]['genre']
			print "Years:"
			for i, ans in zip(range(1, self.num_songs+1), self.answers):
				print "{0}. {1}".format(i, ans['year'])
			y = raw_input("Choose a year: ")
			y = self.answers[int(y)-1]['year']
			self.responses.append({'artist':a, 'title':t,
				'genre':g, 'year':y})
			# TODO: show answer bank; prompt choices.

		for i in xrange(self.num_songs):
			print "Correct answer:"
			print self.answers[i]
			print "Your answer:"
			print self.responses[i]
		# TODO: show results.
