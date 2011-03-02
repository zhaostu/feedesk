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

from feedparser import feedparser
from sgmllib import SGMLParser
import cPickle
import random

ACCEPTED_FORMAT = ['bmp', 'jpeg', 'jpg', 'png']

class Feeds():
#self.feeds: feed_name: FeedParserDict
#self.pics: {pic_url: [picdict, ...], ...}
#picdict: url, updated, width, height, file, deleted

	def __init__(self, feedlist, file, pic_path):
		#init random
		random.seed()

		self.feedlist = feedlist
		self.pic_path = pic_path

		# default extractors
		self.default_extractor = DefaultExtractor()

		self.file = file
		self.load()
		self.clean_feeds()
		self.refresh()
	
	def clean_feeds(self):
		for name in self.feeds.keys():
			if name not in self.feedlist:
				del self.feeds[name]
	
	def refresh(self):
		for name, url in self.feedlist:
			try:
				if not self.feeds.has_key(name):
					# just download the feed
					self.feeds[name] = feedparser.parse(url)
				else:
					of = self.feeds[name] # back up old feed
					if hasattr(of, 'etag'):
						# download new feed
						nf = feedparser.parse(url, etag=of.etag)
					elif hasattr(of, 'modified'):
						nf = feedparser.parse(url, modified=of.modified)
					else:
						nf = feedparser.parse(url)
					# if not all the same
					if nf.status != 304:
						self.feeds[name] = nf
			except Exception as e:
				print 'feeds.py: Warning: unable to download feed "%s":' % name, e

		# generate new picture list
		pics_new = {}
		for name, feed in self.feeds.iteritems():
			pic_list = self.extract(feed)
			for p in pic_list:
				pics_new[p['url']] = p
		
		# delete obsolete pics
		for url in self.pics.keys():
			if not url in pics_new:
				self.delete_pic(url)
		
		# move new pics
		for url in pics_new.keys():
			if not url in self.pics:
				self.pics[url] = pics_new[url]
		self.save()
	
	def delete_pic(self, url):
		if self.pics[url].has_key('file'):
			import os
			# delete file
			try:
				os.remove(self.pics[url]['file'])
			except:
				print 'feeds.py: Warning: unable to delete pictur "%s":' % file, e

		del self.pics[url]
	
	def extract(self, feed):
		self.default_extractor.reset()
		return self.default_extractor.extract(feed)
	
	def load(self):
		# Load file
		try:
			with open(self.file, 'rb') as fin:
				flist = cPickle.load(fin)
			self.feeds = flist[0]
			self.pics = flist[1]
		except Exception as e:
			print 'feeds.py: Warning: Unable to load index file:', e
			print 'feeds.py: Info: Generating index file.'
			self.feeds = {} # feed_name: FeedParserDict
			self.pics = {} # {feed_name: [picdict, ...], ...}
			self.save()

	def get_random_pic(self):
	##TODO: should be written
		import urlparse, os
		for i in xrange(0, 10):
			num = random.randint(0, len(self.pics) - 1)
			url = self.pics.keys()[num]
			if not self.pics[url].has_key('file'):
				# not downloaded, download
				filename = urlparse.urlsplit(url)[2].split('/')[-1]
				filename = os.path.join(self.pic_path, filename)
				try:
					self.download(url, filename)
					self.pics[url]['file'] = filename
					self.save()
				except:
					# download failed
					##TODO: This will do a infinite retry while internet is not connected.
					continue
			return self.pics[url]
		return None

	def download(self, url, filename):
		import urllib
		try:
			remote = urllib.urlopen(url)
			local = open(filename, 'wb')
			local.write(remote.read())
			remote.close()
			local.close()
			print 'feeds.py: Info: Wallpaper downloaded: "%s".' % url
		except:
			print 'feeds.py: Warning: Unable to download file "%s":' % url, e
			raise

	def save(self):
		flist = [self.feeds, self.pics]
		try:
			with open(self.file, 'wb') as fout:
				cPickle.dump(flist, fout, protocol=cPickle.HIGHEST_PROTOCOL)
		except Exception as e:
			print 'feeds.py: Warning: Unable to save index file:', e

class DefaultExtractor():
	def __init__(self):
		self.html_extractor = HTMLExtractor()
	
	# extract from photo feed
	def reset(self):
		self.pictures = []

	def extract(self, feed):
		if feed.version.startswith('atom') or feed.version.startswith('rss'):
			for entry in feed.entries:
				self.extract_entry(entry)
		else:
			print 'feeds.py: Warning: Unknown feed type "%s".' % feed.version
		return self.pictures

	def extract_entry(self, entry):
		if entry.has_key('media_content'):
			self.extract_media(entry.media_content, entry.updated_parsed)
			return
		enclosure = [link for link in entry.links
			if link['rel'] == 'enclosure' and link['type'].startswith('image')]
		if enclosure:
			self.extract_enclosure(enclosure, entry.updated_parsed)
			return
		if entry.has_key('description'):
			pic_list = self.html_extractor.extract(entry.description)
			if pic_list:
				self.pictures.extend(pic_list)
		elif entry.has_key('content'):
			pic_list = self.html_extractor.extract(entry.content)
			if pic_list:
				self.pictures.extend(pic_list)
		else:
			print 'feeds.py: Warning: Unknown entry type.'

	def extract_media(self, media_content, updated):
		for mc_item in media_content:
			# medium is a optional attribute.
			from urlparse import urlsplit
			if (mc_item.has_key('medium') and mc_item['medium'] == 'image') \
			or urlsplit(mc_item['url'].lower())[2].split('.')[-1] \
			in ACCEPTED_FORMAT:
				picdict = {'url': mc_item['url']}
				# set date
				picdict['updated'] = updated
				# set width and height
				if mc_item.has_key('width') and mc_item.has_key('height'):
					picdict['width'] = mc_item['width']
					picdict['height'] = mc_item['height']
				self.pictures.append(picdict)

	def extract_enclosure(self, enclosure, updated):
		for link in enclosure:
			picdict = {'url': link['url']}
			# set date
			picdict['updated'] = updated
			# set width and height
			if link.has_key('width') and link.has_key('height'):
				picdict['width'] = link['width']
				picdict['height'] = link['height']
			self.pictures.append(picdict)

##TODO: extract <a> and <img>
class HTMLExtractor(SGMLParser):
	def __init__(self):
		SGMLParser.__init__(self)
	
	def reset(self):
		SGMLParser.reset(self)
		self.in_a = 0
		self.url = ''
		self.pictures = []

	def extract(self, feed):
		pass

	def start_a(self, attrs):
		try:
			self.url = [v for k, v in attrs if k == 'href'][0]
			self.in_a = 1
			self.height = -1
			self.width = -1
		except:
			pass

	def end_a(self):
		self.pictures.append((self.width, self.height, self.url))
		self.url = ''
		self.in_a = 0
