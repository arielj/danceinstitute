from database import Conn

class Query(object):
  def __init__(self, cls):
    self.cls = cls
    self.wheres = []
    self.values = {}
    self.query_result = None
    self.limit = None
    self.order = cls.default_order
    self.offset = None
    self.select_str = cls.table+'.*'
    self.from_str = cls.table
    self.join_str = None

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

  def __getattr__(self,name):
    return getattr(self.cls,name)

  def __str__(self):
    st = str(map(lambda m: str(m), self._do_query()))
    self.query_result = None
    return st

  def __len__(self):
    return len(self._do_query())

  def query(self):
    q = 'SELECT '+self.select_str+' FROM ' + self.from_str
    if self.join_str: q = q + ' ' + self.join_str
    if self.wheres: q = q + self.get_wheres()
    if self.order is not None: q = q + ' ORDER BY "%s"' % self.order
    if self.limit is not None: q = q + ' LIMIT %i' % self.limit
    if self.offset is not None: q = q + ' OFFSET %i' % self.offset
    return q

  def where(self, field, value=None, comparission=None, placeholder=None):
    if isinstance(field,dict):
      for f in field:
        self.where(f,field[f])
    else:
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
            value = ','.join(map(lambda v: str(v), value))
          else:
            if comparission is None: comparission = '='
            aux = ':'+placeholder
          
          table_field = field.split('.')
          field = '.'.join(map(lambda x: self._fix_field(x), table_field))
          
          self.wheres.append(field+" "+comparission+" "+aux)
          self.values[placeholder] = value
      else:
        self.wheres.append(field)

    return self

  def set_offset(self, off):
    self.query_result = None
    self.offset = off
    return self

  def order_by(self, order):
    self.query_result = None
    self.order = order
    return self

  def set_limit(self, limit):
    self.query_result = None
    self.limit = limit
    return self

  def set_join(self, j):
    self.query_result = None
    self.join_str = j
    return self

  def set_select(self, s):
    self.query_result = None
    self.select_str = s
    return self

  def set_from(self, f):
    self.query_result = None
    self.from_str = f
    return self

  def get_wheres(self):
    return ' WHERE ' + ' AND '.join(self.wheres)

  def count(self):
    q = 'SELECT COUNT(*) FROM ' + self.from_str
    if self.join_str: q = q + ' ' + self.join_str
    if self.wheres: q = q + self.get_wheres()

    return Conn.execute_plain(q, self.values).fetchone()[0]

  def exists(self):
    return self.cls.get_one(self.query(),self.values) != None

  def anything(self):
    return self.count() > 0

  def empty(self):
    return self.count() == 0

  def do_get(self):
    return self._do_query(True)

  def all(self):
    return self

  def first(self):
    return self.cls.get_one(self.query(), self.values)
  
  def delete_all(self):
    q = 'DELETE FROM ' + self.from_str
    if self.wheres: q = q + self.get_wheres()
    if self.limit is not None: q = q + ' LIMIT %i' % self.limit
    return Conn.execute_plain(q, self.values)

  def _fix_field(self, f):
    f =  f if f.startswith('`') else "`"+f+"` "
    return f
