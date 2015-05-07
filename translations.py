#!/usr/local/bin/python
# -*- coding: utf-8 -*-

langs = ['en','es']
lang = 'es'

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
      'payment': ['Payment','Pago']
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
      'Schedules': ['Schedules', 'Horarios']
    },
    'membership': {
      'student_id': ['Student','Alumno'],
      'klass_id': ['Class','Clase'],
      'installments': ['Installments','Cuotas'],
      'year': ['Year','Año'],
      'type': ['Type','Tipo'],
      'info': ['Information','Información'],
      'initial_month': ['Initial month','Mes inicial'],
      'final_month': ['Final month','Mes final'],
      'date': ['Date','Fecha'],
      'fee': ['Fee','Precio']
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
      'comments': ['Comments','Comentarios']
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
      'comments': ['Comments','Comentarios']
    }
  },
  'errors': {
    'field_not_blank': ['Field "%(field)s" can\'t be blank.','El campo "%(field)s" no puede estar en blanco.'],
    'field_not_number': ['Field "%(field)s" is not a number.', 'El campo "%(field)s" no es un número.'],
    'field_not_greate_than': ['Field "%(field)s" must be greater than %(than)s.', 'El campo "%(field)s" debe ser mayor a %(than)s.'],
    'field_not_less_than': ['Field "%(field)s" must be less than %(than)s.', 'El campo "%(field)s" debe ser menor a %(than)s'],
    'wrong_format': ['Field "%(field)s"\'s format is not valid.', 'El formato del campo "%(field)s" no es válido.'],
    'only_letters': ['Field "%(field)s" must be only letters.', 'El campo "%(field)s" debe ser sólo letras.']
  }
}

def lang_idx(l):
  if l is None:
    l = lang
  return langs.index(l)

def _t(key, l = None):
  return ts['common'][key][lang_idx(l)]

def _m(model, l = None):
  return ts['models'][model.lower()][lang_idx(l)]

def _a(model, attr, l = None):
  return ts['attrs'][model.lower()][attr][lang_idx(l)]

def _e(err, l = None):
  return ts['errors'][err][lang_idx(l)]
