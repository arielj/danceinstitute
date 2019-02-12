#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
import getopt
import pygtk
import tempfile
import webbrowser
import re
import datetime
import constants
from database import Conn
from gui import *
from settings import Settings
from models import *
import translations
import exporter

def order_fees(fee):
  return float(fee)

def main(argv):
  env = 'dev'
  try:
    opts, args = getopt.getopt(argv,"e:",["env="])
    for opt, arg in opts:
      if opt in ('-e', '--env'):
        env = arg
  except getopt.GetoptError:
    print "args error"
  Conn.start_connection(env)
  print("Nombre;Apellido;Horas x semana;Valor última cuota (sumando xHora y extra);Clases;Clases extra")
  ks_count = {}
  for s in Student.where({'inactive': False, 'is_teacher': 0}):
    h = 0
    i = 0
    ks = []
    ks2 = []
    ms = Membership.for_student(s.id).do_get()
    if ms != []:
      m = ms[0]
      for k in m.klasses():
        if not ks_count.has_key(k.name):
          ks_count[k.name] = 0
        ks_count[k.name] = ks_count[k.name]+1
        if k.normal_fee > 0:
          ks2.append(k.name)
        else:
          ks.append(k.name)
          h += k.get_duration()
      ins = m.installments.do_get()
      if ins != []:
        i = i+ins[-1].amount
    ks = " - ".join(ks)
    ks2 = " - ".join(ks2)

    print('{};{};{};{};{};{}'.format(s.name, s.lastname, h, i, ks, ks2))


  for k in ks_count.keys():
    n = k
    st = ks_count[k]
    print('{};{}'.format(n,st))

if __name__ == "__main__":
  main(sys.argv[1:])
