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

  def __getitem__(self,index):
    if self.query_result is None:
      self.query_result = self.cls.get_many(self.query(), self.values)
    return self.query_result[index]

  def __contains__(self,item):
    if self.query_result is None:
      self.query_result = self.cls.get_many(self.query(), self.values)
    found = item.id in map(lambda i: i.id, self.query_result)
    self.query_result = None
    return found

  def query(self):
    q = 'SELECT * FROM ' + self.cls.table
    if self.wheres: q = q + self.get_wheres()
    if self.order is not None: q = q + ' ORDER BY %s' % self.order
    if self.offset is not None: q = q + ' OFFSET %i' % self.offset
    if self.limit is not None: q = q + ' LIMIT %i' % self.limit
    return q

  def where(self, field, value = None, comparission = '=', placeholder = None):
    self.query_result = None
    if placeholder is None: placeholder = ':'+field
    aux_placeholder = placeholder[1:]
    if value is not None:
      self.wheres.append("%s %s %s" % (field, comparission, placeholder))
      self.values[aux_placeholder] = value
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
    self.query_result = self.cls.get_many(self.query(), self.values)
    return self.query_result
