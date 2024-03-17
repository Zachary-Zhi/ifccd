import os
import threading
from bson.objectid import ObjectId
from collections import deque

ifccd_task_queueLock = threading.Lock()
enhance_task_queueLock = threading.Lock()

class ifccd_task_priority_queue(object):

    def __init__(self):
        self.__ifccd_task_priority_deque = deque()

    def get_ifccd_task_priority_queue(self):
        return self.__ifccd_task_priority_deque

    def add_ifccd_task_to_queue(self, new_task):
        ifccd_task_queueLock.acquire()
        self.__ifccd_task_priority_deque.append(new_task)
        ifccd_task_queueLock.release()

    def delete_from_ifccd_task_queue(self, task_id):
        tmp_flag = False
        ifccd_task_queueLock.acquire()
        for item in self.__ifccd_task_priority_deque:
            if item.task_id == ObjectId(task_id):
                self.__ifccd_task_priority_deque.remove(item)
                tmp_flag = True
                break

        ifccd_task_queueLock.release()
        self.show_que()
        return tmp_flag

    def change_pos_in_ifccd_queue(self, task_id, sequence):
        tmp_task = None
        tmp_flag = False
        ifccd_task_queueLock.acquire()
        if not self.__ifccd_task_priority_deque:
            ifccd_task_queueLock.release()
            return False

        for item in self.__ifccd_task_priority_deque:
            if item.task_id == ObjectId(task_id):
                tmp_task = item
                self.__ifccd_task_priority_deque.remove(item)
                tmp_flag = True
                break

        if tmp_flag:
            self.__ifccd_task_priority_deque.insert(sequence, tmp_task)
        ifccd_task_queueLock.release()
        return tmp_flag

    def get_nums(self):
        return len(self.__ifccd_task_priority_deque)

    def show_que(self):
        ifccd_task_queueLock.acquire()
        que = self.__ifccd_task_priority_deque
        print(que)
        ifccd_task_queueLock.release()

    def get_que(self):
        return self.__ifccd_task_priority_deque

    def get_pos_by_task_id(self, task_id):
        ifccd_task_queueLock.acquire()
        pos = 0
        if not self.__ifccd_task_priority_deque: # 如果没找到，返回-1
            ifccd_task_queueLock.release()
            return pos
        for item in self.__ifccd_task_priority_deque:
            pos = pos + 1
            if item.task_id == ObjectId(task_id):
                ifccd_task_queueLock.release()
                return pos
        ifccd_task_queueLock.release()
        return pos

class enhance_task_priority_queue(object):
    def __init__(self):
        self.__enhance_task_priority_queue = deque()

    def get_enhance_task_priority_queue(self):
        return self.__enhance_task_priority_queue

    def show_que(self):
        enhance_task_queueLock.acquire()
        que = self.__enhance_task_priority_queue
        print(que)
        enhance_task_queueLock.release()

    def add_enhance_task_to_queue(self, new_task):
        enhance_task_queueLock.acquire()
        self.__enhance_task_priority_queue.append(new_task)
        enhance_task_queueLock.release()

    def delete_from_enhance_task_queue(self, task_id):
        tmp_flag = False
        enhance_task_queueLock.acquire()
        for item in self.__enhance_task_priority_queue:
            if item.task_id == ObjectId(task_id):
                self.__enhance_task_priority_queue.remove(item)
                tmp_flag = True
                break
        enhance_task_queueLock.release()
        self.show_que()
        return tmp_flag

    def change_pos_in_enhance_queue(self, task_id, sequence):
        tmp_task = None
        tmp_flag = False
        enhance_task_queueLock.acquire()
        if not self.__enhance_task_priority_queue:
            # 如果队列为空
            enhance_task_queueLock.release()
            return False
        for item in self.__enhance_task_priority_queue:
            if item.task_id == ObjectId(task_id):
                tmp_task = item
                self.__enhance_task_priority_queue.remove(item)
                tmp_flag = True
                break
        if tmp_flag:
            self.__enhance_task_priority_queue.insert(sequence, tmp_task)
        enhance_task_queueLock.release()
        return tmp_flag

    def get_nums(self):
        enhance_task_queueLock.acquire()
        res = len(self.__enhance_task_priority_queue)
        enhance_task_queueLock.release()
        return res

    def get_que(self):
        return self.__enhance_task_priority_queue

    def get_pos_by_task_id(self, task_id):
        enhance_task_queueLock.acquire()
        pos = 0
        if not self.__enhance_task_priority_queue: # 如果没找到，返回-1
            enhance_task_queueLock.release()
            return pos
        for item in self.__enhance_task_priority_queue:
            pos = pos + 1
            if item.task_id == ObjectId(task_id):
                enhance_task_queueLock.release()
                return pos
        enhance_task_queueLock.release()
        return 0