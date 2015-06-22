from tests import custom_test_case
from models import installment
from tests.factories import Factory
import datetime
from lib.mock import Mock

class InstallmentTests(custom_test_case.CustomTestCase):
  def _setUp(self):
    self.student = Factory.create('student')
    self.klass = Factory.create('klass')
    self.membership = Factory.create('membership', {'student': self.student, 'klass_or_package': self.klass})

  #get_recharge
  def test_it_returns_zero_if_day_less_than_after_day(self):
    false_today = datetime.datetime.strptime('2015-01-10','%Y-%m-%d')
    installment.Installment._today = Mock(return_value=false_today)
    
    ins = Factory.create('installment', {'membership': self.membership, 'month': 0, 'year': 2015})
    self.assertEqual(ins.get_recharge(after_day = 10, recharge_value = '50'),0)
    
    false_today = datetime.datetime.strptime('2015-02-15','%Y-%m-%d')
    installment.Installment._today = Mock(return_value=false_today)
    
    ins = Factory.create('installment', {'membership': self.membership, 'month': 5, 'year': 2015})
    self.assertEqual(ins.get_recharge(after_day = 10, recharge_value = '50'),0)

  def test_it_returns_the_recharge_value_if_day_greater_than_after_day(self):
    false_today = datetime.datetime.strptime('2015-01-11','%Y-%m-%d')
    installment.Installment._today = Mock(return_value=false_today)
    
    ins = Factory.create('installment', {'membership': self.membership, 'month': 0, 'year': 2015, 'amount': 250})
    
    self.assertEqual(ins.get_recharge(after_day = 10, recharge_value = '50'),50)
    self.assertEqual(ins.get_recharge(after_day = 10, recharge_value = '10%'),25)
    
    false_today = datetime.datetime.strptime('2015-01-06','%Y-%m-%d')
    installment.Installment._today = Mock(return_value=false_today)

    ins = Factory.create('installment', {'membership': self.membership, 'month': 11, 'year': 2014, 'amount': 250})
    
    self.assertEqual(ins.get_recharge(after_day = 10, recharge_value = '50'),50)
    self.assertEqual(ins.get_recharge(after_day = 10, recharge_value = '10%'),25)

  #overdues
  def test_it_returns_overdue_installments(self):
    false_today = datetime.datetime.strptime('2015-01-10','%Y-%m-%d')
    installment.Installment._today = Mock(return_value=false_today)

    ins1 = Factory.create('installment', {'membership': self.membership, 'month': 0, 'year': 2015})
    ins2 = Factory.create('installment', {'membership': self.membership, 'month': 2, 'year': 2015})
    
    overdues = installment.Installment.overdues(10)
    self.assertNotIn(ins1, overdues)
    self.assertNotIn(ins2, overdues)

    false_today = datetime.datetime.strptime('2015-01-11','%Y-%m-%d')
    installment.Installment._today = Mock(return_value=false_today)

    overdues = installment.Installment.overdues(10)
    self.assertIn(ins1, overdues)
    self.assertNotIn(ins2, overdues)

    overdues = installment.Installment.overdues(12)
    self.assertNotIn(ins1, overdues)
    self.assertNotIn(ins2, overdues)

    false_today = datetime.datetime.strptime('2015-03-10','%Y-%m-%d')
    installment.Installment._today = Mock(return_value=false_today)
    
    overdues = installment.Installment.overdues(12)
    self.assertIn(ins1, overdues)
    self.assertNotIn(ins2, overdues)
    
    overdues = installment.Installment.overdues(10)
    self.assertIn(ins1, overdues)
    self.assertNotIn(ins2, overdues)

    overdues = installment.Installment.overdues(9)
    self.assertIn(ins1, overdues)
    self.assertIn(ins2, overdues)

  def test_it_can_filter_by_klass(self):
    false_today = datetime.datetime.strptime('2015-01-11','%Y-%m-%d')
    installment.Installment._today = Mock(return_value=false_today)

    self.klass2 = Factory.create('klass', {'name': 'Arabe'})
    self.membership2 = Factory.create('membership', {'student': self.student, 'klass_or_package': self.klass2})
    
    ins1 = Factory.create('installment', {'membership': self.membership, 'month': 0, 'year': 2015})
    ins2 = Factory.create('installment', {'membership': self.membership2, 'month': 0, 'year': 2015})

    overdues = installment.Installment.overdues(10)
    self.assertIn(ins1, overdues)
    self.assertIn(ins2, overdues)

    overdues = installment.Installment.overdues(10,klass=self.klass)
    self.assertIn(ins1, overdues)
    self.assertNotIn(ins2, overdues)
