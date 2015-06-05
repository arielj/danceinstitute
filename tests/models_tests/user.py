from tests import custom_test_case
from tests.factories import Factory

class StudentTests(custom_test_case.CustomTestCase):
  def test_dni_uniqueness(self):
    s = Factory.create('student', {'dni': '32496445'})
    self.assertTrue(s.is_valid())
    
    s2 = Factory.build('student', {'dni': s.dni})
    self.assertFalse(s2.is_valid())
    self.assertIn('dni', s2.errors)

