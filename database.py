#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import datetime
import os

FILENAME = 'data.db'

class Conn(object):
  _conn = None

  CREATE = {'settings': '''CREATE TABLE settings (key text, value text)''',
            'installments': '''CREATE TABLE installments (id integer primary key, year integer, month integer, membership_id integer, amount integer, status text default '')''',
            'payments': '''CREATE TABLE payments (id integer primary key, date date, amount integer, installment_id integer, user_id integer, user_type text default '',description text default '', done integer default 0)''',
            'rooms': '''CREATE TABLE rooms (id integer primary key, name text)''',
            'memberships': '''CREATE TABLE memberships (id integer primary key, student_id integer, for_id integer, for_type text, info text)''',
            'schedules': '''CREATE TABLE schedules (id integer primary key, klass_id integer, from_time integer, to_time integer, room_id integer, day integer)''',
            'users': '''CREATE TABLE users (id integer primary key, name text, lastname text, dni string, cellphone text, alt_phone text, birthday date, address text, male integer, email text, is_teacher integer, comments text default '', facebook_uid text default '')''',
            'klasses': '''CREATE TABLE klasses (id integer primary key, name text, normal_fee integer, half_fee integer, once_fee integer, inscription_fee integer, min_age integer, max_age integer, quota integer, info text)''',
            'klasses_teachers': '''CREATE TABLE klasses_teachers (klass_id integer, teacher_id integer)''',
            'packages': '''CREATE TABLE packages (id integer primary key, name text, fee integer, alt_fee integer)''',
            'klasses_packages': '''CREATE TABLE klasses_packages (klass_id integer, package_id integer)''',
            'movements': '''CREATE TABLE movements (id integer primary key, date date, amount integer, description text default '', done integer default 0)'''
           }

  @classmethod
  def start_connection(cls,env):
    if cls._conn is None:
      create_db = False
      seed_db = False
      dev_data = False
      check_version = False
      if env == 'test' or env == 'dev':
        cls._conn = sqlite3.connect(":memory:")
        create_db = True
        dev_data = env == 'dev'
      else:
        if not os.path.isfile(FILENAME):
          create_db = True
          seed_db = True
          open(FILENAME,'a').close()
        cls._conn = sqlite3.connect(FILENAME)

      if create_db:
        cls.create_tables()

      cls.check_version()
      
      if seed_db:
        cls.seed()
      
      if dev_data:
        cls.dev_data()

      cls._conn.row_factory = sqlite3.Row
      cls._conn.text_factory = str

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
    cls.commit()

  @classmethod
  def create(cls, table):
    cls._conn.execute(cls.CREATE[table])

  @classmethod
  def seed(cls):
    cls.execute('''INSERT INTO rooms (name) VALUES ('Sala 1')''')
    cls.execute('''INSERT INTO settings (key, value) VALUES ('name','Nombre')''')
    cls.execute('''INSERT INTO settings (key, value) VALUES ('opening','18:00')''')
    cls.execute('''INSERT INTO settings (key, value) VALUES ('closing','24:00')''')
    cls.execute('''INSERT INTO settings (key, value) VALUES ('recharge_after','10')''')
    cls.execute('''INSERT INTO settings (key, value) VALUES ('recharge_value','50')''')
    cls.execute('''INSERT INTO settings (key, value) VALUES ('startup_size','')''')
    cls.execute('''INSERT INTO settings (key, value) VALUES ('language','es')''')
    cls.execute('''INSERT INTO settings (key, value) VALUES ('tabs_position','top')''')
    cls.commit()

  @classmethod
  def check_version(cls):
    result = cls.execute('''SELECT value FROM settings WHERE key = "version";''').fetchone()
    if result:
      version = result[0]
    else:
      version = '0.1'
    
    if version == '0.1':
      cls.execute('''ALTER TABLE users ADD COLUMN age integer;''')
      cls.execute('INSERT INTO settings (key, value) VALUES ("version","0.2")')
      version = '0.2'
    
    if version == '0.2':
      cls.execute('INSERT INTO settings (key, value) VALUES ("notes", "")')
      version = cls.set_version('0.3')
    
    if version == '0.3':
      cls.create('movements')
      version = cls.set_version('0.4')
    
    if version == '0.4':
      cls.execute('ALTER TABLE payments ADD COLUMN receipt_number integer;')
      version = cls.set_version('0.5')

    if version == '0.5':
      cls.execute('INSERT INTO settings (key, value) VALUES ("export_path", "")')
      version = cls.set_version('0.6')

  @classmethod
  def set_version(cls,version):
    cls.execute('UPDATE settings SET value = :version WHERE key = "version"',{'version': version})
    return version

  @classmethod
  def dev_data(cls):
    cls.execute('''INSERT INTO rooms (name) VALUES ('Tierra')''')
    cls.execute('''INSERT INTO rooms (name) VALUES ('Aire')''')
    cls.execute('''INSERT INTO rooms (name) VALUES ('Fuego')''')
    cls.execute('''INSERT INTO installments (year, month, amount, membership_id, status) VALUES (2015, 4, 300, 1, 'paid')''')
    cls.execute('''INSERT INTO installments (year, month, amount, membership_id, status) VALUES (2015, 5, 300, 1, 'paid')''')
    cls.execute('''INSERT INTO payments (date, amount, installment_id, user_id, user_type) VALUES (?, 200, 1, 3, 'Student')''',(datetime.date(2015,3,3),))
    cls.execute('''INSERT INTO payments (date, amount, installment_id, user_id, user_type) VALUES (?, 100, 2, 3, 'Student')''',(datetime.date(2015,3,4),))
    cls.execute('''INSERT INTO payments (date, amount, installment_id, user_id, user_type) VALUES (?, 100, 2, 3, 'Student')''',(datetime.date(2015,3,1),))
    cls.execute('''INSERT INTO payments (date, amount, description, user_id, user_type, done) VALUES (?, 100, 'lalala', 1, 'Teacher',1)''',(datetime.datetime.today().date(),))
    cls.execute('''INSERT INTO payments (date, amount, description, user_id, user_type) VALUES (?, 100, 2, 3, 'Student')''',(datetime.datetime.today().date(),))
    cls.execute('''INSERT INTO payments (date, amount, description, user_id, user_type) VALUES (?, 100, 'Inscripción', 3, 'Student')''',(datetime.date(2015,2,26),))
    cls.execute('''INSERT INTO memberships (student_id, for_id, for_type, info) VALUES (3, 1, 'Klass', 'Clase normal lalala')''')
    cls.execute('''INSERT INTO schedules (klass_id, from_time, to_time, room_id, day) VALUES (1, 2000, 2130, 3, 0)''')
    cls.execute('''INSERT INTO schedules (klass_id, from_time, to_time, room_id, day) VALUES (1, 2000, 2130, 3, 3)''')
    cls.execute('''INSERT INTO schedules (klass_id, from_time, to_time, room_id, day) VALUES (2, 1900, 2030, 2, 1)''')
    cls.execute('''INSERT INTO schedules (klass_id, from_time, to_time, room_id, day) VALUES (2, 1900, 2030, 2, 3)''')
    cls.execute('''INSERT INTO users (name, lastname, dni, cellphone, birthday, address, male, email, is_teacher) VALUES ('Lau', 'Gut', '35592392', '0299-15-453-4315', '1991-02-12', '9 de Julio 1140', 0, 'lali_gut@yahoo.com.ar', 1)''')
    cls.execute('''INSERT INTO users (name, lastname, dni, cellphone, birthday, address, male, email, is_teacher) VALUES ('Tincho', 'Arce', '11111111', 'nose', '1981-02-12', 'Barrio mercantil', 1, 'tincho@sharife.com.ar', 1)''')
    cls.execute('''INSERT INTO users (name, lastname, dni, cellphone, birthday, address, male, email, is_teacher, age) VALUES ('Ariel', 'Juod', '32496445', '0299-15-411-5106', '1986-07-18', '9 de Julio 1140', 1, 'arieljuod@gmail.com', 0, 28)''')
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
    cls.execute('UPDATE settings SET value = "anotación importante\nhola" WHERE key = "notes"')
    cls.execute('''INSERT INTO movements (date, amount, description, done) VALUES (?, 50, 'saco 100 para el kiosko',1)''',(datetime.datetime.today().date(),))
    cls.commit()

  @classmethod
  def commit(cls):
    cls._conn.commit()

  @classmethod
  def execute(cls, q, p = ()):
    cur = cls._conn.execute(q, p)
    cls.commit()
    return cur

  @classmethod
  def close(cls):
    cls._conn.close()
