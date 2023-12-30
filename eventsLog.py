import win32evtlog


class eventsLogs:
    word_logs = []
    security_log = []
    user_logs = []

    def __init__(self):
        self.word_logs = eventsLogs.getLogs('OAlerts', eventsLogs.wordFilter)
        self.powerpoint_logs = eventsLogs.getLogs('OAlerts', eventsLogs.powerpointFilter)
        self.excel_logs = eventsLogs.getLogs('OAlerts', eventsLogs.excelFilter)

    def bootFilter(event):
        if event.SourceName == 'Microsoft-Windows-Kernel-General' and event.EventID == 1:
            return True
        else:
            return False

    def wordFilter(event):
        data = event.StringInserts
        if data:
            for msg in data:
                if msg.find('Word')!=-1:
                    return True
        return False

    def powerpointFilter(event):
        data = event.StringInserts
        if data:
            for msg in data:
                if msg.find('PowerPoint')!=-1:
                    return True
        return False

    def excelFilter(event):
        data = event.StringInserts
        if data:
            for msg in data:
                if msg.find('Excel')!=-1:
                    return True
        return False


    def getLogs(logtype, logFilter):
        server = 'localhost' # name of the target computer to get event logs
        #logtype = 'OAlerts' # 'Application' # 'Security'
        hand = win32evtlog.OpenEventLog(server,logtype)
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ
        logs = set()
        i=0
        while True:
            events = win32evtlog.ReadEventLog(hand, flags,0)
            i += len(events)
            if events:
                for event in events:
                    if logFilter(event):
                        edetail = ""
                        data = event.StringInserts
                        if data:
                            for msg in data:
                                edetail += msg
                        logs.add((str(event.TimeGenerated), event.SourceName, event.EventID, edetail))
            else:
                break
        win32evtlog.CloseEventLog(hand)
        return logs

