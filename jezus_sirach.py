# this one is added here to avoid spending a separate app on it

import webapp2
from jinja_templates import jinja_environment
import urllib2
import urllib
import time
import datetime
import xml.etree.ElementTree as ET
import cgi
import logging
import httplib
from google.appengine.runtime import apiproxy_errors
import json


class JezusSirachHandler(webapp2.RequestHandler):
    def get(self):
        # 20150930 Yahoo pipes is deprecated
        yql = 'use "https://raw.githubusercontent.com/vicmortelmans/yql-tables/master/data/twittertextfeed.xml" as twittertextfeed; select * from twittertextfeed where url = "http://users.telenet.be/vicmortelmans/ecclesiasticus.txt" and frequency = "1" and startdate = "2011/06/08" and length = "140";'
        query = "http://query.yahooapis.com/v1/public/yql?q=%s&format=json" % urllib.quote_plus(yql)
        logging.info("Going to query %s [%s]." % (yql, query))
        sleep = 1
        for attempt in range(10):
            try:
                logging.info("Querying %s." % yql)
                result = urllib2.urlopen(query).read()
            except (httplib.HTTPException, apiproxy_errors.DeadlineExceededError) as e:
                time.sleep(sleep)  # pause to avoid "Rate Limit Exceeded" error
                logging.warning("Sleeping %d seconds because of HttpError trying to query %s (%s)." % (sleep, query, e))
                sleep *= 2
            else:
                break  # no error caught
        else:
            logging.critical("Retried 10 times querying %s." % query)
            raise  # attempts exhausted
        items = []
        for item in reversed(json.loads(result)['query']['results']['results']['item']):
            content = item['line']
            items.append({
                'title': cgi.escape(content),
                'description': cgi.escape(content),
                'guid': cgi.escape(content)
            })
        date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
        midnight = datetime.datetime.combine(datetime.datetime.now(), datetime.time.min)
        long_date_midnight = datetime.datetime.strftime(midnight, "%a, %d %b %Y %H:%M:%S +0000")
        long_date = datetime.datetime.strftime(datetime.datetime.now(), "%a, %d %b %Y %H:%M:%S +0000")
        template = jinja_environment.get_template('jezus-sirach.rss')
        output = template.render(
            items=items,
            date=date,
            long_date=long_date,
            long_date_midnight=long_date_midnight
        )
        self.response.headers['Cache-Control'] = 'public,max-age=%s' % 900
        self.response.headers['Content-Type'] = 'text/xml; charset=utf-8'
        self.response.out.write(output)