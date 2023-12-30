import os
import time
import sqlite3
import getpass
from collections import defaultdict


class BrowserHistoryReader:
    browser_path_tail = defaultdict(str, {"chrome": "AppData\\Local\\Google\\Chrome\\User Data\\Default\\History",
                                          "edge": "AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\History"})

    def __init__(self, browser_name="Chrome"):
        self.username = getpass.getuser()
        self.browser_name = browser_name.lower()
        self.browser_history_path = ""
        self.history_file_path_copy = ""
        self.records = []
        self.is_valid = True
        self.last_visit_time = ""
        if self.browser_path_tail[self.browser_name] == "":
            print("Sorry, this program doesn't support browser " + browser_name + ".")
            self.is_valid = False
        else:
            self.browser_history_path = "C:\\Users\\" + self.username + "\\" + self.browser_path_tail[self.browser_name]
            self.history_file_path_copy = self.browser_name + "_history"
        self.getRecentRecords()

    # 参数n表示返回记录的数量，类型为int，当小于0时查询所有历史记录，其值默认为-1
    # 返回字典形式的历史记录，按照访问时间由近及远排序，每一条记录的格式如下：
    # {"id": xxx, "url": xxx, "title": xxx, "visit_count": xxx, "last_visit_time": xxx}
    def getRecentRecords(self, n=-1):
        if not self.is_valid:
            return None
        # 因为用户访问浏览器的行为和python进程访问浏览器历史记录的行为会冲突，所以先将其复制一份再读之
        history = open(self.browser_history_path, 'rb')
        history_copy = open(self.history_file_path_copy, 'wb')
        history_copy.write(history.read())
        history.close()
        history_copy.close()
        # 读取SQLite所有记录并保存在records[]中
        connection = sqlite3.connect(self.history_file_path_copy)
        sqlite_cursor = connection.cursor()
        # SQL查询语句，另外实现查询n条的功能
        SQL_query_statement = "SELECT id,url,title,visit_count,last_visit_time from urls order by last_visit_time desc"
        SQL_query_statement += " LIMIT " + str(n) if n >= 0 else ""
        sqlite_cursor.execute(SQL_query_statement)
        records = []
        original_records = sqlite_cursor.fetchall()
        for unique_id, url, title, visit_count, last_visit_time in original_records:
            record = {"id": unique_id,
                      "url": url,
                      "title": title,
                      "visit_count": visit_count,
                      "last_visit_time": time.strftime("%Y-%m-%d %H:%M:%S",
                                                       time.localtime(last_visit_time / 1000000 - 11644473600))
                      if last_visit_time > 0 else 0}
            records.append(record)
        sqlite_cursor.close()
        connection.close()
        # 使用结束后立即删除临时SQLite文件
        os.remove(self.history_file_path_copy)
        if len(records) > 0:
            self.last_visit_time = records[0]["last_visit_time"]
        if n < 0:
            self.records = records
        return records

    # 获取当前更新的历史记录
    # 历史记录未改变时返回值为空列表
    def getUpdates(self):

        if not self.is_valid:
            return None

        # 将"%Y-%m-%d %H:%M:%S"格式的字符串拆解为[%Y,%m,%d,%H,%M,%S]格式的列表
        # 然后比较前一个时间和后一个时间谁更靠前
        def isTimeNearer(time_string_1, time_string_2):
            coarse_split = time_string_1.split(" ")
            time_1 = [*(coarse_split[0].split("-")), *(coarse_split[1].split(":"))]
            coarse_split = time_string_2.split(" ")
            time_2 = [*(coarse_split[0].split("-")), *(coarse_split[1].split(":"))]
            for i, j in zip(time_1, time_2):
                if i < j:
                    return -1
                elif i > j:
                    return 1
            return 0

        # 通过时间与先前相比是否更靠前来获取新访问的历史记录
        last_visit_time = self.last_visit_time
        self.getRecentRecords()
        updates = []
        for record in self.records:
            if isTimeNearer(record["last_visit_time"], last_visit_time) == 1:
                updates.append(record)
            else:
                break
        return updates


if __name__ == "__main__":
    browser = BrowserHistoryReader(browser_name="Chrome")
    # history_records = browser.getRecentRecords(n=12)
    # for row in history_records:
    #     print(row)
    updated_records = []
    while not updated_records:
        updated_records = browser.getUpdates()
    print("历史记录已改变")
    for row in updated_records:
        print(row)
