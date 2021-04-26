import requests
import math
import datetime

API_ENDPOINT = "http://127.0.0.1:5000/usage"
eqnt_cnt = 7



#18/09/19 01:55 - format
def send(eid, d, predict=False):
    data = dict()
    data['time'] = "{0}/04/21 19:00".format(d)
    data['eid{0}'.format(eid)] = 'on'

    if predict:
        data['predict'] = 'True'
    else:
        data['predict'] = 'False'

    r = requests.get(url = API_ENDPOINT, params = data)
    #{ (time, e) : get_usage_for_one_e(time, e, True)  for e in eqnt_ids }
    return eval(r.text)

def send_and_get_error(eid, d):
    usage_real = send(eid, d, predict=False)
    usage_pred = send(eid, d, predict=True)
    for k in usage_real.keys():
        real_minutes = usage_real[k]
        pred_minutes = usage_pred[k]
        return abs(real_minutes - pred_minutes)

def main():
    for eid in range(eqnt_cnt):
        print("-----Eqnt {0}------".format(eid))
        for d in range(8, 15):
            print("day {0}, error {1}".format(d, send_and_get_error(eid, d)))

main()
