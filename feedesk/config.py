"""

"""

__licence__ = """Copyright (C) 2011  Yanglei Zhao. All right reserved.
http://www4.ncsu.edu/~yzhao11/
z12y12l12@gmail.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = 'Yanglei Zhao <z12y12l12 [AT] gmail [DOT] com>'

import ConfigParser

DEFAULT_CONFIG = {'screen_width': 1024, 'screen_height': 768,
		'interval_feed': 240, 'interval_wallpaper': 10, 'type': 'random'}

DEFAULT_FEEDS = {'wallpaper': 'http://api.flickr.com/services/feeds/groups_pool.gne?id=19604169@N00&lang=en-us&format=rss_200'}

class Config():
	def __init__(self, file, default_section='feedesk'):
		self.default_section = default_section
		self.file = file

		self.config = ConfigParser.RawConfigParser()
		self.load()

	def get(self, key, section=None):
		if section == None:
			section = self.default_section
		return self.config.get(section, key)
	
	def getint(self, key, section=None):
		if section == None:
			section = self.default_section
		return self.config.getint(section, key)
	
	def getbool(self, key, section=None):
		if section == None:
			section = self.default_section
		return self.config.getboolean(section, key)
		
	def getfloat(self, key, section=None):
		if section == None:
			section = self.default_section
		return self.config.getfloat(section, key)

	def getfeedlist(self):
		return self.config.items('feeds')
	
	def load(self):
		try:
			with open(self.file, 'rb') as fin:
				self.config.readfp(fin)
		except Exception as e:
			print 'config.py: Warning: Unable to load config file:', e
			print 'config.py: Info: Generating config file.'
			self.save_default()

	def save_default(self):
		self.config = ConfigParser.RawConfigParser()
		self.config.add_section(self.default_section)
		for key, value in DEFAULT_CONFIG.iteritems():
			self.config.set(self.default_section, key, value)

		self.config.add_section('feeds')
		for key, value in DEFAULT_FEEDS.iteritems():
			self.config.set('feeds', key, value)
		self.save()

	def save(self):
		try:
			with open(self.file, 'wb') as fout:
				self.config.write(fout)
		except Exception as e:
			print 'config.py: Warning: Unable to save config file:', e
