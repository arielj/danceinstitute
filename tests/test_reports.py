from custom_test_case import CustomTestCase
from institute import Controller
from models import payment
from models import student
from factories import Factory
import gui

class PaymentsReportTest(CustomTestCase):
  
  def test_controller_opens_user_edit_when_signal(self):
    ctrlr = Controller('test')
    page = ctrlr.daily_payments(None)
    s = Factory.create('student')
    page.emit('student-edit',s.id)
    self.assertIsInstance(ctrlr.current_page(), gui.users.UserForm)
    self.assertEqual(ctrlr.current_page().object.id, s.id)

