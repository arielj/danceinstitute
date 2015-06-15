from tests import custom_test_case
from tests.factories import Factory

class StudentTests(custom_test_case.CustomTestCase):
  def test_dni_uniqueness(self):
    s = Factory.create('student', {'dni': '32496445'})
    self.assertTrue(s.is_valid())
    
    s2 = Factory.build('student', {'dni': s.dni})
    self.assertFalse(s2.is_valid())
    self.assertIn('dni', s2.errors)

  def test_cannot_be_deleted_if_has_memberships(self):
    s = Factory.create('student', {'dni': '32496446'})
    self.assertIs(s.can_delete(), True)
    m = Factory.create('membership', {'student': s})
    self.assertIsNot(s.can_delete(), True)
    
    s = Factory.create('student', {'dni': '32496447'})
    self.assertIs(s.can_delete(), True)
    p = Factory.create('payment', {'user': s})
    self.assertIsNot(s.can_delete(), True)
