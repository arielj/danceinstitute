from model import Model

class Room(Model):
  table = 'rooms'
  
  def __init__(self,data={}):
    self.name = ''
    Model.__init__(self,data)
