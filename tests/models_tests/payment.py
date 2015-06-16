from tests import custom_test_case
from models import payment
from tests.factories import Factory
import datetime

class PaymenttTests(custom_test_case.CustomTestCase):
  def test_saved_if_valid(self):
    p = Factory.build('payment')
    self.assertTrue(p.is_valid())
    self.assertTrue(p.save())

  def test_incoming_and_outgoing_can_filter_by_date(self):
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    tomorrow = today + datetime.timedelta(days=1)
    p1 = Factory.create('payment', {'done': 0, 'date': today})
    p2 = Factory.create('payment', {'done': 1, 'date': today})
    p3 = Factory.create('payment', {'done': 1, 'date': yesterday})
    p4 = Factory.create('payment', {'done': 0, 'date': tomorrow})
    p5 = Factory.create('payment', {'done': 0, 'date': yesterday})
    p6 = Factory.create('payment', {'done': 1, 'date': today})
    p7 = Factory.create('payment', {'done': 1, 'date': tomorrow})

    payments = payment.Payment.filter(yesterday,yesterday,done = 1)
    for p in [p3]: self.assertIn(p,payments)
    for p in [p1,p2,p4,p5,p6,p7]: self.assertNotIn(p,payments)
    
    payments = payment.Payment.filter(today,today,done = 1)
    for p in [p2,p6]: self.assertIn(p, payments)
    for p in [p1,p3,p4,p5,p7]: self.assertNotIn(p, payments)
    
    payments = map(lambda p: p.id, payment.Payment.filter(tomorrow,tomorrow,done = 1))
    self.assertEqual(payments, [p7.id])
    payments = map(lambda p: p.id, payment.Payment.filter(yesterday,today,done = 1))
    self.assertEqual(payments, [p3.id,p2.id,p6.id])
    payments = map(lambda p: p.id, payment.Payment.filter(yesterday,tomorrow,done = 1))
    self.assertEqual(payments, [p3.id,p2.id,p6.id,p7.id])
    payments = map(lambda p: p.id, payment.Payment.filter(today,tomorrow,done = 1))
    self.assertEqual(payments, [p2.id,p6.id,p7.id])
    payments = map(lambda p: p.id, payment.Payment.filter(yesterday,yesterday,done = 0))
    self.assertEqual(payments, [p5.id])
    payments = map(lambda p: p.id, payment.Payment.filter(today,today,done = 0))
    self.assertEqual(payments, [p1.id])
    payments = map(lambda p: p.id, payment.Payment.filter(tomorrow,tomorrow,done = 0))
    self.assertEqual(payments, [p4.id])
    payments = map(lambda p: p.id, payment.Payment.filter(yesterday,today,done = 0))
    self.assertEqual(payments, [p5.id,p1.id])
    payments = map(lambda p: p.id, payment.Payment.filter(yesterday,tomorrow,done = 0))
    self.assertEqual(payments, [p5.id,p1.id,p4.id])
    payments = map(lambda p: p.id, payment.Payment.filter(today,tomorrow, done = 0))
    self.assertEqual(payments, [p1.id,p4.id])

  def test_is_not_valid_if_amount_is_zero(self):
    p = Factory.build('payment', {'amount': 0})
    self.assertFalse(p.is_valid())
