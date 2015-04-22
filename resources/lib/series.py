#
#  ABC iView XBMC Addon
#  Copyright (C) 2012 Andy Botting
#
#  This addon includes code from python-iview
#  Copyright (C) 2009-2012 by Jeremy Visser <jeremy@visser.name>
#
#  This addon is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This addon is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this addon. If not, see <http://www.gnu.org/licenses/>.
#

import sys
import os
import urllib2
import urllib
import comm
import utils
import xbmc, xbmcaddon, xbmcgui, xbmcplugin

def make_series_list():

    addon_path = xbmcaddon.Addon().getAddonInfo('path')
    abc3_file = os.path.join(addon_path , "abc3.txt")
    abc3_titles = []
    try:
        with open(abc3_file) as f:
            abc3_titles = f.read().splitlines()
    except:
        pass

    try:
        series_list = comm.get_programme_from_feed('abc4kids')
        series_list += [ s for s in comm.get_programme_from_feed('abc3')
                           if s.title in abc3_titles ]
        series_list.sort()

        ok = True
        for s in series_list:
            url = "%s?%s" % (sys.argv[0], utils.make_url({'series': s.title, 'category': s.category}))

            thumbnail = s.get_thumbnail()
            listitem = xbmcgui.ListItem(s.get_list_title(), iconImage=thumbnail, thumbnailImage=thumbnail)
            listitem.setInfo('video', { 'plot' : s.get_description() })

            # add the item to the media list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=True)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
    except:
        utils.handle_error('Unable to fetch program list. Please try again later.')

