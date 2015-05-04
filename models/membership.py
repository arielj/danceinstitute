#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from model import Model
from klass import Klass
from installment import Installment

class Membership(Model):
  #borrar después
  db = {1: {'student_id': 1, 'klass_id': 1, 'installment_ids': [1,2], 'year': 2015}}

  def __init__(self, data = {}):
    Model.__init__(self)
    self.student_id = None
    self.klass_id = None
    self.year = 2015
    self.type = 'normal'
    self.info = ''
    self.initial_month = 0
    self.final_month = 11
    self.date = ''
    self.fee = 0
    self.installment_ids = []
    self.installments = []
    
    self.set_attrs(data)

  def get_student(self, requery = False):
    return Student.find(self.student_id)

  def get_klass(self, requery = False):
    return Klass.find(self.klass_id)

  def get_installments(self, requery = False):
    return [Installment.find(1),Installment.find(2)]

  @classmethod
  def find(cls, id):
    return cls(memberships[id])

  @classmethod
  def get_types(cls):
    return {'normal': 'Normal', 'half': 'Mitad de clases', 'once': 'Una sola clase'}

  @classmethod
  def months(cls):
    return ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
