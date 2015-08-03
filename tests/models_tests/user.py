from tests import custom_test_case
from tests.factories import Factory
from models.student import Student

class StudentTests(custom_test_case.CustomTestCase):
  def test_dni_uniqueness(self):
    s = Factory.create('student')
    s.is_valid()
    self.assertTrue(s.is_valid())
    
    s2 = Factory.build('student', {'dni': s.dni})
    self.assertFalse(s2.is_valid())
    self.assertIn('dni', s2.errors)

  def test_cannot_be_deleted_if_has_memberships(self):
    s = Factory.create('student')
    self.assertIs(s.can_delete(), True)
    m = Factory.create('membership', {'student': s})
    self.assertIsNot(s.can_delete(), True)
    
    s = Factory.create('student')
    self.assertIs(s.can_delete(), True)
    p = Factory.create('payment', {'user': s})
    self.assertIsNot(s.can_delete(), True)
  
  def test_adds_family_members(self):
    s1 = Factory.create('student', {'name': 'Alumno1'})
    s2 = Factory.create('student', {'name': 'Alumno2'})
    s3 = Factory.create('student', {'name': 'Alumno3'})
    s1.add_family_member(s2)
    self.assertEqual(s1.family, s1.id)
    self.assertEqual(s1.family, s2.family)
    s2.add_family_member(s3)
    self.assertEqual(s1.family, s3.family)

  def test_removes_family_members(self):
    s1 = Factory.create('student', {'name': 'AlumnoUno'})
    s2 = Factory.create('student', {'name': 'AlumnoDos'})
    s3 = Factory.create('student', {'name': 'AlumnoTres'})
    s1.add_family_member(s2)
    s1.add_family_member(s3)
    self.assertIn(s2, s1.family_members())
    self.assertIn(s3, s1.family_members())
    s1.remove_family_member(s2)
    self.assertNotIn(s2, s1.family_members())
    self.assertIn(s3, s1.family_members())
    s3.remove_family_member(s1)
    self.assertNotIn(s2, s1.family_members())
    self.assertNotIn(s3, s1.family_members())
    self.assertIs(s1.family, None)

