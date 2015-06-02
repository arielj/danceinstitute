import custom_test_case
from gui import SearchStudent, SearchForm, StudentsList
import gtk

class StudentsSearchTests(custom_test_case.CustomTestCase):
  def _setUp(self):
    self.widget = SearchStudent()

  def test_it_has_the_search_form(self):
    self.assertIsInstance(self.widget.form, SearchForm)

  def test_tab_label(self):
    self.assertEqual(self.widget.get_tab_label(), 'Buscar alumno/a')

  def test_it_has_the_restults_list(self):
    self.assertIsInstance(self.widget.results, StudentsList)

class StudentsSearchFormTests(custom_test_case.CustomTestCase):
  def _setUp(self):
    self.widget = SearchForm()

  def test_it_has_an_entry_field(self):
    self.assertIsInstance(self.widget.entry, gtk.Entry)
