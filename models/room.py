from model import Model

class Room(Model):
  table = 'rooms'
  fields_for_save = ['name']

  def __init__(self,data={}):
    self.name = ''
    Model.__init__(self,data)

  def _is_valid(self):
    self.validate_presence_of('name')

  def to_db(self):
    return {'name': self.name}

