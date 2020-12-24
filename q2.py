# -*- coding: utf-8 -*-
import argparse

import utils as U
from generate_log import generateLogFile

def solve(ans, file_path, args_N) :
    file_lines = []
    with open(file_path) as f :
        file_lines = f.readlines()
    for line in file_lines :
        date, address, res_time = line.strip().split(',')
        if address not in ans :
            ans[address] = {
                "fail_cnt" : 0,     # タイムアウト回数のカウント
                "failed_date" : []  # 故障期間の日付(故障開始日時，故障終了日時が交互に入る)
            }
        if res_time == '-' :
            ans[address]["fail_cnt"] += 1
            if len(ans[address]["failed_date"])%2 == 0 : ans[address]["failed_date"].append(date)
        elif len(ans[address]["failed_date"])%2 :
            if ans[address]["fail_cnt"] < args_N : ans[address]["failed_date"].pop()
            else : ans[address]["failed_date"].append(date)
            ans[address]["fail_cnt"] = 0
    for fail_info in ans.values() : # 最後に記録した日時が故障開始日時の時，連続故障回数がN以下なら不要となるので削除
        if len(fail_info["failed_date"])%2 and fail_info["fail_cnt"] < args_N :
            fail_info["failed_date"].pop()

def outputAns(ans) :
    for address, fail_info in ans.items() :
        num = len(fail_info["failed_date"])
        print(address)
        print('合計故障回数: '+str((num + 1)//2))
        for cnt in range(num) :
            if cnt%2 == 0 : print('\t故障期間'+str(cnt//2+1)+': '+U.outputDate(fail_info["failed_date"][cnt])+' ~ ', end='')
            else : print(U.outputDate(fail_info["failed_date"][cnt]))
        if num%2 : print(U.LOG_END)
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-N", help="設問のN", type=int, default=1)
    parser.add_argument('-agl', '--auto_gen_log', help=U.AGL_HELP, action='store_true')
    parser.add_argument('-lfp', '--log_file_path', help=U.LFP_HELP, default='./log_for_q2.txt')
    parser.add_argument('-lfl', '--log_file_lines', help=U.LFL_HELP, type=int, default=200)
    args = parser.parse_args()

    if args.auto_gen_log :
        generateLogFile(args.log_file_path, args.log_file_lines, [1, 0, 1])

    ans = {}
    solve(ans, args.log_file_path, args.N)
    outputAns(ans)
