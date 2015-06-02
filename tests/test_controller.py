import unittest
from institute import Controller
from gui import home

class ControllerTests(unittest.TestCase):
  def setUp(self):
    self.ctrlr = Controller('test')

  def test_it_starts_with_home_page(self):
    self.assertIsInstance(self.ctrlr.current_page(), home.Home)

