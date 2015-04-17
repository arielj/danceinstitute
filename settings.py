class Settings():
  _settings = None

  def __init__(self):
    self.language = 'es'
    self.startup_size = ''

  @classmethod
  def get_settings(cls):
    return cls._settings or cls.load_settings()

  @classmethod
  def load_settings(cls):
    cls._settings = cls()
    return cls._settings

