from database import Conn

class Settings(object):
  _settings = None

  def __init__(self):
    self.language = 'en'
    self.startup_size = ''
    self.opening = '09:00'
    self.closing = '24:00'
    self.name = ''
    self.tabs_position = 'top'
    self.recharge_after = 0
    self.recharge_value = 0

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
    for r in Conn.execute('SELECT * FROM settings').fetchall():
      setattr(cls._settings,r['key'],r['value'])
    return cls._settings

  def set_values(self, data):
    for k in data:
      setattr(self,k,data[k])

  def save(self):
    for k in vars(self):
      Conn.execute('UPDATE settings SET value=:value WHERE key=:key', {'key': k, 'value': getattr(self,k)})
    return True
