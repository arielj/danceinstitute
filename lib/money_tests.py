import unittest
from money import Money
from decimal import Decimal

class MoneyTests(unittest.TestCase):
  def test_instanciation(self):
    m = Money(1)
    self.assertEqual('1',str(m))

  def test_addition(self):
    m1 = Money(10.30)
    self.assertEqual('10,30', str(m1))
    m2 = Money('15,00')
    self.assertEqual('15', str(m2))

    m3 = m1+m2
    self.assertEqual('25,30',str(m3))
    self.assertIsInstance(m3, Money)
    
    m1 += m1
    self.assertEqual('20,60', str(m1))
    
    m4 = m2+'10,40'
    self.assertEqual('25,40',str(m4))
    
    m4 = m2+'10.70'
    self.assertEqual('25,70',str(m4))

  def test_r_addition(self):
    m1 = Money('10,40')
    s = 'hola '+m1
    self.assertEqual('hola 10,40', s)

unittest.main()
