
from model import Model
import installment

class Payment(Model):
  db = {1: {'amount': 200}, 2: {'amount': 100}, 3: {'amount': 100}}

  def __init__(self, attrs = {}):
    Model.__init__(self)
    self.amount = 0.00
    self.installment_id = None
    
    self.set_attrs(attrs)

  @property
  def installment(self, requery = False):
    if self.installment_id and (requery or self._installment is None):
      self._installment = installment.Installment.find(self.installment_id)
    return self._installment

