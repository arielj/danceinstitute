from tests import custom_test_case
from models import installment
from tests.factories import Factory
import datetime
from lib.mock import Mock

class InstallmentTests(custom_test_case.CustomTestCase):
  def _setUp(self):
    self.student = Factory.create('student')
    self.membership = Factory.create('membership', {'student': self.student})

  #get_recharge
  def test_it_returns_zero_if_day_less_than_after_day(self):
    false_today = datetime.datetime.strptime('2015-01-10','%Y-%m-%d').date()
    installment.Installment._today = Mock(return_value=false_today)
    
    ins = Factory.create('installment', {'membership': self.membership, 'month': 0, 'year': 2015})
    self.assertEqual(ins.get_recharge(after_day = 10, recharge_value = '50'),0)
    
    false_today = datetime.datetime.strptime('2015-02-15','%Y-%m-%d').date()
    installment.Installment._today = Mock(return_value=false_today)
    
    ins = Factory.create('installment', {'membership': self.membership, 'month': 5, 'year': 2015})
    self.assertEqual(ins.get_recharge(after_day = 10, recharge_value = '50'),0)

  def test_it_returns_the_recharge_value_if_day_greater_than_after_day(self):
    false_today = datetime.datetime.strptime('2015-01-11','%Y-%m-%d').date()
    installment.Installment._today = Mock(return_value=false_today)
    
    ins = Factory.create('installment', {'membership': self.membership, 'month': 0, 'year': 2015, 'amount': 250})
    
    self.assertEqual(ins.get_recharge(after_day = 10, recharge_value = '50'),50)
    self.assertEqual(ins.get_recharge(after_day = 10, recharge_value = '10%'),25)
    
    false_today = datetime.datetime.strptime('2015-01-06','%Y-%m-%d').date()
    installment.Installment._today = Mock(return_value=false_today)

    ins = Factory.create('installment', {'membership': self.membership, 'month': 11, 'year': 2014, 'amount': 250})
    
    self.assertEqual(ins.get_recharge(after_day = 10, recharge_value = '50'),50)
    self.assertEqual(ins.get_recharge(after_day = 10, recharge_value = '10%'),25)

