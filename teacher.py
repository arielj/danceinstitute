class Teacher():
  def __init__(self):
    self.id = None
    self.name = ''
    self.lastname = ''
    self.dni = ''
    self.cellphone = ''
    self.birthday = ''
    self.address = ''
    self.male = True
  
  @classmethod
  def find(cls, teacher_id):
    teacher = Teacher()
    teacher.id = teacher_id
    teacher.name = 'Lau'
    teacher.lastname = 'Gut'
    teacher.dni = '35.592.392'
    teacher.cellphone = '0299-15-453-4315'
    teacher.birthday = '12/02/1991'
    teacher.address = '9 de Julio 1140'
    teacher.male = False
    return teacher
