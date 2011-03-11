#!/usr/bin/env python

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

import wx
from wx.lib.mixins.listctrl import TextEditMixin, CheckListCtrlMixin
import os

import config

class MiscPanel(wx.Panel):
    """
    The misc panel of the feedesk config GUI.
    """
    def __init__(self, parent, cfg):
        """
        Initialize misc panel.
        """
        wx.Panel.__init__(self,parent)

        self.cfg = cfg

        # Select Interval of feed
        feed_txt = wx.StaticText(self, label='Feed update interval (min):')
        self.feed_sc = wx.SpinCtrl(self, wx.ID_ANY, '120', min=60, max=360)

        # Select Interval of updating wallpaper
        wall_txt = wx.StaticText(self, label='Wallpaper update interval (min):')
        self.wall_sc = wx.SpinCtrl(self, wx.ID_ANY, '10', min=5, max=60)

        # Select the type of wallpaper update.
        update_txt = wx.StaticText(self, label='Wallpaper update type:')
        self.update_cb = wx.Choice(self, wx.ID_ANY, choices=('Default', 'Random', 'Suffle', 'Latest'), style=wx.CB_READONLY) 

        bold_font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        # Select the size of the screen
        resolution_txt = wx.StaticText(self, label='Screen Resolution:')
        self.detect = wx.Button(self, label='Auto Detect')


        width_txt = wx.StaticText(self, label='Width:')
        self.width_sc = wx.SpinCtrl(self, wx.ID_ANY, '1024', min=1, max=9999)

        height_txt = wx.StaticText(self, label='Height:')
        self.height_sc = wx.SpinCtrl(self, wx.ID_ANY, '768', min=1, max=9999)

        # The sizer
        grid_sizer = wx.FlexGridSizer(0, 2)
        grid_sizer.Add(feed_txt, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        grid_sizer.Add(self.feed_sc, 1, wx.EXPAND | wx.ALL, 5)
        grid_sizer.Add(wall_txt, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        grid_sizer.Add(self.wall_sc, 1, wx.EXPAND | wx.ALL, 5)
        grid_sizer.Add(update_txt, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        grid_sizer.Add(self.update_cb, 1, wx.EXPAND | wx.ALL, 5)
        grid_sizer.Add(resolution_txt, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        grid_sizer.Add(self.detect, 1, wx.EXPAND | wx.ALL, 5)
        grid_sizer.Add(width_txt, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        grid_sizer.Add(self.width_sc, 1, wx.EXPAND | wx.ALL, 5)
        grid_sizer.Add(height_txt, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        grid_sizer.Add(self.height_sc, 1, wx.EXPAND | wx.ALL, 5)
        grid_sizer.AddGrowableCol(1)

        # bind things together
        self.SetSizer(grid_sizer)
        self.SetAutoLayout(True)
        grid_sizer.Fit(self)

        self.load_options()

    def load_options(self):
        pass

class FeedListCtrl(wx.ListCtrl, TextEditMixin, CheckListCtrlMixin):
    """
    The Feed List Control
    """
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize):
        wx.ListCtrl.__init__(self, parent, id, pos, size,
            style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        TextEditMixin.__init__(self)
        CheckListCtrlMixin.__init__(self)
        self.InsertColumn(0, 'URL')
        self.SetColumnWidth(0, size[1] - 60)

class FeedPanel(wx.Panel):
    """
    The feed panel for feedesk config GUI.
    """
    def __init__(self, parent, cfg):
        wx.Panel.__init__(self, parent)

        self.cfg = cfg

        # The left (FeedListCtrl)
        self.feed_list = FeedListCtrl(self, size=(250, 300))
        #self.feed_list = wx.ListBox(self, size=(250, 300))
        
        # The right (Buttons on a vbox)
        self.add = wx.Button(self, label='Add')
        self.delete = wx.Button(self, label='Delete')
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.add, 0, wx.TOP, 5)
        vbox.Add(self.delete, 0, wx.TOP, 5)

        # Bind events
        self.add.Bind(wx.EVT_BUTTON, self._on_add_click)
        self.delete.Bind(wx.EVT_BUTTON, self._on_delete_click)
        
        # The sizer
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.feed_list, 1, wx.EXPAND | wx.ALL, 5)
        hbox.Add(vbox, 0, wx.ALL, 5)

        self.SetSizer(hbox)
        self.SetAutoLayout(True)
        hbox.Fit(self)

        self.load_feeds()

    def load_feeds(self):
        feeds = self.cfg.get_all_feeds()
        for i, (url, enabled) in enumerate(feeds):
            self.feed_list.Append((url,))
            if enabled:
                self.feed_list.ToggleItem(i)

    def save_feeds(self):
        feeds = []
        for i in xrange(self.feed_list.GetItemCount()):
            feeds.append((
                self.feed_list.GetItem(i, 0).GetText(),
                self.feed_list.IsChecked(i)))

        self.cfg.clear_feeds()
        self.cfg.set_feeds(feeds)

    def _on_add_click(self, event):
        self.feed_list.Append(('http://',))

    def _on_delete_click(self, event):
        item = self.feed_list.GetFirstSelected()
        while item != -1:
            self.feed_list.DeleteItem(item)
            item = self.feed_list.GetNextSelected(item - 1)

class ConfigWindow(wx.Frame):
    """
    The main window of the feedesk config GUI.
    """
    def __init__(self, parent, cfg):
        """
        Initialize the main window.
        """
        wx.Frame.__init__(self, parent, title='feedesk', size=(320, 350))

        self.cfg = cfg

        # The top (a notebook)
        nb = wx.Notebook(self, style=wx.NB_TOP)

        # Feed panel
        self.feed_panel = FeedPanel(nb, cfg)
        nb.AddPage(self.feed_panel, 'Feed')

        # Misc panel
        self.misc_panel = MiscPanel(nb, cfg)
        nb.AddPage(self.misc_panel, 'Misc')

        # The bottom (a sizer with two buttons)
        self.save = wx.Button(self, label='Save')
        self.cancel = wx.Button(self, label='Cancel')

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.save, 1, wx.EXPAND | wx.RIGHT, 5)
        hbox.Add(self.cancel, 1, wx.EXPAND | wx.LEFT, 5)

        # Bind events
        self.save.Bind(wx.EVT_BUTTON, self._on_save_click)
        self.cancel.Bind(wx.EVT_BUTTON, self._on_cancel_click)
        
        # The sizer
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(nb, 1, wx.EXPAND | wx.ALL, 10)
        vbox.Add(hbox, 0, wx.EXPAND | wx.RIGHT | wx.LEFT | wx.BOTTOM, 10)

        # Load settings

        # Set sizer
        self.SetSizer(vbox)
        self.SetAutoLayout(True)
        vbox.Fit(self)
        self.Show(True)

    def _on_save_click(self, event):
        '''
        Save the options in to config file.
        '''
        self.feed_panel.save_feeds()
        self.cfg.save()
    
    def _on_cancel_click(self, event):
        '''
        Exit the gui_config.
        '''
        self.Destroy()

def main():
    config.create_app_dir()
    cfg = config.Config(os.path.join(config.get_home_path(), '.feedesk', '.feedesk'))

    app = wx.App(False)
    frame = ConfigWindow(None, cfg)
    app.MainLoop()

if __name__ == '__main__':
    main()
