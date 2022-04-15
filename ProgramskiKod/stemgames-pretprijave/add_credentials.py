import random
import string

from application_app import models

PASSLENGTH = 8

def generate_password():
    s = ''
    for i in range(PASSLENGTH):
        s += random.choice(string.ascii_letters + string.digits)
    return s

for inst in models.Institution.query.all():
    name = inst.name.split()[0]+str(inst.id)
    pwd = generate_password()
    print(name,pwd,'(%s)'%inst.name)

    cred = models.Credentials(name=name, limit_to_institution=inst.id)
    cred.set_password(pwd)
    models.db.session.add(cred)
    models.db.session.commit()

for name in ['COLLEGIUM', 'IZVRSNI']:
    pwd = generate_password()
    print(name,pwd)

    cred = models.Credentials(name=name, limit_to_institution=inst.id)
    cred.set_password(pwd)
    models.db.session.add(cred)
    models.db.session.commit()
