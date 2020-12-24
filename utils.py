# ランダム生成されるIPアドレスのネットワークアドレスとプレフィックス長の設定
IP_NETS = [
    [10, 20, 0, 0, 16],
    [10, 21, 128, 0, 17],
    [192, 168, 1, 0, 24],
    [192, 168, 3, 128, 25]
]

AGL_HELP = 'テスト用ログファイルの自動生成指定フラグ'
LFP_HELP = 'ログファイルまでの絶対パスまたは相対パス'
LFL_HELP = 'ログファイルの行数'

LOG_END = '(UNKNOWN BECAUSE LOG END)'

def outputDate(date_str) :
    return date_str[0:4]+'/'+date_str[4:6]+'/'+date_str[6:8]+' '+date_str[8:10]+':'+date_str[10:12]+':'+date_str[12:14]