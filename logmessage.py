# -*- coding: utf-8 -*-
from datetime import datetime
import sys

yyyy = str(datetime.now().year)
mm = str(datetime.now().month)
dd = str(datetime.now().day)
output_file = open('log/' + yyyy + '-' + mm + '-' + dd + '.log', 'w')


def logprint(message):
    global output_file

    message = str(message)

    # yyyy
    yyyy = str(datetime.now().year)

    # mm
    mm = str(datetime.now().month)
    if len(mm) == 1:
        mm = '0' + mm

    # dd
    dd = str(datetime.now().day)
    if len(dd) == 1:
        dd = '0' + dd

    # HH
    HH = str(datetime.now().hour)
    if len(HH) == 1:
        HH = '0' + HH

    # MM
    MM = str(datetime.now().minute)
    if len(MM) == 1:
        MM = '0' + MM

    # SS
    SS = str(datetime.now().second)
    if len(SS) == 1:
        SS = '0' + SS

    print_message = (
            yyyy + '-' +
            mm + '-' +
            dd + 'T' +
            HH + ':' +
            MM + ':' +
            SS + ' ' +
            message
            )

    print(print_message)
    # ファイルに書き出す
    # flushで強制的に書き込む
    output_file.write(print_message + '\n')
    output_file.flush()
