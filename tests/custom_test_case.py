import unittest
import database

class CustomTestCase(unittest.TestCase):
  def setUp(self):
    database.Conn.start_connection('test')
    self._setUp()

  def _setUp(self):
    pass
