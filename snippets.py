    # crear cuotas de 2018 a alumnos de 2017
    sids = []
    for i in Installment.where('year', '2017').where('month', 10, '>='):
      sid = i.get_student_id()
      if sid not in sids:
        sids.append(sid)

    for sid in sids:
      print sid
      s = Student.find(sid)
      m = s.memberships[0]
      a = None
      if m.for_type == 'Package':
          new_p = Package.for_user_with_klasses(m.klasses())
          new_p.for_user = sid
          new_p.save()
          m = Membership()
          m.student = s
          m.klass_or_package = new_p
          m.save()
          a = new_p.get_hours_fee()
      else:
          k = m.klass_or_package
          m = Membership()
          m.student = s
          m.klass_or_package = k
          m.save()
          a = k.get_hours_fee()

      if s.family:
        a = float(a)*0.9

      m.create_installments('2018', 2, 6, a)
