#!/usr/local/bin/python
# -*- coding: utf-8 -*-

class I18n():
  langs = ['en','es']
  lang = 'es'

  @classmethod
  def set_lang(cls, l):
    if l in cls.langs:
      cls.lang = l

  ts = {
    'common': {
      'months': [
        ['January','February','March','April','May','June','July','August','September','October','November','December'],
        ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
      ],
      'abbr_months': [
        ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'],
        ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
      ],
      'days': [
        ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],
        ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
      ],
      'abbr_days': [
        ['mon','tue','wed','thu','fri','sat','sun'],
        ['lun','mar','mie','jue','vie','sab','dom']
      ]
    },
    'models': {
      'installment': ['Installment','Cuota'],
      'klass': ['Class','Clase'],
      'membership': ['Membership','Inscripción'],
      'room': ['Room','Sala'],
      'schedule': ['Schedule','Horario'],
      'student': ['Student','Alumno'],
      'teacher': ['Teacher','Profesor']
    },
    'attrs': {
      'installment': {
        'month': ['Month', 'Mes'],
        'membership': ['Membership', 'Inscripción'],
        'paid': ['Paid','Pagado'],
        'amount': ['Amount','Cantidad'],
        'payment': ['Payment','Pago'],
        'paid': ['Paid','Pagado'],
        'waiting': ['Waiting','A pagar'],
        'paid_with_interests': ['Paid with interests', 'Pagado con intereses']
      },
      'klass': {
        'name': ['Name','Nombre'],
        'normal_fee': ['Normal fee', 'Precio normal'],
        'half_fee': ['Half classes fee', 'Precio mitad de las clases'],
        'once_fee': ['One class fee', 'Precio de una sola clase'],
        'inscription_fee': ['Inscription fee', 'Precio de incripción'],
        'min_age': ['Minimum age', 'Edad mínima'],
        'max_age': ['Maximum age', 'Edad máxima'],
        'quota': ['Quota', 'Cupo máximo'],
        'info': ['Information', 'Información'],
        'teachers': ['Teachers', 'Profesores'],
        'students': ['Students', 'Alumnos'],
        'schedules': ['Schedules', 'Horarios']
      },
      'membership': {
        'student_id': ['Student','Alumno'],
        'klass_or_package': ['Class or Package','Clase o Paquete'],
        'installments': ['Installments','Cuotas'],
        'info': ['Information','Información']
      },
      'package': {
        'name': ['Name','Nombre'],
        'fee': ['Fee','Precio'],
        'alt_fee': ['Alternative Fee','Precio Alternativo'],
        'klasses': ['Classes','Clases']
      },
      'payment': {
        'date': ['Date','Fecha'],
        'amount': ['Amount','Monto'],
        'description': ['Description','Descripción']
      },
      'room': {
        'name': ['Name','Nombre']
      },
      'schedule': {
        'from_time': ['From','Desde'],
        'to_time': ['To','Hasta'],
        'day': ['Day','Día'],
        'room': ['Room','Salón']
      },
      'student': {
        'name': ['Name','Nombre'],
        'lastname': ['Lastname','Apellido'],
        'dni': ['Doc','DNI'],
        'cellphone': ['Cellphone','Celular'],
        'alt_phone': ['Alternative Phone','Teléfono alternativo'],
        'birthday': ['Birthday','Fecha de nacimiento'],
        'address': ['Address','Dirección'],
        'male': ['Male','Hombre'],
        'female': ['Female','Mujer'],
        'gender': ['Gender','Sexo'],
        'email': ['Email', 'E-mail'],
        'is_teacher': ['Is teacher','Es profesor'],
        'comments': ['Comments','Comentarios'],
        'memberships': ['Memberships','Inscripciones'],
        'facebook_uid': ['Facebook ID', 'ID de Facebook'],
        'age': ['Age (Years)', 'Edad (Años)']
      },
      'teacher': {
        'name': ['Name','Nombre'],
        'lastname': ['Lastname','Apellido'],
        'dni': ['Doc','DNI'],
        'cellphone': ['Cellphone','Celular'],
        'alt_phone': ['Alternative Phone','Teléfono alternativo'],
        'birthday': ['Birthday','Fecha de nacimiento'],
        'address': ['Address','Dirección'],
        'male': ['Male','Hombre'],
        'female': ['Female','Mujer'],
        'gender': ['Gender','Sexo'],
        'email': ['Email', 'E-mail'],
        'is_teacher': ['Is teacher','Es profesor'],
        'comments': ['Comments','Comentarios'],
        'facebook_uid': ['Facebook ID', 'ID de Facebook'],
        'age': ['Age (Years)', 'Edad (Años)']
      }
    },
    'errors': {
      'field_not_blank': ['Field "%(field)s" can\'t be blank.','El campo "%(field)s" no puede estar en blanco.'],
      'field_not_number': ['Field "%(field)s" is not a number.', 'El campo "%(field)s" no es un número.'],
      'field_not_greate_than': ['Field "%(field)s" must be greater than %(than)s.', 'El campo "%(field)s" debe ser mayor a %(than)s.'],
      'field_not_less_than': ['Field "%(field)s" must be less than %(than)s.', 'El campo "%(field)s" debe ser menor a %(than)s'],
      'field_not_greate_than_or_equal': ['Field "%(field)s" must be greater or equal than %(than)s.', 'El campo "%(field)s" debe ser mayor o igual a %(than)s.'],
      'field_not_less_than_or_equal': ['Field "%(field)s" must be less or equal than %(than)s.', 'El campo "%(field)s" debe ser menor o igual a %(than)s'],
      'wrong_format': ['Field "%(field)s"\'s format is not valid.', 'El formato del campo "%(field)s" no es válido.'],
      'only_letters': ['Field "%(field)s" must have only letters.', 'El campo "%(field)s" debe tener sólo letras.'],
      'wrong_quantity': ['Quantity of %(field)s is wrong.', 'La cantidad de %(field)s es inválida.'],
      'has_many_invalid': ['One or more %(relationship)s are invalid.','Uno/a o más %(relationship)s son inválidos.']
    }
  }

  @classmethod
  def lang_idx(cls, l):
    if l is None:
      l = cls.lang
    return cls.langs.index(l)

def _t(key, l = None):
  return I18n.ts['common'][key][I18n.lang_idx(l)]

def _m(model, l = None):
  return I18n.ts['models'][model.lower()][I18n.lang_idx(l)]

def _a(model, attr, l = None):
  return I18n.ts['attrs'][model.lower()][attr][I18n.lang_idx(l)]

def _e(err, l = None):
  return I18n.ts['errors'][err][I18n.lang_idx(l)]
