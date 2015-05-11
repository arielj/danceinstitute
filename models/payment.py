from decimal import Decimal
from model import Model
import installment
import student

class Payment(Model):
  table = 'payments'
  fields_for_save = ['amount','installment_id','student_id','date']

  def __init__(self, attrs = {}):
    self._amount = 0
    self.installment_id = None
    self._installment = None
    self.student_id = None
    self._student = None
    self._date = None
    Model.__init__(self, attrs)

  @property
  def amount(self):
    return self._amount/100

  @amount.setter
  def amount(self,value):
    try:
      v = int(Decimal(value)*100)
    except:
      v = 0
    self._amount = v

  @property
  def student(self):
    if self.student_id and self._student is None:
      self._student = student.Student.find(self.student_id)
    return self._student
    
  @student.setter
  def student(self, st):
    if st is None:
      self.student_id = None
    else:
      self.student_id = st.id
    self._student = st

  @property
  def installment(self):
    if self.installment_id and self._installment is None:
      self._installment = installment.Installment.find(self.installment_id)
    return self._installment

  @installment.setter
  def installment(self, ins):
    if ins is None:
      self.installment_id = None
    else:
      self.installment_id = ins.id
    self._installment = ins

  @property
  def date(self):
    return self._date

  @property
  def date(self,value):
    try:
      self._date = datetime.datetime.strptime(value,'%Y/%m/%d').date()
    except:
      try:
        self._date = datetime.datetime.strptime(value,'%Y/%d/%m').date()
      except:
        try:
          self._date = datetime.datetime.strptime(value,'%Y-%m-%d').date()
        except:
          try:
            self._date = datetime.datetime.strptime(value,'%Y-%d-%m').date()
          except:
            try:
              self._date = datetime.datetime.strptime(value,'%d-%m-%Y').date()
            except:
              try:
                self._date = datetime.datetime.strptime(value,'%d/%m/%Y').date()
              except:
                self._date = ''

  def _is_valid(self):
    self.validate_numericallity_of('amount', great_than = 0, only_integer = False)

  def to_db(self):
    return {'amount': self.amount, 'date': self.date, 'installment_id': self.installment_id, 'student_id': self.student_id}

  def to_s(self):
    return str(self.date) + ": $" + str(self.amount)

  @classmethod
  def for_installment(cls,ins_id):
    return cls.get_where('installment_id',ins_id)
