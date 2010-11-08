from xl import event

def enable(exaile):
	if (exaile.loading):
		event.add_callback(_enable, 'exaile_loaded')
	else:
		_enable(None, exaile, None)

def disable(exaile):
	print('It is a good day to die.')

def _enable(eventname, exaile, nothing):
	print('Battlecru- er, plugin operational!')
