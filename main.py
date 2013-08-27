import webapp2

routes = [
    webapp2.Route(r'/_ah/start', handler='main.StartBackendHandler'),
    webapp2.Route(r'/kaart/link', handler='card.CardRedirectHandler'),
    webapp2.Route(r'/quiz/<category>', handler='card.QuizHandler'),
    webapp2.Route(r'/<set>/<card>', handler='card.CardHandler'),
    webapp2.Route(r'/list-spreadsheet', handler='spreadsheet.ListSpreadsheetHandler'),
    webapp2.Route(r'/list-datastore', handler='datastore.ListDatastoreHandler'),
    webapp2.Route(r'/sync', handler='sync.SyncHandler'),
    webapp2.Route(r'/sync-mc', handler='sync.SyncMCHandler')
]

app = webapp2.WSGIApplication(routes, debug=True)

class StartBackendHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("OK")
