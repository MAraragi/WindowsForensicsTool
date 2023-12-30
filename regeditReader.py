import winreg
import re
from datetime import datetime, timedelta, timezone


class regeditReader:

    mru_set = set()

    def __init__(self):
        self.mru_set = set()
        root_path = "SOFTWARE\\Microsoft\\Office"
        version = '16.0'
        softwares = ['Word', 'PowerPoint', 'Excel']

        for software in softwares:
            id_path = root_path + "\\" + version + "\\" + software + "\\User MRU"
            LiveId = regeditReader.findKey(id_path, regeditReader.idFilter)
            mru_path = id_path + "\\" + LiveId + "\File MRU"
            mru_list = regeditReader.getKeys(mru_path)
            #print(regeditReader.convert(mru_list))
            self.mru_set = self.mru_set.union(regeditReader.convert(mru_list, software))

    def winTimeConvert(byte_time):
        nt_timestamp = int(byte_time, 16)
        epoch = datetime(1601, 1, 1, 0, 0, 0)
        nt_datetime = epoch + timedelta(microseconds=nt_timestamp / 10)
        tz = timezone(timedelta(hours=+16))
        nt_datetime = nt_datetime.astimezone(tz)
        return str(nt_datetime.strftime("%Y-%m-%d %H:%M:%S"))

    def idFilter(sub_key):
        if sub_key.startswith('LiveId'):
            return True
        else:
            return False

    def findKey(key_path, keyFiler):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
        except WindowsError as e:
            # print(e)
            pass
        i = 0
        for i in range(10):
            try:
                sub_key = winreg.EnumKey(key, i)
                if keyFiler(sub_key):
                    winreg.CloseKey(key)
                    return sub_key
            except WindowsError as e:
                winreg.CloseKey(key)
                break
        return ""

    def getKeys(key_path):
        keys = []
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
        except WindowsError as e:
            print(e)
        i = 0
        for i in range(0,1000):
            try:
                key_value = winreg.EnumValue(key, i)
                keys.append(key_value)
            except WindowsError as e:
                winreg.CloseKey(key)
                break
        return keys
    
    def convert(mru_list, software):
        mru_set = set()
        for l in mru_list:
            value = l[1]
            try:
                path = value.split('*')[1]
            except:
                continue
            values = re.findall(r'\[(.*?)\]',value)
            time_convert = regeditReader.winTimeConvert(values[1][1:])
            mru_set.add((time_convert, 'REGEDIT-' + software + '/User MRU/File MRU', 0, path))
        return mru_set
