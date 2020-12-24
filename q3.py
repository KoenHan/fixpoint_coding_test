# -*- coding: utf-8 -*-
import argparse

import utils as U
from generate_log import generateLogFile

def solve(ans, file_path, args_N, args_m, args_t) :
    file_lines = []
    with open(file_path) as f :
        file_lines = f.readlines()
    for line in file_lines :
        date, address, res_time = line.strip().split(',')
        if address not in ans :
            ans[address] = {
                "fail_cnt" : 0,     # タイムアウト回数のカウント
                "rs_time_vec" : [], # 直近m回の応答結果
                "failed_date" : [], # 故障期間の日付(故障開始日時，故障終了日時が交互に入る)
                "over_date" : []    # 過負荷期間の日付(過負荷開始日時，過負荷終了日時が交互に入る)
            }

        # 故障状態の記録
        if res_time == '-' :
            ans[address]["fail_cnt"] += 1
            if len(ans[address]["failed_date"])%2 == 0 : ans[address]["failed_date"].append(date)
            ans[address]["rs_time_vec"].clear() # 過負荷状態の次の状態が故障と考える
        else :
            if len(ans[address]["failed_date"])%2 :
                if ans[address]["fail_cnt"] < args_N : ans[address]["failed_date"].pop()
                else : ans[address]["failed_date"].append(date)
                ans[address]["fail_cnt"] = 0
            ans[address]["rs_time_vec"].append(int(res_time))
            if(len(ans[address]["rs_time_vec"]) > args_m) :
                ans[address]["rs_time_vec"].pop(0)

        # 過負荷状態の記録
        if(args_m == 0) : continue
        rt_mean = sum(ans[address]["rs_time_vec"])/args_m
        if len(ans[address]["over_date"])%2 == 0 and rt_mean >= args_t :
            ans[address]["over_date"].append(date)
        elif len(ans[address]["over_date"])%2 and rt_mean < args_t :
            ans[address]["over_date"].append(date)

    for fail_info in ans.values() :
        if len(fail_info["failed_date"])%2 and fail_info["fail_cnt"] < args_N :
            fail_info["failed_date"].pop()

def outputAns(ans) :
    for address, fail_info in ans.items() :
        print(address)
        for key, value in fail_info.items() :
            output_type = ''
            if key == "failed_date" : output_type = '故障'
            elif key == "over_date" : output_type = '過負荷'
            else : continue
            num = len(value)
            print('合計'+output_type+'回数: '+str((num + 1)//2))
            for cnt in range(num) :
                if cnt%2 == 0 : print('\t'+output_type+'期間'+str(cnt//2+1)+': '+U.outputDate(value[cnt])+' ~ ', end='')
                else : print(U.outputDate(value[cnt]))
            if num%2 : print(U.LOG_END)
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-N", help="設問2のN", type=int, default=1)
    parser.add_argument("-m", help="設問3のm", type=int, default=0)
    parser.add_argument("-t", help="設問3のt", type=int, default=0)
    parser.add_argument('-agl', '--auto_gen_log', help=U.AGL_HELP, action='store_true')
    parser.add_argument('-lfp', '--log_file_path', help=U.LFP_HELP, default='./log_for_q3.txt')
    parser.add_argument('-lfl', '--log_file_lines', help=U.LFL_HELP, type=int, default=200)
    args = parser.parse_args()

    if args.auto_gen_log :
        generateLogFile(args.log_file_path, args.log_file_lines, [2, 2, 1])

    ans = {}
    solve(ans, args.log_file_path, args.N, args.m, args.t)
    outputAns(ans)
