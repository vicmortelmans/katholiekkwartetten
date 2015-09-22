import webapp2
from oauth2client.appengine import OAuth2Decorator
import google_credentials

decorator = OAuth2Decorator(client_id=google_credentials.CLIENT_ID,
                            client_secret=google_credentials.CLIENT_SECRET,
                            scope='https://spreadsheets.google.com/feeds https://www.googleapis.com/auth/drive')

routes = [
    webapp2.Route(r'/_ah/start', handler='main.StartBackendHandler'),
    webapp2.Route(r'/kaart/link', handler='card.CardRedirectHandler'),
    webapp2.Route(r'/quiz/<category>', handler='card.QuizHandler'),
    webapp2.Route(r'/<set>/<card>', handler='card.CardHandler'),
    webapp2.Route(r'/list-spreadsheet', handler='spreadsheet.ListSpreadsheetHandler'),
    webapp2.Route(r'/list-datastore', handler='datastore.ListDatastoreHandler'),
    webapp2.Route(r'/sync', handler='sync.SyncHandler'),
    webapp2.Route(r'/sync-mc', handler='sync.SyncMCHandler'),
    # this one is added here to avoid spending a separate app on it
    webapp2.Route(r'/innerlijk-leven.rss', handler='innerlijk_leven.InnerlijkLevenHandler'),
    webapp2.Route(r'/heiligen-net.rss', handler='heiligen_net.HeiligenNetHandler'),
    webapp2.Route(r'/jezus-sirach.rss', handler='jezus_sirach.JezusSirachHandler'),
    webapp2.Route(decorator.callback_path, handler=decorator.callback_handler())
]

app = webapp2.WSGIApplication(routes, debug=True)

class StartBackendHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("OK")
