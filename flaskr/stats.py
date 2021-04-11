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
    return redirect(url_for('stats.choose_time_eqnt'))

@bp.route('/choose_time_eqnt')
@login_required
def choose_time_eqnt():
    return redirect(url_for('stats.usage'))

@bp.route('/usage')
@login_required
def usage():
    #times and eqnt from request
    cnt = 5
    times = [ "Time " + str(i) for i in range(1)]
    eqnt = [ "Machine " + str(i) for i in range(cnt) ]
    usage = { (t, e) : "0%"  for t in times for e in eqnt }
    return render_template('stats/usage.html', times=times, eqnt=eqnt, usage=usage)

def print_touch_data_db():
    db = get_db()
    touch_data = db.execute(
        'SELECT * FROM touch_data'
    ).fetchall()
    ret = ''
    for t in touch_data:
            ret += "({0}, {1}, {2}, {3})".format(t['user_id'], \
                                t['eqnt_id'], t['time'], t['set_busy']) \
                   + "<br>\n"
    return ret

@bp.route('/new_touch_data', methods=('GET', 'POST'))
#@login_required #TODO: admin account
def new_touch_data():
    if request.method == 'POST':
        user_id = int(request.form['user_id'])
        #TODO: time = request.form['time']
        eqnt_id = int(request.form['eqnt_id'])
        set_busy = bool(request.form['set_busy'])
        db = get_db()
        db.execute(
            'INSERT INTO touch_data (user_id, eqnt_id, set_busy)'
            ' VALUES (?, ?, ?)',
            (user_id, eqnt_id, set_busy)
        )
        db.commit()

    return print_touch_data_db()
