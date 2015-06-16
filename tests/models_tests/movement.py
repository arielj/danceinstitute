from tests import custom_test_case
from models import movement
from tests.factories import Factory
import datetime

class MovementTests(custom_test_case.CustomTestCase):
  def test_movement_can_be_outgoing(self):
    mov = movement.Movement({'direction': 'out'})
    self.assertTrue(mov.is_outgoing())

  def test_movement_can_be_incoming(self):
    mov = movement.Movement({'direction': 'in'})
    self.assertTrue(mov.is_incoming())

  def test_movement_cannot_be_out_and_in_at_the_same_time(self):
    mov = movement.Movement({'direction': 'in'})
    self.assertTrue(mov.is_incoming())
    self.assertFalse(mov.is_outgoing())
    
    mov = movement.Movement({'direction': 'out'})
    self.assertFalse(mov.is_incoming())
    self.assertTrue(mov.is_outgoing())

  def test_saved_if_valid(self):
    mov = Factory.build('movement')
    self.assertTrue(mov.is_valid())
    self.assertTrue(mov.save())

  def test_incoming_returns_only_incoming_movements(self):
    mv1 = Factory.create('movement', {'direction': 'in'})
    mv2 = Factory.create('movement', {'direction': 'out'})
    mv3 = Factory.create('movement', {'direction': 'out'})
    mv4 = Factory.create('movement', {'direction': 'in'})
    incoming = movement.Movement.incoming()
    self.assertIn(mv1,incoming)
    self.assertNotIn(mv2,incoming)
    self.assertNotIn(mv3,incoming)
    self.assertIn(mv4,incoming)

  def test_incoming_returns_only_incoming_movements(self):
    mv1 = Factory.create('movement', {'direction': 'in'})
    mv2 = Factory.create('movement', {'direction': 'out'})
    mv3 = Factory.create('movement', {'direction': 'out'})
    mv4 = Factory.create('movement', {'direction': 'in'})
    outgoing = movement.Movement.outgoing()
    self.assertNotIn(mv1,outgoing)
    self.assertIn(mv2,outgoing)
    self.assertIn(mv3,outgoing)
    self.assertNotIn(mv4,outgoing)

  def test_incoming_and_outgoing_can_filter_by_date(self):
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    tomorrow = today + datetime.timedelta(days=1)
    mv1 = Factory.create('movement', {'direction': 'in', 'date': today})
    mv2 = Factory.create('movement', {'direction': 'out', 'date': today})
    mv3 = Factory.create('movement', {'direction': 'out', 'date': yesterday})
    mv4 = Factory.create('movement', {'direction': 'in', 'date': tomorrow})
    mv5 = Factory.create('movement', {'direction': 'in', 'date': yesterday})
    mv6 = Factory.create('movement', {'direction': 'out', 'date': today})
    mv7 = Factory.create('movement', {'direction': 'out', 'date': tomorrow})
    outgoing = map(lambda m: m.id, movement.Movement.outgoing(yesterday))
    self.assertEqual(outgoing, [mv3.id])
    outgoing = map(lambda m: m.id, movement.Movement.outgoing(today))
    self.assertEqual(outgoing, [mv2.id,mv6.id])
    outgoing = map(lambda m: m.id, movement.Movement.outgoing(tomorrow))
    self.assertEqual(outgoing, [mv7.id])
    outgoing = map(lambda m: m.id, movement.Movement.outgoing(yesterday,today))
    self.assertEqual(outgoing, [mv2.id,mv3.id,mv6.id])
    outgoing = map(lambda m: m.id, movement.Movement.outgoing(yesterday,tomorrow))
    self.assertEqual(outgoing, [mv2.id,mv3.id,mv6.id,mv7.id])
    outgoing = map(lambda m: m.id, movement.Movement.outgoing(today,tomorrow))
    self.assertEqual(outgoing, [mv2.id,mv6.id,mv7.id])
    incoming = map(lambda m: m.id, movement.Movement.incoming(yesterday))
    self.assertEqual(incoming, [mv5.id])
    incoming = map(lambda m: m.id, movement.Movement.incoming(today))
    self.assertEqual(incoming, [mv1.id])
    incoming = map(lambda m: m.id, movement.Movement.incoming(tomorrow))
    self.assertEqual(incoming, [mv4.id])
    incoming = map(lambda m: m.id, movement.Movement.incoming(yesterday,today))
    self.assertEqual(incoming, [mv1.id,mv5.id])
    incoming = map(lambda m: m.id, movement.Movement.incoming(yesterday,tomorrow))
    self.assertEqual(incoming, [mv1.id,mv4.id,mv5.id])
    incoming = map(lambda m: m.id, movement.Movement.incoming(today,tomorrow))
    self.assertEqual(incoming, [mv1.id,mv4.id])

  def test_is_not_valid_if_amount_is_zero(self):
    mov = Factory.build('movement', {'amount': 0})
    self.assertFalse(mov.is_valid())
