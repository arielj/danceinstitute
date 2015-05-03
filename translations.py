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
      'student': ['Student','Alumno'],
      'klass': ['Class','Clase'],
      'installments': ['Installments','Cuotas'],
      'year': ['Year','Año'],
      'type': ['Type','Tipo'],
      'info': ['Information','Información'],
      'initial_month': ['Initial month','Mes inicial'],
      'final_month': ['Final month','Mes final'],
      'date': ['Date','Fecha'],
      'fee': ['Fee','Precio']
    }
  }
}

def lang_idx():
  return langs.index(lang)

def _t(key):
  return ts['common'][key][lang_idx()]

def _m(model):
  return ts['models'][model][lang_idx()]

def _a(model, attr):
  return ts['attrs'][model][attr][lang_idx()]
