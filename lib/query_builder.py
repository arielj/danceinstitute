from database import Conn

class Query(object):
  def __init__(self, cls):
    self.cls = cls
    self.wheres = []
    self.values = {}
    self.query_result = None
    self.limit = None
    self.order = None
    self.offset = None

  def _do_query(self, force = False):
    if self.query_result is None or force is True:
      self.query_result = self.cls.get_many(self.query(), self.values)
    return self.query_result

  def __getitem__(self,index):
    return self._do_query()[index]

  def __contains__(self,item):
    ids = map(lambda i: i.id, self._do_query())
    
    if isinstance(item, list):
      found = all(map(lambda i: i.id in ids, item))
    else:
      found = item.id in ids

    self.query_result = None
    return found

  def query(self):
    q = 'SELECT * FROM ' + self.cls.table
    if self.wheres: q = q + self.get_wheres()
    if self.order is not None: q = q + ' ORDER BY %s' % self.order
    if self.offset is not None: q = q + ' OFFSET %i' % self.offset
    if self.limit is not None: q = q + ' LIMIT %i' % self.limit
    return q

  def where(self, field, value=None, comparission=None, placeholder=None):
    self.query_result = None

    if placeholder is None: placeholder = field

    if value is not None:
      if isinstance(value, dict):
        self.wheres.append("("+field+")")
        self.values.update(value)
      else:
        if isinstance(value, list):
          if comparission is None: comparission = 'IN'
          aux = '(:'+placeholder+')'
          value = ','.join(map(lambda v: str(v),value))

          
        else:
          if comparission is None: comparission = '='
          aux = ':'+placeholder

        self.wheres.append(field+" "+comparission+" "+aux)
        self.values[placeholder] = value
    else:
      self.wheres.append(field)

    return self

  def offset(self, off):
    self.query_result = None
    self.offset = off
    return self

  def order_by(self, order):
    self.query_result = None
    self.order = order
    return self

  def limit(self, limit):
    self.query_result = None
    self.limit = limit
    return self

  def get_wheres(self):
    return ' WHERE ' + ' AND '.join(self.wheres)

  def count(self):
    q = 'SELECT COUNT(*) FROM ' + self.cls.table
    if self.wheres: q = q + self.get_wheres()

    return Conn.execute(q, self.values).fetchone()[0]

  def exists(self):
    return self.cls.get_one() != None

  def anything(self):
    return self.count() > 0

  def do_get(self):
    return self._do_query(True)
