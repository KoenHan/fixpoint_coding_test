# -*- coding: utf-8 -*-
import argparse
import datetime

import utils as U
from generate_log import generateLogFile

# IPアドレスからネットワークアドレスを取得する関数
def getSubnetIP(address) :
    ip, prefix = address.split('/')
    ip_binary = 0
    for ip_part in ip.split('.') :
        ip_binary <<= 8
        ip_binary += int(ip_part)
    shift = 32 - int(prefix)
    ip_binary >>= shift
    ip_binary <<= shift
    subnet_str_vec = []
    for shift in range(24, -1, -8) :
        subnet_str_vec.append(str((ip_binary&(255<<shift))>>shift))
    return '.'.join(subnet_str_vec)+'/'+prefix

# サーバごとの故障・過負荷の記録
# q3のsolveを一部の変数名だけ変えたもの
def solveServer(server_ans, file_path, args_N, args_m, args_t) :
    file_lines = []
    with open(file_path) as f :
        file_lines = f.readlines()
    for line in file_lines :
        date, server, res_time = line.strip().split(',')
        if server not in server_ans :
            server_ans[server] = {
                "fail_cnt" : 0,     # タイムアウト回数のカウント
                "rs_time_vec" : [], # 直近m回の応答結果
                "failed_date" : [], # 故障期間の日付(故障開始日時，故障終了日時が交互に入る)
                "over_date" : []    # 過負荷期間の日付(過負荷開始日時，過負荷終了日時が交互に入る)
            }

        # 故障状態の記録
        if res_time == '-' :
            server_ans[server]["fail_cnt"] += 1
            if len(server_ans[server]["failed_date"])%2 == 0 :
                server_ans[server]["failed_date"].append(date)
            server_ans[server]["rs_time_vec"].clear() # 過負荷状態の次の状態が故障と考える
        else :
            if len(server_ans[server]["failed_date"])%2 :
                if server_ans[server]["fail_cnt"] < args_N : server_ans[server]["failed_date"].pop()
                else : server_ans[server]["failed_date"].append(date)
                server_ans[server]["fail_cnt"] = 0
            server_ans[server]["rs_time_vec"].append(int(res_time))
            if(len(server_ans[server]["rs_time_vec"]) > args_m) :
                server_ans[server]["rs_time_vec"].pop(0)

        # 過負荷状態の記録
        if(args_m == 0) : continue
        rt_mean = sum(server_ans[server]["rs_time_vec"])/args_m
        if len(server_ans[server]["over_date"])%2 == 0 and rt_mean >= args_t :
            server_ans[server]["over_date"].append(date)
        elif len(server_ans[server]["over_date"])%2 and rt_mean < args_t :
            server_ans[server]["over_date"].append(date)

    for fail_info in server_ans.values() :
        if len(fail_info["failed_date"])%2 and fail_info["fail_cnt"] < args_N :
            fail_info["failed_date"].pop()

def convertYMDHMS2Second(origin, date) :
    value = datetime.datetime(
        year=int(date[0:4]), month=int(date[4:6]), day=int(date[6:8]),
        hour=int(date[8:10]), minute=int(date[10:12]), second=int(date[12:14]))
    return (value - origin).total_seconds()

def convertSecond2YMDHMS(origin, second) :
    return origin + datetime.timedelta(seconds=second)

# サブネットワークごとの故障の記録
# サーバの故障結果から求める
def solveSubnet(ans) :
    server_subnet = {}
    subnet_server_fail = {}
    for server in ans['server'].keys() :
        subnet = getSubnetIP(server)
        server_subnet[server] = subnet
        if subnet not in ans['subnet'] :
            ans['subnet'][subnet] = [] # サブネットの故障期間の日付(故障開始日時，故障終了日時が交互に入る)
            subnet_server_fail[subnet] = {
                'server_num' : 0,   # サブネットに属しているサーバの数
                'failed_date' : []  # サブネットに属しているサーバの故障期間を全てまとめたリスト
            }
        subnet_server_fail[subnet]['server_num'] += 1

    # 各サーバの故障情報をそのサーバが属するサブネットごとに1つにまとめる
    origin = datetime.datetime(year=1, month=1, day=1) # 時間軸の原点
    for server, infos in ans['server'].items() :
        subnet = server_subnet[server]
        for idx in range(len(infos['failed_date'])) :
            t = 'e' if idx%2 else 's' # 故障開始なら's(=start)'，故障終了なら'e(=end)'
            subnet_server_fail[subnet]['failed_date'].append(
                (convertYMDHMS2Second(origin, infos['failed_date'][idx]), t))

    # 各サブネットに属している全てのサーバの故障期間情報からサブネットの故障期間を求める
    for subnet, infos in subnet_server_fail.items() :
        fail_server_cnt = 0
        infos['failed_date'].sort()
        for second, type in infos['failed_date'] :
            if type == 's' :
                fail_server_cnt += 1
                if fail_server_cnt == infos['server_num'] :
                    ans['subnet'][subnet].append(convertSecond2YMDHMS(origin, second))
            else :
                if len(ans['subnet'][subnet])%2 :
                    ans['subnet'][subnet].append(convertSecond2YMDHMS(origin, second))
                if fail_server_cnt > 0: fail_server_cnt -= 1

def outputAns(ans) :
    print('==========サーバ故障・過負荷情報==========')
    for address, infos in ans['server'].items() :
        print('IP: '+address)
        for key, value in infos.items() :
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
    print('==========サブネット故障情報==========')
    for subnet, fail_info in ans['subnet'].items() :
        num = len(fail_info)
        print('IP: '+subnet)
        print('合計故障回数: '+str((num + 1)//2))
        for cnt in range(num) :
            if cnt%2 == 0 : print('\t故障期間'+str(cnt//2+1)+': '+fail_info[cnt].strftime('%Y/%m/%d %H:%M:%S')+' ~ ', end='')
            else : print(fail_info[cnt].strftime('%Y/%m/%d %H:%M:%S'))
        if num%2 : print(U.LOG_END)
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-N", help="設問2のN", type=int, default=1)
    parser.add_argument("-m", help="設問3のm", type=int, default=0)
    parser.add_argument("-t", help="設問3のt", type=int, default=0)
    parser.add_argument('-agl', '--auto_gen_log', help=U.AGL_HELP, action='store_true')
    parser.add_argument('-lfp', '--log_file_path', help=U.LFP_HELP, default='./log_for_q4.txt')
    parser.add_argument('-lfl', '--log_file_lines', help=U.LFL_HELP, type=int, default=300)
    args = parser.parse_args()

    if args.auto_gen_log :
        generateLogFile(args.log_file_path, args.log_file_lines, [2, 4, 4])

    ans = {'server' : {}, 'subnet' : {}}
    solveServer(ans['server'], args.log_file_path, args.N, args.m, args.t)
    solveSubnet(ans)
    outputAns(ans)
