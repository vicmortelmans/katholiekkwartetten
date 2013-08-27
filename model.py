from google.appengine.ext import ndb


class QRCode(ndb.Model):
    """ the key is the same as the nrc field """
    nrc = ndb.StringProperty(required=True)
    nr = ndb.IntegerProperty()
    kwartet = ndb.StringProperty()
    kwartetsluggy = ndb.StringProperty()
    kaart = ndb.StringProperty()
    kaartsluggy = ndb.StringProperty()
    cardurl = ndb.TextProperty()
    firstcardurl = ndb.TextProperty()
    secondcardurl = ndb.TextProperty()
    thirdcardurl = ndb.TextProperty()
    url = ndb.TextProperty()
    beeld = ndb.TextProperty()
    uitleg = ndb.TextProperty()
    vraag = ndb.TextProperty()
    antwoord = ndb.TextProperty()
    embed = ndb.TextProperty()
    fullurl = ndb.TextProperty()


class MC(ndb.Model):
    n = ndb.IntegerProperty(required=True)
    l = ndb.IntegerProperty()
    i = ndb.IntegerProperty()
    q = ndb.TextProperty()
    a = ndb.TextProperty()