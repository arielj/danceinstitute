import datetime
from models import student
from models import payment

def create_student(attrs = {}):
  data = {'name': 'Arielo', 'lastname': 'Juodziukynas', 'is_teacher': 0}
  for attr in attrs:
    data[attr] = attrs[attr]

  s = student.Student(data)
  s.save()
  return s

def create_payment(attrs = {}):
  data = {'description': 'Cuota loca', 'amount': 200, 'date': str(datetime.datetime.today())}
  for attr in attrs:
    data[attr] = attrs[attr]

  p = payment.Payment(data)
  p.save()
  return p
