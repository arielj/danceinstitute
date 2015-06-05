from tests import custom_test_case
from models import klass
from models import schedule
from tests.factories import Factory

class KlassTests(custom_test_case.CustomTestCase):
  def _setUp(self):
    self.klass = Factory.create('klass')

  def test_can_be_deleted(self):
    self.assertIs(self.klass.delete(), True)
    
  def test_cannot_be_deleted_if_a_package_uses_it(self):
    k2 = Factory.create('klass')
    p = Factory.create('package', {'klasses': [self.klass,k2]})
    self.assertIsNot(self.klass.delete(), True)

  def test_cannot_be_deleted_if_a_membership_uses_it(self):
    s = Factory.create('student')
    m = Factory.create('membership', {'student': s, 'klass_or_package': self.klass})
    self.assertIsNot(self.klass.delete(), True)

  def test_deletes_its_schedules(self):
    r = Factory.create('room')
    s = Factory.build('schedule', {'room': r})
    self.klass.add_schedule(s)
    self.klass.delete()
    self.assertIs(schedule.Schedule.find(s.id), False)

  def test_deletes_teachers_associations(self):
    t = Factory.create('teacher')
    self.klass.add_teacher(t)
    self.klass.save()
    self.assertEqual(self._count_teachers_for_klass(self.klass.id), 1)
    self.klass.delete()
    self.assertEqual(self._count_teachers_for_klass(self.klass.id), 0)

  def _count_teachers_for_klass(self, k_id):
    return klass.Klass.get_conn().execute('SELECT COUNT(*) FROM klasses_teachers WHERE klass_id = :klass_id', {'klass_id': k_id}).fetchone()[0]
