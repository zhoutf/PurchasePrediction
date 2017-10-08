# -*- coding: utf-8 -*-

import time
import datetime
from data_process import process_user_behaviors
import output

# date convension

def date_to_timestamp(date):
    if len(date) == 0:
        return -1
    pattern = '%Y-%m-%d %H:%M:%S'
    strptime = time.strptime(date, pattern)
    timestamp = time.mktime(strptime)
    return timestamp


def timestamp_to_date(timestamp):
    date_ = datetime.datetime.fromtimestamp(timestamp)
    date_str = date_.strftime('%Y-%m-%d %H:%M:%S')
    return date_str


def filter_user_action(action, data):
    """
    :param action: 1-浏览 2-收藏 3-加购 4-购买
    """

    def _filter_(element):
        if element[-1] == action:
            return True
        else:
            return False

    new_data = filter(_filter_, data)

    return new_data


def filter_time(data, start_time, end_time=-1):

    """
    filter with timestamp
    :param start_time: start time/Unix Timestamp
    :param end_time: end time/Unix Timestamp
    """

    def _filter_(element):

        if element[2] >= start_time and (element[2] <= end_time or end_time == -1):
            return True
        else:
            return False

    new_data = filter(_filter_, data)

    return new_data


def write_to_file(behaviors, filepath, timestamp=False):

    with open(filepath, 'w+') as f:

        for element in behaviors:
            line = '\t'.join(['%s' % x for x in element])
            line += '\n'
            f.write(line)
    print("Saved to file: %s" % filepath)


def remove_purchased(purchased, shopping_cart):

    def _filter(element):
        for pur_ele in purchased:
            if element[0] == pur_ele[0] and  element[1] == pur_ele[1] and element[2] < pur_ele[2]:
                return True

        return False

    _shopping = filter(_filter, shopping_cart)

    return _shopping



def split_action_behaviors():

    behaviors = process_user_behaviors()

    action_one_behavior = filter_user_action(1, behaviors)
    action_two_behavior = filter_user_action(2, behaviors)
    action_three_behavior = filter_user_action(3, behaviors)
    action_four_behavior = filter_user_action(4, behaviors)
    del behaviors
    dir_path = './data/behaviors/'
    write_to_file(action_one_behavior, dir_path+'action_1.txt')
    write_to_file(action_two_behavior, dir_path+'action_2.txt')
    write_to_file(action_three_behavior, dir_path+'action_3.txt')
    write_to_file(action_four_behavior, dir_path+'action_4.txt')


def split_seven_days_3_behavior():
    """
    获取7天，用户加入购物车的商品，排除已经购买的
    :return:
    """
    start_time = '2017-8-18 00:00:00'
    end_time = '2017-8-25 23:59:59'

    start_time = date_to_timestamp(start_time)
    end_time = date_to_timestamp(end_time)

    behaviors = process_user_behaviors()
    seven_days = filter_time(behaviors, start_time, end_time)
    shopping_cart = filter_user_action(3, seven_days)
    purchased = filter_user_action(4, seven_days)
    del behaviors
    del seven_days
    _shopping = remove_purchased(purchased, shopping_cart)

    result = [(x[0], x[1]) for x in _shopping]
    output.output_result(result)


if __name__ == '__main__':
    split_action_behaviors()
    split_seven_days_3_behavior()




















