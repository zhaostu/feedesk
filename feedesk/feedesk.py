#! /usr/bin/env python

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
__version__ = "0.1.8pre2"

import config
import feeds
import os

class Feedesk():
    def __init__(self):
        if os.name == 'posix':
            self.app_path = os.environ['HOME']
            self.cmd = 'gconftool -s /desktop/gnome/background/picture_filename -t string "%s"'
        elif os.name == 'nt':
            self.app_path = os.environ['APPDATA']
            self.cmd = os.path.join(os.getcwd(), 'windesk', 'windesk.exe') + ' "%s"'
        
        self.app_path = os.path.join(self.app_path, '.feedesk')
        self.pic_path = os.path.join(self.app_path, 'picture')
        # create necessary folders
        try:
            os.mkdir(self.app_path)
            os.mkdir(self.pic_path)
        except:
            pass

        # load config
        cfg_path = os.path.join(self.app_path, 'config.cfg')
        self.cfg = config.Config(cfg_path)
        
        # load feeds
        self.fds = feeds.Feeds(self.cfg.getfeedlist(),
                os.path.join(self.app_path, 'index.pickle'),
                self.pic_path)
        
        # load plugins
        ##TODO

    def set_wallpaper(self):
        type = self.cfg.get('type')
        if type == 'random':
            pic = self.fds.get_random_pic()
            if pic != None:
                cmd = self.cmd % pic['file']
                os.system(cmd)
        elif type == '':
            ##TODO: 
            pass
    
    def daemon(self):
        import time
        ifeed = self.cfg.getfloat('interval_feed')
        iwall = self.cfg.getfloat('interval_wallpaper')

        lfeed = ifeed
        lwall = iwall
        while True:
            if ifeed == lfeed:
                print 'feedesk.py: Info: Refreshing feeds.'
                self.fds.refresh()

            if iwall == lwall:
                print 'feedesk.py: Info: Setting wallpaper.'
                self.set_wallpaper()
            
            # find next wake up time
            if lfeed < lwall:
                sleep_time = lfeed
                lfeed = ifeed
                lwall -= sleep_time
            else:
                sleep_time = lwall
                lwall = iwall
                lfeed -= sleep_time

            # sleep and renew times
            time.sleep(sleep_time * 60)

if __name__ == '__main__':
    fd = Feedesk()
    fd.daemon()
    #test()

## VERSION HISTORY
# 0.1.0 Original Version, Downloads the latest sentense.me wallpaper
#   and apply to gnome desktop
# 0.1.1 sentense.me for windows
# 0.2.0 rewrite for plugins, operation systems
###################################################################
# BLUEPRINT
# 0.2.1 change feeds.pics into list to support shuffle.

