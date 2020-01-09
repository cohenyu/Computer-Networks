from socket import socket, AF_INET, SOCK_DGRAM
import sys

users = {}
msgs = {}


# This function parses the massage of the client
def parse_msg(data):
    # check if the massage is by the rule
    try:
        task_num = int(data.split()[0])
    except:
        task_num = -1
    # and if there is a message after a number
    try:
        data_msg = data.split(None, 1)[1]
    except:
        data_msg = ''
    return task_num, data_msg


# This function checks if client is already in the group
def isInGroup(info):
    if info in users:
        return True
    else:
        return False


# This function send massage to the client if his massage is illegal
def illegal(s, user_info, msg):
    s.sendto("Illegal request", user_info)


# This function matches to task 1 - when client want to join the group
def add_user(s, sender_info, new_name):
    if isInGroup(sender_info) or (new_name == ""):
        illegal(s, sender_info, new_name)
        return

    names = ''
    msgs.update({sender_info: ''})
    # for each user in the group create the message that a new client has joined
    for user_info, user_name in users.items():
        if user_info != sender_info:
            msgs[user_info] = msgs[user_info] + new_name + "has joined\n"
            names += user_name + ', '
    # if its the last one we delete the ,
    if users:
        names = names[:(len(names) - 2)]
    s.sendto(names, sender_info)
    users.update({sender_info: new_name})


# this function send a massage to all the clients
def send_msg(s, sender_info, msg):
    # if the client is not in the group he can't send the massage
    if not(isInGroup(sender_info)) or (msg == ''):
        illegal(s, sender_info, msg)
        return
    for user_info, user_name in users.items():
        if user_info != sender_info:
            msgs[user_info] = msgs[user_info] + users[sender_info] + ': ' + msg + "\n"
    # update the client with all the massage
    update(s, sender_info)


# This function matches to task - 3 when client want to change his name
def change_name(s, sender_info, new_name):
    # if the client is not in the group he can't change his name
    if not(isInGroup(sender_info)) or (new_name == ''):
        illegal(s, sender_info, new_name)
        return

    for user_info, user_name in users.items():
        if user_info != sender_info:
            msgs[user_info] = msgs[user_info] + users[sender_info] + ' changed his name to ' + new_name + "\n"

    users[sender_info] = new_name
    # update the client with all the massage
    update(s, sender_info)


# This function matches to task - 4 when client want to leave the group
def delete_user(s, sender_info, msg):
    # if the client is not in the group he can't leave the group
    if not(isInGroup(sender_info)) or (msg != ''):
        illegal(s, sender_info, msg)
        return

    name = users[sender_info]
    del users[sender_info]
    del msgs[sender_info]
    for user_info, user_name in users.items():
        msgs[user_info] = msgs[user_info] + name + ' has left the group' + "\n"
    s.sendto('', sender_info)


# This function sends all the massage that wait for the client
def update(s, sender_info):
    msg = msgs[sender_info][:len(msgs[sender_info])-1]
    s.sendto(msg, sender_info)
    msgs[sender_info] = ''


# This function matches to task 5 - updating
def get_msg(s, sender_info, msg):
    if not(isInGroup(sender_info)) or (msg != ""):
        illegal(s, sender_info, msg)
    else:
        update(s, sender_info)


# This function starts to listen to clients and runs the function according to the received massage
def start_server(s):
    while True:
        data, sender_info = s.recvfrom(2048)
        task, msg = parse_msg(data)

        switcher = {
            1: add_user,
            2: send_msg,
            3: change_name,
            4: delete_user,
            5: get_msg
        }
        switcher.get(task, illegal)(s, sender_info, msg)


def main():
    # create the socket
    s = socket(AF_INET, SOCK_DGRAM)
    source_ip = '0.0.0.0'
    source_port = int(sys.argv[1])
    s.bind((source_ip, source_port))
    start_server(s)


if __name__ == "__main__":
    main()