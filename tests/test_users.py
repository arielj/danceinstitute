import unittest
import database
from models import student

class StudentTests(unittest.TestCase):
  def setUp(self):
    database.Conn.start_connection('test')

  def test_dni_uniqueness(self):
    u = student.Student.find_by('dni', '32496445')
    self.assertTrue(u.is_valid())
    u = student.Student({'dni': 32496445})
    self.assertFalse(u.is_valid())
    self.assertIn('dni', u.errors)

