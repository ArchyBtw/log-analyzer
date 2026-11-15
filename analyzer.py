from operator import itemgetter
import subprocess

def logs():
    try:
        result = subprocess.run(['journalctl', '-b'], capture_output=True, text=True)
        b = result.returncode
        if b != 0:
            return b, result.stderr
        return b, result.stdout.splitlines()
    except OSError:
        b = 1
        return b, 'Ошибка системы, у вас не systemd'

def exten(strk):
    ls = strk.split()
    if len(ls) < 5:
        return None
    else:
        return ls[4].rstrip(':').split('[')[0]

def poisk(file):
    words = []
    for line in file:
        proc = exten(line)
        if proc is None:
            continue
        else:
            words.append(proc)
    return words

def counter(ext):
    chet = {}
    words = poisk(ext)
    for word in words:
        if word not in chet:
            chet[word] = 1
        else: 
            chet[word] += 1
    chet = sorted(chet.items(), key=itemgetter(1), reverse=True)
    chet = dict(chet[:5])
    return chet


def sudo(log):
    count = 0
    count_auth_fail = 0
    dict_command = {}
    for line in log:
        if 'sudo' == exten(line):
            count += 1
            if 'authentication failure' in line:
                count_auth_fail += 1
            elif 'COMMAND=' in line:
                command = line.split('COMMAND=')[-1]
                if command not in dict_command:
                    dict_command[command] = 1
                else:
                    dict_command[command] += 1
    return count, count_auth_fail, dict_command


def output():
    pro, file1 = logs()
    if pro != 0:
        print(file1)
        return
    print('Топ программ:')
    for i, n in counter(file1).items():
        print(f'{i}: {n}')

    count, count_auth_fail, dict_command = sudo(file1)
    print('\nsudo:')
    print(f'Записи: {count}')
    print(f'Неудачных паролей: {count_auth_fail}')
    print('Команды:')
    for i, n in dict_command.items():
        print(f'{i}: {n}')

output()