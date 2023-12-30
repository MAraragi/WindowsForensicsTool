import os
import time
from datetime import datetime, timedelta, timezone


class FolderMonitor:

    def __init__(self, root_path: str):
        self.root_path = root_path
        self.is_valid = True
        self.file_tree = {}
        if not os.path.isdir(root_path):
            print(f"路径\"{root_path}\"上不存在文件夹")
            self.is_valid = False
        else:
            self.initialize()

    def getFileTree(self):
        return self.file_tree

    # 初始化文件树
    def initialize(self):
        if not self.is_valid:
            return None
        self.file_tree = {}

        def getFormatTime(path: str, mode='c'):
            float_time = 0
            if mode == 'c':
                float_time = os.path.getctime(path)
            elif mode == 'm':
                float_time = os.path.getmtime(path)
            elif mode == 'a':
                float_time = os.path.getatime(path)
            create_utc_time = datetime.utcfromtimestamp(float_time)
            tz = timezone(timedelta(hours=8))
            create_local_time = create_utc_time.replace(tzinfo=timezone.utc).astimezone(tz)
            return create_local_time.strftime('%Y-%m-%d %H:%M:%S')

        # 递归建立文件树
        def createFileTree(folder_path):
            # 文件树基本单元基本结构{inode, filename, type(folder/file), children(if type is folder)}
            folder_status = os.stat(folder_path)
            file_tree = {'inode': folder_status.st_ino,
                         'name': folder_path,
                         'type': 'folder',
                         'create_time': getFormatTime(folder_path, mode='c'),
                         'modify_time': getFormatTime(folder_path, mode='m'),
                         'access_time': getFormatTime(folder_path, mode='a'),
                         'is_hidden': folder_status.st_file_attributes & 2 != 0,
                         'children': []}
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    file_status = os.stat(item_path)
                    file_tree['children'].append({'inode': file_status.st_ino,
                                                  'name': item,
                                                  'type': 'file',
                                                  'create_time': getFormatTime(item_path, mode='c'),
                                                  'modify_time': getFormatTime(item_path, mode='m'),
                                                  'access_time': getFormatTime(item_path, mode='a'),
                                                  'is_hidden': file_status.st_file_attributes & 2 != 0,
                                                  })
                elif os.path.isdir(item_path):
                    file_tree['children'].append(createFileTree(item_path))
            return file_tree

        # 建立文件树并保存在公有变量self.file_tree中
        self.file_tree = createFileTree(self.root_path)

    def getUpdates(self):

        if not self.is_valid:
            return None

        file_previous_status = []
        file_current_status = []

        def traverse(tree_node, file_status_set):
            if tree_node['is_hidden']:
                return
            file_status_set.append([tree_node['inode'],
                                    tree_node['name'],
                                    tree_node['type'],
                                    tree_node['create_time'],
                                    tree_node['modify_time'],
                                    tree_node['access_time'],
                                    0])
            for child in tree_node['children']:
                if child['is_hidden']:
                    continue
                if len(child['name']) > 4 and child['name'][-4:] == ".tmp":
                    continue
                if child['type'] == 'folder':
                    traverse(child, file_status_set)
                else:
                    file_status_set.append([child['inode'],
                                            tree_node['name'] + "\\" + child['name'],
                                            child['type'],
                                            child['create_time'],
                                            child['modify_time'],
                                            child['access_time'],
                                            0])

        traverse(self.file_tree, file_previous_status)
        self.initialize()
        traverse(self.file_tree, file_current_status)
        file_previous_status.sort(key=lambda x: x[0])
        file_current_status.sort(key=lambda x: x[0])

        add_files = []
        rename_files = []
        modify_files = []
        delete_files = []
        visit_files = []
        move_files = []

        for i in file_current_status:
            for j in file_previous_status:
                if j[6] == 1:
                    continue
                if j[6] == 0 and (i[0] == j[0] or i[1] == j[1]):
                    i[6] = j[6] = 1
                    if i[1] != j[1]:
                        i_path = i[1].split("\\")
                        j_path = j[1].split("\\")
                        if len(i_path) == len(j_path) and i_path[:-1] == j_path[:-1]:
                            rename_files.append([j, i])
                        else:
                            move_files.append([j, i])
                    elif i[2] != "folder":
                        if i[4] != j[4]:
                            modify_files.append(i)
                        elif i[5] != j[5]:
                            visit_files.append(i)
            if i[6] == 0:
                add_files.append(i)
        for j in file_previous_status:
            if j[6] == 0:
                delete_files.append(j)

        return add_files, rename_files, modify_files, delete_files, visit_files, move_files


if __name__ == "__main__":
    monitored_folder_path = "C:\\Users\\admin\\Desktop\\forensics_test"
    folder_monitor = FolderMonitor(monitored_folder_path)
    tree = folder_monitor.getFileTree()

    """
    # 递归遍历文件树
    def traverse_file_tree(file_tree):
        print(f"{file_tree['inode']}, "
              f"{file_tree['name']}, "
              f"{file_tree['type']}, "
              f"{file_tree['create_time']}, "
              f"{file_tree['modify_time']}, "
              f"{file_tree['access_time']}")

        for child in file_tree['children']:
            if child['type'] == 'folder':
                traverse_file_tree(child)
            else:
                print(f"{child['inode']}, "
                      f"{file_tree['name']}\\{child['name']}, "
                      f"{child['type']}, "
                      f"{child['create_time']}, "
                      f"{child['modify_time']}, "
                      f"{child['access_time']}")

    traverse_file_tree(tree)#"""

    #"""
    output_prefix = ["add", "rename", "modify", "delete", "visit", "move"]
    while 1:
        results = folder_monitor.getUpdates()
        if not results:
            break
        for i in range(len(results)):
            for j in results[i]:
                #"""
                if i == 1 or i == 5:
                    print(f"{output_prefix[i]} {j[0][2]}: {j[0][1]}-->{j[1][1]}")
                else:
                    print(f"{output_prefix[i]} {j[2]}:  {j[1]}")#"""
        time.sleep(2) #"""
