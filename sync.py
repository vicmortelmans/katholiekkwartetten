import webapp2
from jinja_templates import jinja_environment
import spreadsheet
import datastore
import spreadsheetMC
import datastoreMC
import re
from main import decorator


class SyncHandler(webapp2.RequestHandler):

    @decorator.oauth_required
    def get(self):
        # get the contents of the spreadsheet
        spreadsheet_mgr = spreadsheet.QRCodes(oauth_decorator=decorator)
        self.spreadsheet = spreadsheet_mgr.table

        # get the contents of the datastore
        datastore_mgr = datastore.QRCodes()
        self.datastore = datastore_mgr.table

        # get all entities from the datastore
        all_entities = {}
        self.get_all_entities(all_entities)

        # delete all entities from the datastore
        datastore_mgr.delete_entities(all_entities)

        # bulkload the data from the spreadsheet to the datastore
        datastore_mgr.bulkload_table(self.spreadsheet)

        # the app redirects the user to the index
        template = jinja_environment.get_template('list-cards.html')
        self.response.out.write(template.render(qrCodes=self.datastore))

    def get_all_entities(self, d):
        """
        @param d: an emtpy dict
        @return: the dict filled with 'nrc' values from the datastore
        """
        for i in self.datastore:
            d[i['nrc']] = {}


class SyncMCHandler(webapp2.RequestHandler):
    def get(self):
        # get the contents of the spreadsheet
        spreadsheet_mgr = spreadsheetMC.MC(oauth_decorator=decorator)
        self.spreadsheet = spreadsheet_mgr.table

        # get the contents of the datastore
        datastore_mgr = datastoreMC.MC()
        self.datastore = datastore_mgr.table

        # get all entities from the datastore
        all_entities = {}
        self.get_all_entities(all_entities)

        # delete all entities from the datastore
        datastore_mgr.delete_entities(all_entities)

        # bulkload the data from the spreadsheet to the datastore
        datastore_mgr.bulkload_table(self.spreadsheet)

        # the app redirects the user to the index
        template = jinja_environment.get_template('list-mc.html')
        self.response.out.write(template.render(mc=self.datastore))

    def get_all_entities(self, d):
        """
        @param d: an emtpy dict
        @return: the dict filled with 'n' values from the datastore
        """
        for i in self.datastore:
            d[i['n']] = {}

