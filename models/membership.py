from model import Model
from klass import Klass
from installment import Installment

memberships = {1: {'student_id': 1, 'klass_id': 1, 'installment_ids': [1,2]}}

class Membership(Model):
  def __init__(self, data = {}):
    Model.__init__(self)
    self.student_id = None
    self.klass_id = None
    self.installment_ids = []
    self.installments = []
    
    self.set_attrs(data)

  def get_student(self, requery = False):
    return Student.find(self.student_id)

  def get_klass(self, requery = False):
    return Klass.find(self.klass_id)

  def get_installments(self, requery = False):
    return [Installment.find(1),Installment.find(2)]

  @classmethod
  def find(cls, id):
    return cls(memberships[id])
