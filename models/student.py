from user import User
from membership import Membership

class Student(User):
  def __init__(self, data = {}):
    self.memberships = []
    self.membership_ids = []
    User.__init__(self, data)

  @classmethod
  def search(cls, value):
    if value == 'Lau':
      return [cls.find(1)]
    elif value == 'Tincho':
      return [cls.find(2)]
    elif value == 'Prof':
      return [cls.find(1),cls.find(2)]
    else:
      return []

  def get_memberships(self, requery = False):
    if requery or not self.memberships:
      self.memberships = []
      for id in self.membership_ids:
        self.memberships.append(Membership.find(id))
    return self.memberships

