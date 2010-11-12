"""The purpose of this Exaile plugin is to quiz the listener on selected music.

It randomly selects and plays a short clip from each song and presents the
user with a bank of answers.  Solutions are given at the end of the quiz.

"""
# TODO: Make the interface file work without specifying an absolute path.

from random import randrange, sample
from time import sleep
from logging import getLogger
from threading import Thread

from xl import player
from xl.event import add_callback
from gtk import Builder, Window, Notebook, Adjustment, HBox
from gtk import combo_box_new_text, TextBuffer

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
	QUIZZER_PLUGIN.window.destroy()
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
		b = Builder()
		b.add_from_file(
			'/home/andrew/.local/share/exaile/plugins/jazzquiz/jazzquiz.glade')
		self.window = b.get_object('QuizWindow')

		# Prepare quiz to run in a separate thread.
		self.thread = Thread(target=self.quiz)

		# When closed, don't prompt the user, just close the window.
		self.window.connect("delete_event", lambda x,y: False)
		self.window.connect_object("destroy", Window.destroy,
			self.window)

		# Connect buttons to move through the notebook.
		self.start_button = b.get_object('start_button')
		self.submit_button = b.get_object('submit_button')
		self.restart_button = b.get_object('restart_button')
		self.notebook = b.get_object('notebook1')
		self.start_button.connect_object("clicked", Quizzer.quiz, self)
		self.submit_button.connect_object("clicked", Quizzer.finish, self)
		self.restart_button.connect_object("clicked", Notebook.set_current_page,
				self.notebook, 0)

		# Connect spinner to self.num_songs
		temp = Adjustment(value=_def_num_songs, lower=1,
				upper=len(self.playlist), step_incr=1)
		self.num_songs_spinner = b.get_object('num_songs_spinner')
		temp.connect("value_changed", self.change_num_songs,
				self.num_songs_spinner)
		self.num_songs_spinner.set_adjustment(temp)

		self.quiz_vbox = b.get_object('quiz_vbox')
		self.results_textview = b.get_object('results_textview')

		# Done! Show the window!
		self.window.show()

		log.debug("Quizzer plugin loaded.")

	def change_num_songs(self, widget, spinner):
		self.num_songs = self.num_songs_spinner.get_value_as_int()

	def quiz(self, widget=None):
		"""Quiz the user on a random subset of the playlist."""
		subset = sample(self.playlist, self.num_songs)
		clipStarts = [randrange(0, int(_length(i)) - _clip_length, 1)
			for i in subset]
		log.debug("Clip starts: %s" % clipStarts)
		self.answers = [{'artist': _artist(i), 'title': _title(i),
			'genre': _genre(i), 'year': _year(i)} for i in subset]
		artist_pool = set(_artist(i) for i in subset)
		title_pool = set(_title(i) for i in subset)
		date_pool = set(_year(i) for i in subset)
		genre_pool = set(_genre(i) for i in subset)
		self.responses = []

		# Set up quiz_vbox. Remove old children if they're lying around.
		for child in self.quiz_vbox.get_children():
			self.quiz_vbox.remove(child)
		for i in xrange(self.num_songs):
			widget = HBox();
			artist_cb = combo_box_new_text()
			for artist in artist_pool:
				artist_cb.append_text(artist)
			title_cb = combo_box_new_text()
			for title in title_pool:
				title_cb.append_text(title)
			date_cb = combo_box_new_text()
			for date in date_pool:
				date_cb.append_text(date)
			genre_cb = combo_box_new_text()
			for genre in genre_pool:
				genre_cb.append_text(genre)
			widget.pack_start(artist_cb)
			widget.pack_start(title_cb)
			widget.pack_start(date_cb)
			widget.pack_start(genre_cb)
			self.quiz_vbox.pack_start(widget)

		self.quiz_vbox.show_all()
		self.notebook.next_page()
		# Look into doing follow-up code (running the quiz) with a callback
		# registered to the notebook's "switch-page" signal.

		for clip in subset:
			log.info("playing clip!")
			player.QUEUE.play(clip)
			player.PLAYER.unpause() # without this, seek fails.
			player.PLAYER.seek(clipStarts.pop(0))
			sleep(_clip_length)
			self.exaile.player.stop()
			log.info("done playing clip.")

	def finish(self, widget=None):
		self.results = ""
		for i in xrange(self.num_songs):
			current_hbox = self.quiz_vbox.get_children()[i]
			a = current_hbox.get_children()[0].get_active_text()
			t = current_hbox.get_children()[1].get_active_text()
			y = current_hbox.get_children()[2].get_active_text()
			g = current_hbox.get_children()[3].get_active_text()
			this_response = {'artist':a, 'title':t, 'genre':g, 'year':y}
			self.results += "Correct answer:\n"
			self.results += str(self.answers[i]) + "\n"
			self.results += "Your answer:\n"
			self.results += str(this_response) + "\n"
		log.info("results:\n" + self.results)

		result_buf = TextBuffer()
		result_buf.set_text(self.results)
		self.results_textview.set_buffer(result_buf)

		self.notebook.next_page()
