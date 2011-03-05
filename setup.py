#!/usr/bin/env python

from distutils.core import setup

setup(name='feedesk',
      version           = '0.1.8pre-2',
      description       = 'Read images from media RSS feeds, and set as desktop background.',
      author            = 'Yanglei Zhao',
      author_email      = 'z12y12l12@gmail.com',
      url               = 'https://github.com/zhaostu/feedesk',
      packages          = ['feedesk', 'feedesk.feedparser'],
      zip_safe          = True,
)

