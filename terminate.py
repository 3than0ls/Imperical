import os
import time

def list_processes(name):
    os.system('tasklist /FI "IMAGENAME eq {}" > tmp.txt'.format(name))
    tmp = open('tmp.txt', 'r')
    processes = [list(i.split()) for i in tmp.readlines()[3:]]
    pids, pnames = [], []
    for proccess in processes:
        pnames.append(proccess[0])
        pids.append(proccess[1])
    return pids, pnames

def kill_proccess(pid):
    os.system('taskkill /f /pid {}'.format(pid))

pids, pnames = list_processes('pythonw.exe')

if __name__ == '__main__':
    if (len(pids) > 0): 
        for i in range(len(pids)):
            terminate = input('Are you sure you want to terminate proccess {} (Proccess ID: {})? (Y/N): '.format(pids[i], pnames[i]))
            if terminate.lower() == 'y':
                print('Terminating process in 5 seconds...')
                time.sleep(5)
                kill_proccess(pids[i])
            else:
                print('Cancelled termination of process')
    else:
        print("No pythonw.exe processes running.")