from datetime import timedelta


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class Status(AttrDict):
    ...


class Service(AttrDict):
    ...


RAND_GEN = Service(**{'id': 1, 'name': 'Randon number generator'})
services = [s for s in vars(
).values() if isinstance(s, Service)]

PLAN_1 = Status(**{'id': 1, 'name': 'PLAN I',
                       'services_enabled': str([RAND_GEN.id]), 'plan': timedelta(30),
                       'lifetime': False})
statuses = [st for st in vars().values()
                 if isinstance(st, Status)]
