import random
import numpy as np 

eqnt_cnt = 15
appch_cnt = 5
user_cnt = 100 

def normal(x,mu,sigma):
        return ( 2.*np.pi*sigma**2. )**-.5 * np.exp( -.5 * (x-mu)**2. / sigma**2. )

def gen_train_start_time()
    return int(np.random.normal(19 * 60 , 2 * 60, 1)[0]) % (24 * 60)

class Eqnt:
    list = []
    is_filled = False

    def __init__(self, id):
        self.queue = []
        self.id = id 

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
        self.start_time = start_time

    @staticmethod
    def gen_random_train():
        global appch_cnt
        appch_list = [gen_random_approach() for i in range(appch_cnt)]
        return Train(appch_list, gen_train_start_time())

class Schedule:
    def __init__(self, days_of_week, trains):
        #lists of the same len of course (one train for a day)
        self.days_of_week = days_of_week
        self.days_of_week.sort()
        self.trains = trains

    def train_for_this_t(self, t):
        for i, d in enumerate(self.days_of_week):
            if d != t.weekday():
                continue

            d_minute = self.trains[i].start_time
            t_minue = t.time().hour * 60 + t.time().minutes
            if d_minute == t_minute:
                return self.trains[i]

        return None

    @staticmethod
    def gen_random_schedule():
        all_days_of_week = [i for in range(7)]
        trains_per_week = 3
        days_of_week = random.sample(all_days_of_week, trains_per_week)

        trains = [Train.gen_random_train() for i in range(trains_per_week)]

        return Schedule(days_of_week, trains)
        
class User:
    list = []
    is_filled = False

    def __init__(self, sched):
        self.sched = sched
        self.in_train = None
        self.curr_train = None
        self.appch_idx = None
        self.appch_start = None
        self.appch_end = None

    @classmethod
    def fill_list(cls):
        global user_cnt
        if cls.is_filled:
            return
        for i in range(user_cnt):
            cls.list.append(User(gen_random_schedule()))
        cls.is_filled = True


