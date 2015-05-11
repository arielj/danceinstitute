#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import datetime

class Conn(object):
  _conn = sqlite3.connect(":memory:")
  _conn.row_factory = sqlite3.Row

  CREATE = {'settings': '''CREATE TABLE settings (key text, value text)''',
            'installments': '''CREATE TABLE installments (id integer primary key, year integer, month integer, membership_id integer, amount integer)''',
            'payments': '''CREATE TABLE payments (id integer primary key, date date, amount integer, installment_id integer, student_id integer)''',
            'rooms': '''CREATE TABLE rooms (name text)''',
            'memberships': '''CREATE TABLE memberships (id integer primary key, student_id integer, for_id integer, for_type text, info text)''',
            'schedules': '''CREATE TABLE schedules (id integer primary key, klass_id integer, from_time integer, to_time integer, room text, day integer)''',
            'users': '''CREATE TABLE users (id integer primary key, name text, lastname text, dni string, cellphone text, alt_phone text, birthday date, address text, male integer, email text, is_teacher integer, comments text default '')''',
            'klasses': '''CREATE TABLE klasses (id integer primary key, name text, normal_fee integer, half_fee integer, once_fee integer, inscription_fee integer, min_age integer, max_age integer, quota integer, info text)''',
            'klasses_teachers': '''CREATE TABLE klasses_teachers (klass_id integer, teacher_id integer)''',
            'packages': '''CREATE TABLE packages (id integer primary key, name text, fee integer, alt_fee integer)''',
            'klasses_packages': '''CREATE TABLE klasses_packages (klass_id integer, package_id integer)'''
           }

  @classmethod
  def create_tables(cls):
    cls.create('settings')
    cls.create('installments')
    cls.create('payments')
    cls.create('rooms')
    cls.create('memberships')
    cls.create('schedules')
    cls.create('klasses')
    cls.create('users')
    cls.create('packages')
    cls.create('klasses_teachers')
    cls.create('klasses_packages')
    cls.seed()
    cls.commit()

  @classmethod
  def create(cls, table):
    cls._conn.execute(cls.CREATE[table])

  @classmethod
  def seed(cls):
    cls.execute('''INSERT INTO rooms (name) VALUES ('Agua')''')
    cls.execute('''INSERT INTO rooms (name) VALUES ('Aire')''')
    cls.execute('''INSERT INTO rooms (name) VALUES ('Fuego')''')
    cls.execute('''INSERT INTO installments (year, month, amount, membership_id) VALUES (2015, 4, 300, 1)''')
    cls.execute('''INSERT INTO installments (year, month, amount, membership_id) VALUES (2015, 5, 300, 1)''')
    cls.execute('''INSERT INTO payments (date, amount, installment_id, student_id) VALUES (?, 200, 1, 1)''',(datetime.date(2015,3,3),))
    cls.execute('''INSERT INTO payments (date, amount, installment_id, student_id) VALUES (?, 100, 1, 1)''',(datetime.date(2015,3,4),))
    cls.execute('''INSERT INTO payments (date, amount, installment_id, student_id) VALUES (?, 100, 2, 1)''',(datetime.date(2015,3,1),))
    cls.execute('''INSERT INTO memberships (student_id, for_id, for_type, info) VALUES (3, 1, 'Klass', 'Clase normal lalala')''')
    cls.execute('''INSERT INTO schedules (klass_id, from_time, to_time, room, day) VALUES (1, 2000, 2130, 'Fuego', 0)''')
    cls.execute('''INSERT INTO schedules (klass_id, from_time, to_time, room, day) VALUES (1, 2000, 2130, 'Fuego', 3)''')
    cls.execute('''INSERT INTO schedules (klass_id, from_time, to_time, room, day) VALUES (2, 1900, 2030, 'Aire', 1)''')
    cls.execute('''INSERT INTO schedules (klass_id, from_time, to_time, room, day) VALUES (2, 1900, 2030, 'Aire', 3)''')
    cls.execute('''INSERT INTO users (name, lastname, dni, cellphone, birthday, address, male, email, is_teacher) VALUES ('Lau', 'Gut', '35592392', '0299-15-453-4315', '1991-02-12', '9 de Julio 1140', 0, 'lali_gut@yahoo.com.ar', 1)''')
    cls.execute('''INSERT INTO users (name, lastname, dni, cellphone, birthday, address, male, email, is_teacher) VALUES ('Tincho', 'Arce', '11111111', 'nose', '1981-02-12', 'Barrio mercantil', 1, 'tincho@sharife.com.ar', 1)''')
    cls.execute('''INSERT INTO users (name, lastname, dni, cellphone, birthday, address, male, email, is_teacher) VALUES ('Ariel', 'Juod', '32496445', '0299-15-411-5106', '1986-07-18', '9 de Julio 1140', 1, 'arieljuod@gmail.com', 0)''')
    cls.execute('''INSERT INTO klasses (name, normal_fee, half_fee, once_fee, inscription_fee, min_age, max_age, quota, info) VALUES ('Flamenco Adultos', 350, 200, 50, 0, 15, 0, 15, 'Traer zapatos con taco ancho y una pollera larga.')''')
    cls.execute('''INSERT INTO klasses (name, normal_fee, half_fee, once_fee, inscription_fee, min_age, max_age, quota, info) VALUES ('HipHop Adolescentes', 300, 200, 30, 0, 13, 22,30, 'Zapatillas y ropa cómoda')''')
    cls.execute('''INSERT INTO klasses_teachers (klass_id, teacher_id) VALUES (1,1)''')
    cls.execute('''INSERT INTO klasses_teachers (klass_id, teacher_id) VALUES (2,2)''')
    cls.execute('''INSERT INTO packages (name, fee, alt_fee) VALUES ('Paquete A', 500, 350)''')
    cls.execute('''INSERT INTO klasses_packages (klass_id, package_id) VALUES (1,1)''')
    cls.execute('''INSERT INTO klasses_packages (klass_id, package_id) VALUES (2,1)''')
    cls.execute('''INSERT INTO settings (key, value) VALUES ('name','Instituto Superior de Danzas Sharife')''')
    cls.execute('''INSERT INTO settings (key, value) VALUES ('opening','18:00')''')
    cls.execute('''INSERT INTO settings (key, value) VALUES ('closing','24:00')''')
    cls.execute('''INSERT INTO settings (key, value) VALUES ('recharge_after','10')''')
    cls.execute('''INSERT INTO settings (key, value) VALUES ('recharge_value','50')''')
    cls.execute('''INSERT INTO settings (key, value) VALUES ('startup_size','')''')
    cls.execute('''INSERT INTO settings (key, value) VALUES ('language','es')''')
    cls.execute('''INSERT INTO settings (key, value) VALUES ('tabs_position','top')''')
    cls.commit()

  @classmethod
  def commit(cls):
    cls._conn.commit()

  @classmethod
  def execute(cls, q, p = ()):
    return cls._conn.execute(q, p)
