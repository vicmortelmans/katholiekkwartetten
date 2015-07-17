# this one is added here to avoid spending a separate app on it

import webapp2
from jinja_templates import jinja_environment
import urllib2
import time
import datetime
import xml.etree.ElementTree as ET
import cgi


class InnerlijkLevenHandler(webapp2.RequestHandler):
    def get(self):
        url = "https://9f9de36913d4ce56639a9e232a5dd522e288f02d.googledrive.com/host/0B-659FdpCliwRkRYclJvRUFZNFU/innerlijk-leven-html/%s.html" % time.strftime("%Y-%m-%d")
        html = urllib2.urlopen(url).read()
        root = ET.fromstring(html)
        title = root.find('body').find('h1').text
        div = root.find('body').find('div')
        content = ET.tostring(div, encoding="ascii")
        date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
        midnight = datetime.datetime.combine(datetime.datetime.now(), datetime.time.min)
        long_date_midnight = datetime.datetime.strftime(midnight, "%a, %d %b %Y %H:%M:%S GMT")
        long_date = datetime.datetime.strftime(datetime.datetime.now(), "%a, %d %b %Y %H:%M:%S GMT")
        template = jinja_environment.get_template('innerlijk-leven.rss')
        output = template.render(
            title=title,
            description=cgi.escape(content),
            date=date,
            long_date=long_date,
            long_date_midnight=long_date_midnight
        )
        self.response.headers['Cache-Control'] = 'public,max-age=%s' % 86400
        self.response.headers['Content-Type'] = 'application/rss+xml'
        self.response.out.write(output)