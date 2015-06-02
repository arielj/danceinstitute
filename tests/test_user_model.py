import custom_test_case
from models import student

class StudentTests(custom_test_case.CustomTestCase):
  def test_dni_uniqueness(self):
    u = student.Student.find_by('dni', '32496445')
    self.assertTrue(u.is_valid())
    u = student.Student({'dni': 32496445})
    self.assertFalse(u.is_valid())
    self.assertIn('dni', u.errors)

