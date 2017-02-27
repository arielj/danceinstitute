from database import Conn
import json

class Settings(object):
  _settings = None

  def __init__(self):
    self.language = 'en'
    self.startup_size = ''
    self.opening = '09:00'
    self.closing = '24:00'
    self.name = ''
    self.tabs_position = 'top'
    self._recharge_after = 0
    self.recharge_value = 0
    self.second_recharge_value = 0
    self.notes = ''
    self._export_path = ''
    self.date_format = '%Y-%m-%d'
    self.fees = {}
    self._use_hour_fees = '0'
    self._installments_from = 0
    self._installments_to = 11

  @property
  def export_path(self):
    return self._export_path or None

  @export_path.setter
  def export_path(self, value):
    self._export_path = value

  @property
  def recharge_after(self):
    return self._recharge_after

  @recharge_after.setter
  def recharge_after(self, value):
    try:
      self._recharge_after = int(value)
    except:
      self._recharge_after = 10

  @property
  def installments_from(self):
    return self._installments_from

  @installments_from.setter
  def installments_from(self, value):
    try:
      self._installments_from = int(value)
    except:
      self._installments_from = 0

  @property
  def installments_to(self):
    return self._installments_to

  @installments_to.setter
  def installments_to(self, value):
    try:
      self._installments_to = int(value)
    except:
      self._installments_to = 11

  @property
  def use_hour_fees(self):
    return self._use_hour_fees == '1'

  @use_hour_fees.setter
  def use_hour_fees(self, value):
    if type(value) == int: self._use_hour_fees = '1' if value == 1 else '0'
    elif type(value) == str: self._use_hour_fees = '1' if value == '1' or value == 'True' else '0'
    elif type(value) == bool: self._use_hour_fees = '1' if value else '0'
    else: self._use_hour_fees = '0'

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
      if r['key'] == 'fees':
        setattr(cls._settings,r['key'], json.loads(r['value']))
      else:
        setattr(cls._settings,r['key'], r['value'])

    return cls._settings

  def set_values(self, data):
    for k in data:
      setattr(self,k,data[k])

  def save(self):
    for k in vars(self):
      if k.startswith('_'): k = k.replace('_','',1)
      v = json.dumps(getattr(self, k)) if k == 'fees' else None
      if k == 'use_hour_fees': v = getattr(self, '_use_hour_fees')
      if k == 'installments_from': v = getattr(self, '_installments_from')
      if k == 'installments_to': v = getattr(self, '_installments_to')

      self.save_attr(k, v)

    return True

  def save_attr(self, k, value = None):
    if value is None: value = getattr(self, k)
    Conn.execute('UPDATE settings SET value=:value WHERE `key`=:key', {'key': k, 'value': value})

  @classmethod
  def get_fee_for(cls, k):
    return cls.get_settings().fees[k]
