import webapp2
from model import QRCode
from jinja_templates import jinja_environment
import urllib
import random

jinja_environment.globals['urlencode'] = urllib.urlencode  # so I can construct URLs in the template


class CardRedirectHandler(webapp2.RequestHandler):
    def get(self):
        nrc = self.request.get('nr')
        qrCode = QRCode.get_by_id(nrc)
        template = jinja_environment.get_template('playing-card.html')
        if self.request.cookies.get('spelen'):
            r = random.random();
            if r < 0.1:
                # give the first other card in the set
                otherQrCode = (QRCode.query(QRCode.kwartetsluggy == qrCode.kwartetsluggy).fetch(3))[0]
                self.response.out.write(template.render(qrCode=otherQrCode))
            elif r < 0.2:
                # give the second other card in the set
                otherQrCode = (QRCode.query(QRCode.kwartetsluggy == qrCode.kwartetsluggy).fetch(3))[1]
                self.response.out.write(template.render(qrCode=otherQrCode))
            elif r < 0.3:
                # give the third other card in the set
                otherQrCode = (QRCode.query(QRCode.kwartetsluggy == qrCode.kwartetsluggy).fetch(3))[2]
                self.response.out.write(template.render(qrCode=otherQrCode))
            elif r < 0.5:
                # rechtvaardige god
                otherQrCode = QRCode.query(QRCode.kwartetsluggy == 'godsbeelden', QRCode.kaartsluggy == 'rechtvaardige-god').get()
                self.response.out.write(template.render(qrCode=otherQrCode, quiz=True))
            elif r < 0.55:
                # toornige god
                otherQrCode = QRCode.query(QRCode.kwartetsluggy == 'godsbeelden', QRCode.kaartsluggy == 'toornige-god').get()
                self.response.out.write(template.render(qrCode=otherQrCode))
            elif r < 0.7:
                # liefdevolle god
                otherQrCode = QRCode.query(QRCode.kwartetsluggy == 'godsbeelden', QRCode.kaartsluggy == 'liefdevolle-god').get()
                self.response.out.write(template.render(qrCode=otherQrCode))
            elif r < 0.9:
                # almachtige god
                otherQrCode = QRCode.query(QRCode.kwartetsluggy == 'godsbeelden', QRCode.kaartsluggy == 'almachtige-god').get()
                self.response.out.write(template.render(qrCode=otherQrCode))
            else:
                # barmhartige god
                otherQrCode = QRCode.query(QRCode.kwartetsluggy == 'godsbeelden', QRCode.kaartsluggy == 'barmhartige-god').get()
                self.response.out.write(template.render(qrCode=otherQrCode))
        else:
            template = jinja_environment.get_template('card.html')
            self.response.out.write(template.render(qrCode=qrCode))
            # I got rid of the redirect... doesn't seem to cause much harm


class CardHandler(webapp2.RequestHandler):
    def get(self, set, card):
        qrCode = QRCode.query(QRCode.kwartetsluggy == set, QRCode.kaartsluggy == card).get()
        template = jinja_environment.get_template('card.html')
        self.response.out.write(template.render(qrCode=qrCode))


class QuizHandler(webapp2.RequestHandler):
    def get(self, category):
        r = random.randint(1,52)
        qrCode = QRCode.query(QRCode.nr == r).get()
        template = jinja_environment.get_template('quiz.html')
        self.response.out.write(template.render(qrCode=qrCode))