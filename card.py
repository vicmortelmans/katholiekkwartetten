import webapp2
from model import QRCode
from model import MC
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
            elif r < 0.6:
                # rechtvaardige god
                otherQrCode = QRCode.query(QRCode.kwartetsluggy == 'godsbeelden', QRCode.kaartsluggy == 'rechtvaardige-god').get()
                self.response.out.write(template.render(qrCode=otherQrCode, quiz=True))
            elif r < 0.65:
                # toornige god
                otherQrCode = QRCode.query(QRCode.kwartetsluggy == 'godsbeelden', QRCode.kaartsluggy == 'toornige-god').get()
                self.response.out.write(template.render(qrCode=otherQrCode))
            elif r < 0.8:
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
        if category == 'kwartetvraag':
            r = random.randint(1,52)
            qrCode = QRCode.query(QRCode.nr == r).get()
            template = jinja_environment.get_template('quiz.html')
            self.response.out.write(template.render(category='Kwartetvraag', vraag=qrCode.vraag, antwoord=qrCode.antwoord))
        elif category == 'catechismus1':
            (l, i) = randomInTwoRanges(22, 27)
            mc = MC.query(MC.l == l, MC.i == i).get()
            template = jinja_environment.get_template('quiz.html')
            self.response.out.write(template.render(category='Vraag uit de catechismus (1-2)', vraag=mc.q, antwoord=mc.a))
        elif category == 'catechismus2':
            (l, i) = randomInTwoRanges(76, 86)
            mc = MC.query(MC.l == l + 2, MC.i == i).get()
            template = jinja_environment.get_template('quiz.html')
            self.response.out.write(template.render(category='Vraag uit de catechismus (3-4)', vraag=mc.q, antwoord=mc.a))
        elif category == 'catechismus3':
            (l, i) = randomInThreeRanges(99, 70, 67)
            mc = MC.query(MC.l == l + 4, MC.i == i).get()
            template = jinja_environment.get_template('quiz.html')
            self.response.out.write(template.render(category='Vraag uit de catechismus (5-7)', vraag=mc.q, antwoord=mc.a))



def randomInTwoRanges(l1, l2):
    """
    take a random hit out of two ranges [1..l1] and [1..l2],
    return (l,n) where l is the range (1 or 2) and n is the index of the hit in that range
    :param l1: size of first range
    :param l2: size of second range
    """
    r = random.randint(1, l1 + l2)
    l = 1 if r <= l1 else 2
    n = r if r <= l1 else r - l1
    return l, n


def randomInThreeRanges(l1, l2, l3):
    """
    same as above
    """
    r = random.randint(1, l1 + l2 + l3)
    if r <= l1:
        l = 1
        n = r
    elif r <= l1 + l2:
        l = 2
        n = r - l1
    else:
        l = 3
        n = r - l1 - l2
    return l, n