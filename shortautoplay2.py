import re
import subprocess
import time
import uiautomator2 as u2
import csv
import pandas as pd

d = u2.connect('989e1592') #连接设备，默认为一个USB设备

#播放短剧，输出日志信息
def play_shortvideo(csv_file, device_id,logcat_name):
    results = []
    total_play=0
    fail_play=0
    fail_count = 0
    # 循环执行次数
    # for i in range(5):
    with open(csv_file, newline='', encoding='utf-8-sig') as file:
        reader = csv.reader(file)

        for count,row in enumerate(reader):
            total_play += 1
            subprocess.run(f"adb -s {device_id} logcat -c", shell=True, check=True)
            subprocess.run(
                ['adb','-s',device_id,'shell','am', 'start', '-a', 'android.intent.action.VIEW', '-d', 'mv://VideoShortPlaylet?url=entity/' + row[0] + '&id=' + row[0]])
            time.sleep(5)

            get_logcat(device_id,logcat_name)  # 获取日志
            error_occured, error_type, error_msg = check_for_log(logcat_name)  # 判断日志信息

            #输出日志
            if error_occured:
                fail_play += 1
                fail_count += 1
                results.append([row[0], '播放失败,失败日志: ErrorType:{},ErrorMsg:{},当前失败次数:{}'.format(error_type, error_msg,fail_count)])
            else:
                results.append([row[0], '正常播放'])

            time.sleep(2)
            d.app_stop('com.miui.video')
            time.sleep(2)

    #新数据写入csv文件
    df = pd.DataFrame(results)
    df.to_csv(csv_file, index=False, header=False,encoding='utf-8-sig')

    #计算错误率
    error_rate=(fail_play/total_play) * 100 if total_play > 0 else 0
    #把错误率写入csv末尾
    with open(csv_file, 'a', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(['播放失败次数：', fail_play])
        writer.writerow(['播放总次数:',total_play])
        writer.writerow(['错误率：', f'{error_rate:.2f}%'])
#获取日志
def get_logcat(device_id,logcat_name):
    subprocess.run(f"adb -s {device_id} logcat -d > {logcat_name}", shell=True, check=True)
    time.sleep(2)

#通过日志判断是否播放成功，失败的话输出Errortype和Errormsg
def check_for_log(logcat_name):
    error_type, error_msg = None, None
    with open(logcat_name, 'r', encoding='utf-8-sig', errors='ignore') as file:
        for line in file:
            if 'onerror' in line.lower():
                log_line = line.strip()
                error_type_pattern = re.compile(r"errorType=(\d+)")
                error_msg_pattern = re.compile(r"errorMsg='([^']*)'")

                error_type_match = error_type_pattern.search(log_line)
                error_msg_match = error_msg_pattern.search(log_line)

                if error_type_match and error_msg_match:
                    error_type = error_type_match.group(1)
                    error_msg = error_msg_match.group(1)
                    return True, error_type, error_msg
    return False, error_type, error_msg

if __name__ == '__main__':
    csv_file = "C:\\Users\\Administrator\\Desktop\\短剧.csv"        #!!!只需要改本地csv路径和设备id即可运行，csv文件只需要第一列放视频ID即可
    device_id = '989e1592'
    logcat_name = 'logcat.log'
    play_shortvideo(csv_file,device_id,logcat_name)
