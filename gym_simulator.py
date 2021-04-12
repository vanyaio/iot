import random
import numpy as np
import datetime
from inspect import currentframe, getframeinfo

def linenum():
    cf = currentframe()
    return cf.f_back.f_lineno

eqnt_cnt = 7
appch_cnt = 5
user_cnt = 50
trains_per_week = 3

def normal(x,mu,sigma):
        return ( 2.*np.pi*sigma**2. )**-.5 * np.exp( -.5 * (x-mu)**2. / sigma**2. )

def gen_train_start_time():
    return int(np.random.normal(19 * 60 , 2 * 60, 1)[0]) % (24 * 60)

class Eqnt:
    list = []
    is_filled = False

    def __init__(self, id):
        self.queue = [] #of User objects
        self.id = id
        self.curr_user = None

    def is_in_queue(self, user):
        for u in self.queue:
            if u is user:
                return True
        return False

    def add_to_queue(self, user):
        self.queue.append(user)

    def can_use_eqnt(self, user):
        if user is self.queue[0] and self.curr_user == None:
            return True
        return False

    def use_eqnt(self, user):
        self.queue.pop(0)
        self.curr_user = user

    def stop_using_eqnt(self, user):
        self.curr_user = None

    def time_wait(self, t):
        time_end = t
        if self.curr_user != None:
            time_end = self.curr_user.appch_end

        for u in self.queue:
            time_end += datetime.timedelta(minutes = u.curr_appch.time_len)

        if (time_end is t):
            return 0
        delta = time_end - t
        return (time_end - t)

    @classmethod
    def fill_list(cls):
        global eqnt_cnt
        if cls.is_filled:
            return
        for i in range(eqnt_cnt):
            cls.list.append(Eqnt(i))
        cls.is_filled = True

class Approach:
    def __init__(self, eqnt, time_len):
        self.eqnt = eqnt
        self.time_len = time_len

    @staticmethod
    def gen_random_approach():
        Eqnt.fill_list()
        eqnt_len = len(Eqnt.list)
        idx = random.randint(0, eqnt_len - 1)

        eqnt = Eqnt.list[idx]
        time_len = 12

        return Approach(eqnt, time_len)

class Train:
    def __init__(self, appch_list, start_time):
        self.appch_list = appch_list
        self.start_time = start_time #minutes (24 * 60 range)
        self.reload_appch_iter()

    def reload_appch_iter(self):
        self.iter = self.next_appch_gen()

    def next_appch(self):
        return next(self.iter)

    def next_appch_gen(self):
        for a in self.appch_list:
            yield a

    @staticmethod
    def gen_random_train():
        global appch_cnt
        appch_list = [Approach.gen_random_approach() for i in range(appch_cnt)]
        return Train(appch_list, gen_train_start_time())

class Schedule:
    def __init__(self, days_of_week, trains):
        #lists of the same len (one train for a day)
        _days_of_week = days_of_week.copy()
        _days_of_week.sort()
        self.train_of_day = {d : trains[i] for i, d in enumerate(_days_of_week)}

    def train_for_this_t(self, t):
        #t is datetime.datetime
        for d in self.train_of_day:
            if d != t.weekday():
                continue

            d_minute = self.train_of_day[d].start_time
            t_minute = t.time().hour * 60 + t.time().minute
            if d_minute == t_minute:
                return self.train_of_day[d]

        return None

    @staticmethod
    def gen_random_schedule():
        all_days_of_week = [i for i in range(7)]
        global trains_per_week
        days_of_week = random.sample(all_days_of_week, trains_per_week)

        trains = [Train.gen_random_train() for i in range(trains_per_week)]

        return Schedule(days_of_week, trains)

class User:
    list = []
    is_filled = False

    def __init__(self, sched):
        self.sched = sched
        self.in_train = False
        self.curr_train = None
        self.curr_appch = None
        self.appch_start = None
        self.appch_end = None

    def train_entry(self, train):
        train.reload_appch_iter()
        self.curr_train = train
        self.in_train = True
        self.appch_start = None

    def train_exit(self, time):
        self.in_train = False
        self.curr_train = None
        self.curr_appch = None
        self.appch_start = None
        self.appch_end = None

    def appch_entry(self, t):
        eqnt = self.curr_appch.eqnt
        eqnt.use_eqnt(self)
        self.appch_start = t
        self.appch_end = t + datetime.timedelta(minutes = self.curr_appch.time_len)

    def appch_exit(self, t):
        eqnt = self.curr_appch.eqnt
        eqnt.stop_using_eqnt(self)
        self.curr_appch = None
        self.appch_start = None
        self.appch_end = None

    @classmethod
    def fill_list(cls):
        global user_cnt
        if cls.is_filled:
            return
        for i in range(user_cnt):
            cls.list.append(User(Schedule.gen_random_schedule()))
        cls.is_filled = True

def time_generator():
    epoch = 0
    t = datetime.datetime.fromtimestamp(epoch)
    yield t
    #while t.month != 2:
    while t.day != 8:
        t += datetime.timedelta(minutes = 1)
        yield t

def sim_step(t, u):
    train = u.sched.train_for_this_t(t)

    if train != None:
        if u.in_train:
            raise Exception('Value error!')
        u.train_entry(train)

    del train

    if not u.in_train:
        return

    if u.appch_start == None:
        if u.curr_appch == None:
            try:
                u.curr_appch = u.curr_train.next_appch()
            except StopIteration:
                u.train_exit(t)
                return

        eqnt = u.curr_appch.eqnt
        if (not eqnt.is_in_queue(u)):
            eqnt.add_to_queue(u)

        if eqnt.can_use_eqnt(u):
            u.appch_entry(t)
        else:
            return

    #u.appch_start not None by this moment
    if t != u.appch_end:
        return
    else:
        u.appch_exit(t)


class Stats:
    time_usage = [] # [[(time, usage), ...], ..., []], i-th [] for Equipment-i
    is_alloced = False

    def alloc():
        if Stats.is_alloced:
            return
        Stats.is_alloced = True
        Stats.time_usage = [[] for i in range(len(Eqnt.list))]

    def update(t):
        Stats.alloc()
        for i, e in enumerate(Eqnt.list):
            arr = Stats.time_usage[i]
            arr.append((t, e.time_wait(t)))

def sim_main():
    User.fill_list()
    for t in time_generator():
        for u in User.list:
            sim_step(t, u)
        Stats.update(t)

sim_main()
