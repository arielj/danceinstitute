import datetime
from models import student
from models import payment

def build_student(attrs = {}):
  data = {'name': 'Arielo', 'lastname': 'Juodziukynas', 'is_teacher': 0}
  data.update(attrs)
  return student.Student(data)

def create_student(attrs = {}):
  s = build_student(attrs)
  s.save()
  s.__class__.get_conn().commit()
  return s

def build_payment(attrs = {}):
  data = {'description': 'Cuota loca', 'amount': 200, 'date': str(datetime.datetime.today())}
  data.update(attrs)
  return payment.Payment(data)

def create_payment(attrs = {}):
  p = build_payment(attrs)
  p.save()
  p.__class__.get_conn().commit()
  return p
