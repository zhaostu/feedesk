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

import os
import ConfigParser

DEFAULT_OPTIONS = {'screen_width': 1024, 'screen_height': 768,
        'interval_feed': 240, 'interval_wallpaper': 10, 'type': 'random'}

class Config():
    def __init__(self, file):
        self.options_section = 'options'
        self.feeds_section = 'feeds'
        self.feeds_disabled_section = 'feeds_disabled'
        self.file = file

        self.config = ConfigParser.RawConfigParser()
        self.load()

    def load(self):
        try:
            with open(self.file, 'rb') as fin:
                self.config.readfp(fin)
        except Exception as e:
            print 'config.py: Warning: Unable to load config file:', e
            self.save_default()

    def save_default(self):
        print 'config.py: Info: Generating config file.'
        self.config = ConfigParser.RawConfigParser()
        self.config.add_section('options')
        for key, value in DEFAULT_OPTIONS.iteritems():
            self.set(key, value)

        self.clear_feeds()
        self.save()

    def save(self):
        try:
            with open(self.file, 'wb') as fout:
                self.config.write(fout)
        except Exception as e:
            print 'config.py: Warning: Unable to save config file:', e

    def set(self, key, value):
        self.config.set('options', key, value)

    def get(self, key):
        return self.config.get('options', key)
    
    def getint(self, key):
        return self.config.getint('options', key)
    
    def getbool(self, key):
        return self.config.getboolean('options', key)
        
    def getfloat(self, key):
        return self.config.getfloat('options', key)

    def clear_feeds(self):
        self.config.remove_section('feeds')
        self.config.remove_section('feeds_disabled')
        self.config.add_section('feeds')
        self.config.add_section('feeds_disabled')

    def set_feeds(self, feeds):
        '''
        Add feeds into the config file.

        Args: feeds, a list of tuple [(url, enabled), (...), ...]
        '''
        for i, (url, enabled) in enumerate(feeds):
            if enabled:
                self.config.set('feeds', str(i), url)
            else:
                self.config.set('feeds_disabled', str(i), url)


    def get_feeds(self):
        return self.config.items('feeds')

    def get_all_feeds(self):
        feeds = self.config.items('feeds')
        feeds_disabled = self.config.items('feeds_disabled')

        feeds = [(url, True) for id, url in sorted(feeds)]
        feeds_disabled = [(url, False) for id, url in sorted(feeds_disabled)]

        feeds.extend(feeds_disabled)
        return feeds

def create_app_dir():
    home_path = get_home_path()
    try:
        os.mkdir(os.path.join(home_path, '.feedesk'))
    except:
        pass
    try:
        os.mkdir(os.path.join(home_path, '.feedesk', 'picture'))
    except:
        pass

def get_home_path():
    if os.name == 'posix':
        return os.environ['HOME']
    elif os.name == 'nt':
        return os.environ['APPDATA']
