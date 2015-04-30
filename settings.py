class Settings():
  _settings = None

  def __init__(self):
    self.language = 'es'
    self.startup_size = ''
    self.opening = '18:00'
    self.closing = '24:00'
    self.name = 'Instituto Superior de Danzas Sharife'

  def get_opening_h(self):
    return int(self.opening.split(':')[0])
  
  def get_closing_h(self):
    return int(self.closing.split(':')[0])

  @classmethod
  def get_settings(cls):
    return cls._settings or cls.load_settings()

  @classmethod
  def load_settings(cls):
    cls._settings = cls()
    return cls._settings

