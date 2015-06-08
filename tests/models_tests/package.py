from tests import custom_test_case
from models import klass
from models import package
from models import membership
from tests.factories import Factory

class PackageTests(custom_test_case.CustomTestCase):
  def _setUp(self):
    self.klass1 = Factory.create('klass', {'name': 'klass_1'})
    self.klass2 = Factory.create('klass', {'name': 'klass_2'})
    self.package = Factory.build('package')
    self.package.klasses = [self.klass1, self.klass2]
    self.package.save()

  def test_can_be_deleted(self):
    self.assertIs(self.package.can_delete(), True)

  def test_cannot_be_deleted_if_there_is_a_membership(self):
    u = Factory.create('student')
    m = membership.Membership.create({'klass_or_package': self.package, 'student': u})
    self.assertIsNot(self.package.can_delete(), True)
