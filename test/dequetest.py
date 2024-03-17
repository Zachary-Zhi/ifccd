from collections import deque

deq = deque()


def delete_from_ifccd_task_queue(task_id):
    for item in deq:
        if item == task_id:
            deq.remove(item)
            break

def change_pos_in_ifccd_queue(task_id, sequence):
    tmp_id = -1
    for item in deq:
        if item == task_id:
            tmp_id = item
            deq.remove(item)
            break

    deq.insert(sequence, tmp_id)

for i in range(10):
    deq.append(i+1)
print(deq)
deq.insert(3, 100)
print(deq)
change_pos_in_ifccd_queue(100, 7)
print(deq)