#
#  ABC iView XBMC Addon
#  Copyright (C) 2012 Andy Botting
#
#  This plugin includes code from python-iview
#  Copyright (C) 2009-2012 by Jeremy Visser <jeremy@visser.name>
#
#  This plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this plugin. If not, see <http://www.gnu.org/licenses/>.
#

import sys, re, traceback
import htmlentitydefs, cgi, unicodedata, urllib
import urllib2, socket
import textwrap
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import config
import issue_reporter

pattern = re.compile("&(\w+?);")


def descape_entity(m, defs=htmlentitydefs.entitydefs):
    # callback: translate one entity to its ISO Latin value
    try:
        return defs[m.group(1)]
    except KeyError:
        return m.group(0) # use as is


def descape(string):
    # Fix the hack back from parsing with BeautifulSoup
    string = string.replace('&#38;', '&amp;')

    return pattern.sub(descape_entity, string)


def get_url(s):
    dict = {}
    pairs = s.lstrip("?").split("&")
    for pair in pairs:
        if len(pair) < 3: continue
        kv = pair.split("=",1)
        k = kv[0]
        v = urllib.unquote_plus(kv[1])
        dict[k] = v
    return dict


def make_url(d):
    pairs = []
    for k,v in d.iteritems():
        k = urllib.quote_plus(k)
        # Values can possibly be - UTF-8 as an ASCII str, ASCII as an ASCII str, or unicode. Want clean ASCII for URL.
        if not isinstance(v, unicode):
            v = str(v)
            v = v.decode("utf-8")
        v = unicodedata.normalize('NFC', v).encode('ascii','ignore')
        v = urllib.quote_plus(v)
        pairs.append("%s=%s" % (k,v))
    return "&".join(pairs)


def log(s):
    print "[%s v%s] %s" % (config.NAME, config.VERSION, s)


def log_error(message=None):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if message:
        exc_value = message
    print "[%s v%s] ERROR: %s (%d) - %s" % (config.NAME, config.VERSION, exc_traceback.tb_frame.f_code.co_name, exc_traceback.tb_lineno, exc_value)
    print traceback.print_exc()


def dialog_error(err=None):
    # Generate a list of lines for use in XBMC dialog
    msg = ''
    content = []
    exc_type, exc_value, exc_traceback = sys.exc_info()
    content.append("%s v%s Error" % (config.NAME, config.VERSION))
    content.append(str(exc_value))
    if err:
        msg = " - %s" % err
    content.append("%s (%d) %s" % (exc_traceback.tb_frame.f_code.co_name, exc_traceback.tb_lineno, msg))
    return content


def dialog_message(msg, title=None):
    if not title:
        title = "%s v%s" % (config.NAME, config.VERSION)
    # Add title to the first pos of the textwrap list
    content = textwrap.wrap(msg, 60)
    content.insert(0, title)
    return content


def get_platform():
    """ Work through a list of possible platform types and return the first
        match. Ordering of items is important as some match more thant one type.

        E.g. Android will match both Android and Linux
    """
    platforms = [
        "Android",
        "Linux.RaspberryPi",
        "Linux",
        "XBOX",
        "Windows",
        "ATV2",
        "IOS",
        "OSX",
        "Darwin",
    ]

    for platform in platforms:
        if xbmc.getCondVisibility('System.Platform.'+platform):
            return platform
    return "Unknown"


def get_xbmc_build():
    return xbmc.getInfoLabel("System.BuildVersion")


def get_xbmc_version():
    build = get_xbmc_build()
    # Keep the version number, and strip the rest
    version = build.split(' ')[0]
    return version


def log_xbmc_platform_version():
    """ Log our XBMC version and platform for debugging
    """
    version = get_xbmc_version()
    platform = get_platform()
    log("XBMC %s running on %s" % (version, platform))


def handle_error(err=None):
    traceback_str = traceback.format_exc()
    log(traceback_str)
    report_issue = False
    d = xbmcgui.Dialog()
    if d:
        message = dialog_error(err)
        try:
            message.append("Would you like to automatically report this error?")
            report_issue = d.yesno(*message)
        except:
            message.append("If this error continues to occur, please report it to our issue tracker.")
            d.ok(*message)
    if report_issue:
        log("Reporting issue to GitHub...")
        issue_url = issue_reporter.report_issue(traceback_str)
        if issue_url:
            # Split the url here to make sure it fits in our dialog
            split_url = issue_url.replace('/xbmc', ' /xbmc')
            d.ok("%s v%s Error" % (config.NAME, config.VERSION), "Thanks! Your issue has been reported to: %s" % split_url)
