# -*- coding: utf-8 -*-
import datetime
import random

from utils import IP_NETS

# ipアドレスの生成
def generateIPAddress() :
    address = []
    for net in IP_NETS :
        prefix = net[-1]
        for _ in range(random.randint(2, 3)) :
            while True :
                ip = net[0:4]
                host = random.randint(1, (1<<(32 - prefix)) - 2)
                for shift in range(0, 25, 8) :
                    ip[3 - shift//8] += (host&(255<<shift))>>shift
                ip_str = '.'.join(map(str, ip))+'/'+str(prefix)
                if ip_str not in address :
                    address.append(ip_str)
                    break
    return address

# ログファイルの生成
def generateLogFile(file_path, file_total_line, state_weights) :
    # 設定
    state = [1, 2, 3] # ping応答が[早い, 遅い, タイムアウト]
    address = generateIPAddress()

    # ログファイル生成
    log_time = datetime.datetime.now()
    log_time -= datetime.timedelta(days=365)
    log = []
    address_num = len(address)
    pre_ip = address[0][0:2]
    for cnt in range(file_total_line) :
        ip = address[cnt%address_num]
        # ログの日時間隔はあまり重要ではないと考えたため，
        # IPアドレスの先頭2文字が前のIPアドレスと一致なら10秒，そうでないなら100秒にした
        log_time += datetime.timedelta(seconds=10 if(pre_ip[0:2] == ip[0:2]) else 100)
        pre_ip = ip
        st = random.choices(state, weights=state_weights)[0]
        rp_time = '-'
        if st == 1 :
            rp_time = str(random.randint(1, 10))
        elif st == 2 :
            rp_time = str(random.randint(300, 600))
        log.append(log_time.strftime('%Y%m%d%H%M%S')+','+ip+','+rp_time+'\n')
    with open(file_path, 'w') as f:
        f.writelines(log)

if __name__ == "__main__":
    file_path = './log_sample.txt'
    file_total_line = 100
    state_weights = [7, 2, 1]
    generateLogFile(file_path, file_total_line, state_weights)
