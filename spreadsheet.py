import webapp2
from jinja_templates import jinja_environment
from gdata.spreadsheets.client import SpreadsheetsClient
from gdata.gauth import OAuth2TokenFromCredentials
import google_credentials
import logging

logging.basicConfig(level=logging.INFO)

google_spreadsheet_first_worksheet_id = 'od6'
google_spreadsheet_key = "0Au659FdpCliwdDZDaXBZOUE3X0hvdno4cDBRdHdLUnc"
google_spreadsheet_worksheet_id = 'od6'

reading_references_separator = '|'

# list of column names that will be renamed by the API
renamed_columns = []

# list of column names that contain repeated properties represented as joined strings
repeated_properties = []

# list of column names that contain integer ata
integer_properties = [
    {
        'name': 'nr'
    },
    {
        'name': 'beeldnr'
    }
]


def import_from_spreadsheet(d):
    """
    @param d: dict containing fields of a row in the spreadsheet as they are in the API
    @return: same dict, but with the original row names
    and the strings of the repeating properties split into lists
    """
    for c in integer_properties:
        if c['name'] in d:
            if d[c['name']]:
                d[c['name']] = int(d[c['name']])
    return d


class ListSpreadsheetHandler(webapp2.RequestHandler):
    def get(self):
        qrCodes = QRCodes().table
        template = jinja_environment.get_template('list-cards.html')
        self.response.out.write(template.render(qrCodes=qrCodes))


class Spreadsheet_index():
    """Read a published google spreadsheet into a list of dicts.
       Each dict is a row of the spreadsheet.
       Repeated properties are represented as a list.
       The list is then available as the table attribute."""
    def __init__(self, google_spreadsheet_key, google_worksheet_id, oauth_decorator=None):
        """google_spreadsheet_key is the key of the spreadsheet (can be read from the url)."""
        self._google_spreadsheet_key = google_spreadsheet_key
        self._google_worksheet_id = google_worksheet_id
        self._client = SpreadsheetsClient()
        self._token = OAuth2TokenFromCredentials(oauth_decorator.credentials)
        self._token.authorize(self._client)
        self.table = []
        self.sync_table()

    def sync_table(self):
        del self.table[:]  # table = [] would break the references!
        self._rows = self._client.get_list_feed(
            self._google_spreadsheet_key,
            self._google_worksheet_id
        ).entry
        for row in self._rows:
            self.table.append(import_from_spreadsheet(row.to_dict()))


class QRCodes(Spreadsheet_index):
    """Read the published google spreadsheet containing QRCode card metadata
    into a list of dicts"""
    def __init__(self, oauth_decorator=None):
        Spreadsheet_index.__init__(
            self,
            google_spreadsheet_key,
            google_spreadsheet_worksheet_id,
            oauth_decorator=oauth_decorator
        )

    def update_fields(self, updates):
        Spreadsheet_index.update_fields(self, updates, 'nrc')

    def delete_rows(self, obsolete_rows):
        Spreadsheet_index.delete_rows(self, obsolete_rows, 'nrc')
