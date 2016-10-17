# this one is added here to avoid spending a separate app on it

import webapp2
from jinja_templates import jinja_environment
import urllib2
import time
import datetime
import xml.etree.ElementTree as ET
import cgi
import logging


class NavolgingVanChristusHandler(webapp2.RequestHandler):
    def get(self):
        url = "https://storage.googleapis.com/navolging-van-christus/%s.html" % time.strftime("%Y-%m-%d")
        data = {}
        data['date'] = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
        midnight = datetime.datetime.combine(datetime.datetime.now(), datetime.time.min)
        data['long_date_midnight'] = datetime.datetime.strftime(midnight, "%a, %d %b %Y %H:%M:%S +0000")
        data['long_date'] = datetime.datetime.strftime(datetime.datetime.now(), "%a, %d %b %Y %H:%M:%S +0000")
        try:
            html = urllib2.urlopen(url).read()
        except urllib2.HTTPError:
            logging.info("No sources on URL %s" % url)
        else:
            root = ET.fromstring(html)
            data['url'] = url
            data['title'] = root.find('body').find('h1').text
            div = root.find('body').find('div')
            data['description'] = cgi.escape(ET.tostring(div, encoding="ascii"))
        template = jinja_environment.get_template('navolging-van-christus.rss')
        output = template.render(
            data=data
        )
        self.response.headers['Cache-Control'] = 'public,max-age=%s' % 900
        self.response.headers['Content-Type'] = 'text/xml; charset=utf-8'
        self.response.out.write(output)


class InnerlijkLevenHandler(webapp2.RequestHandler):
    def get(self):
        # 20150902 note that googledrive.com/host is deprecated on 20160831
        url = "https://googledrive.com/host/0B-659FdpCliwRkRYclJvRUFZNFU/innerlijk-leven-html/%s.html" % time.strftime("%Y-%m-%d")
        html = urllib2.urlopen(url).read()
        root = ET.fromstring(html)
        title = root.find('body').find('h1').text
        div = root.find('body').find('div')
        content = ET.tostring(div, encoding="ascii")
        date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
        midnight = datetime.datetime.combine(datetime.datetime.now(), datetime.time.min)
        long_date_midnight = datetime.datetime.strftime(midnight, "%a, %d %b %Y %H:%M:%S +0000")
        long_date = datetime.datetime.strftime(datetime.datetime.now(), "%a, %d %b %Y %H:%M:%S +0000")
        template = jinja_environment.get_template('innerlijk-leven.rss')
        output = template.render(
            title=title,
            description=cgi.escape(content),
            url=url,
            date=date,
            long_date=long_date,
            long_date_midnight=long_date_midnight
        )
        self.response.headers['Cache-Control'] = 'public,max-age=%s' % 900
        self.response.headers['Content-Type'] = 'text/xml; charset=utf-8'
        self.response.out.write(output)