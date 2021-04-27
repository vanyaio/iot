import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('stats', __name__)

@bp.route('/')
@login_required
def index():
    #return redirect(url_for('stats.choose_time_eqnt'))
    return render_template('stats/index.html')

@bp.route('/last_beep')
@login_required
def last_beep():
    id = g.user['id']
    db = get_db()

    data = db.execute(
        'SELECT * FROM touch_data d '
        'WHERE d.user_id = ? '
        'ORDER BY time DESC;',
        (id, )
    ).fetchone()

    print(data['user_id'], data['time'], data['eqnt_id'], data['set_busy'])
    ret = "user {0}, time {1}, equipment {2}, set busy {3}".format(\
           data['user_id'], data['time'], data['eqnt_id'], data['set_busy'])
    #  return str(data)
    return ret 

eqnt_cnt = 7
@bp.route('/choose_time_eqnt')
#  @login_required
def choose_time_eqnt():
    global eqnt_cnt
    eqnt = {i : 'Machine' + str(i) for i in range(eqnt_cnt)}
    return render_template('stats/choose_time_eqnt.html', eqnt=eqnt)

@bp.route('/usage', methods=('GET', 'POST'))
#  @login_required
def usage():
    global eqnt_cnt

    if request.method == 'GET':
        time_str = request.args.get('time', '')
        #18/09/19 01:55 - format
        time = datetime.datetime.strptime(time_str, '%d/%m/%y %H:%M')

        eqnt = []
        for eid in range(eqnt_cnt):
            if request.args.get('eid' + str(eid), '') == 'on':
                eqnt.append(int(eid))

        predict = request.args.get('predict', '')
        if predict == '':
            predict_if_happened = None
        else:
            predict_if_happened = eval(predict)#predict 'True' or 'F..'

        if predict_if_happened is not None and predict_if_happened:
            usage = get_usage_if_happened(time, eqnt)
            return str(usage)
        if predict_if_happened is not None and not predict_if_happened:
            usage = get_usage(time, eqnt)
            return str(usage)

        if predict_if_happened is None:
            usage = get_usage(time, eqnt)
            return render_template('stats/usage.html', time=time, \
                                   eqnt=eqnt, usage=usage)

@bp.route('/new_touch_data', methods=('GET', 'POST'))
#@login_required #TODO: admin account
def new_touch_data():
    if request.method == 'POST':
        print(request.content_type)
        print(request.form)
        user_id = int(request.form['user_id'])
        eqnt_id = int(request.form['eqnt_id'])
        set_busy = int(request.form['set_busy'])
        if 'time' not in request.form:
            time = datetime.datetime.now()
        else:
            time = request.form['time']
        db = get_db()
        db.execute(
            'INSERT INTO touch_data (user_id, time, eqnt_id, set_busy)'
            ' VALUES (?, ?, ?, ?)',
            (user_id, time, eqnt_id, set_busy)
        )
        db.commit()

    #return print_touch_data_db()
    return "Hello"






@bp.route('/test_db')
def test_db():
    db = get_db()
    data = db.execute(
        'SELECT * FROM touch_data d '
    ).fetchall()

    ret = ''
    ret += 'hey'
    for d in data:
        ret += str(d['time']) + '<br>'

    return ret

def get_some_weeks_ago_in_db(time, predict_if_happened=False):
    db = get_db()

    if predict_if_happened:
        t = time - datetime.timedelta(days = 7)
    else:
        t = time

    while True:
        data = db.execute(
            'SELECT * FROM touch_data d '
            'WHERE d.time > ? ',
            (t,)
        ).fetchone()
        if data is not None:
            return t
        t = t - datetime.timedelta(days = 7)

#ML:
def get_usage_for_one_e(time, eqnt_id, predict_if_happened=False):
    db = get_db()
    delta_mins = 60

    #  t = datetime.datetime(2021, 3, 1, 18, 53, 0, 0)
    t = get_some_weeks_ago_in_db(time, predict_if_happened=predict_if_happened)
    tl = t - datetime.timedelta(minutes = delta_mins)

    data = db.execute(
        'SELECT * FROM touch_data d '
        'WHERE d.time > ? AND d.time <= ? '
        'ORDER BY time DESC;',
        (tl, t)
    ).fetchall()
    #
    #  for d in data:
            #  ret += "({0}, {1}, {2}, {3})".format( \
                   #  d['user_id'], d['time'], d['eqnt_id'], d['set_busy']) + "<br>\n"
    #  ret += "<br><br><br><br>"
    #

    user = dict()
    for d in data:
        if d['user_id'] not in user:
            user[d['user_id']] = { 'set_busy' : d['set_busy'], \
                                   'eqnt_id' : d['eqnt_id'], \
                                   'time' : d['time'] }

    waiting_users = [u for u in user if user[u]['set_busy'] == 0]

    tr = t + datetime.timedelta(minutes = delta_mins)
    data = db.execute(
        'SELECT * FROM touch_data d '
        'WHERE d.time > ? AND d.time <= ? AND d.eqnt_id == ? '
        'ORDER BY time ASC;',
        (t, tr, eqnt_id)
    ).fetchall()

    waiting_users_for_e = []
    for d in data:
        if d['user_id'] in waiting_users:
            if d['eqnt_id'] == eqnt_id and d['set_busy'] == 1:
                waiting_users_for_e.append({'user_id' : d['user_id'], \
                                            'time_start' : d['time']})

    wait_time = datetime.timedelta()
    for m in waiting_users_for_e:
        uid = m['user_id']
        time_start = m['time_start']
        wait_time = max(wait_time, time_start - t)

    return wait_time.seconds // 60

def get_usage(time, eqnt_ids):
    #time is datetime, eqnt is iterable
    return { (time, e) : get_usage_for_one_e(time, e)  for e in eqnt_ids }

def get_usage_if_happened(time, eqnt_ids):
    #time is datetime, eqnt is iterable
    return { (time, e) : get_usage_for_one_e(time, e, True)  for e in eqnt_ids }
