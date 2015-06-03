import unittest
from institute import Controller
from models import payment
import factories
import gui

class PaymentsReportTest(unittest.TestCase):
  
  def test_double_click_row_opens_user_edit(self):
    s = factories.create_student()
    p = factories.create_payment({'student_id': s.id})
    ctrlr = Controller('test')
    page = ctrlr.daily_payments(None)
    page.emit('student-edit',s.id)
    self.assertIsInstance(ctrlr.current_page(), gui.users.UserForm)
    self.assertEqual(ctrlr.current_page().object.id, s.id)
