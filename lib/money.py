from decimal import Decimal, InvalidOperation

def convert_to_cents(amount):
  c = 0
  if isinstance(amount, Money):
    c = amount._cents
  elif isinstance(amount, int):
    c = amount*100
  elif isinstance(amount, float):
    c = int(amount*100)
  elif isinstance(amount, str):
    amount = amount.replace(',','.')
    try:
      d = Decimal(amount)
      c = int(d*100)
    except InvalidOperation:
      raise InvalidOperation
  elif isinstance(amount, Decimal):
    c = int(amount*100)
  else:
    raise InvalidOperation
  
  return c

class Money(object):
  def __init__(self, amount):
    self._cents = convert_to_cents(amount)

  def __str__(self):
    s = str(self._cents)
    v = s[:-2]+','+s[-2:]
    v = v[0:-3] if v.endswith(',00') else v
    if v.startswith(','): v = '0' + v
    return v

  def __add__(self, other):
    return Money(Decimal(self._cents + convert_to_cents(other))/100)

  def __sub__(self, other):
    return Money(Decimal(self._cents - convert_to_cents(other))/100)

  def __iadd__(self, other):
    self._cents = (self+other)._cents
    return self

  def __radd__(self, other):
    return other+str(self)

  def __int__(self):
    return self._cents/100
