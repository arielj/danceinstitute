
from model import Model
from student import Student

class Payment(Model):
  def __init__(self):
    Model.__init__(self)
    self.amount = 0.00
    self.user_id = None
    self.installment_id = None
    
