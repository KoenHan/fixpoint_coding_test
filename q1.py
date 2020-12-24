# -*- coding: utf-8 -*-
import argparse

import utils as U
from generate_log import generateLogFile

def solve(ans, file_path) :
    file_lines = []
    with open(file_path) as f :
        file_lines = f.readlines()
    for line in file_lines :
        date, address, res_time = line.strip().split(',')
        if address not in ans :
            ans[address] = [] # 故障期間の日付(故障開始日時，故障終了日時が交互に入る)
        if len(ans[address])%2 == 0 and res_time == '-' :
            ans[address].append(date)
        elif len(ans[address])%2 and res_time != '-' :
            ans[address].append(date)

def outputAns(ans) :
    for address, failed_date in ans.items() :
        num = len(failed_date)
        print('IP: '+address)
        print('合計故障回数: '+str((num + 1)//2))
        for cnt in range(num) :
            if cnt%2 == 0 : print('\t故障期間'+str(cnt//2+1)+': '+U.outputDate(failed_date[cnt])+' ~ ', end='')
            else : print(U.outputDate(failed_date[cnt]))
        if num%2 : print(U.LOG_END) # 最後の要素が故障開始時間の時，ログだけでは故障終了時間が不明であることを表示する
        print()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-agl', '--auto_gen_log', help=U.AGL_HELP, action='store_true')
    parser.add_argument('-lfp', '--log_file_path', help=U.LFP_HELP, default='./log_for_q1.txt')
    parser.add_argument('-lfl', '--log_file_lines', help=U.LFL_HELP, type=int, default=100)
    args = parser.parse_args()

    if args.auto_gen_log :
        generateLogFile(args.log_file_path, args.log_file_lines, [80, 15, 5])

    ans = {}
    solve(ans, args.log_file_path)
    outputAns(ans)