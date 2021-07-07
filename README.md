# WiFiCrackPy

WiFiCrackPy demonstrates some of the security flaws associated with WPA(2) networks by performing simple and efficient cracking. The tool is for educational purposes and should not be misused.

There are two independent scripts included in this repository. The first (`WiFiCrackPy.py`) captures the necessary Wi-Fi packets associated with WPA(2) handshakes and then utilises [hashcat](https://github.com/hashcat/hashcat) to attempt to extract the hashed passkey.

_**Under development:**_ The second script (`WiFiCrackPy-DeAuth.py`) is a modified version of the first script that speeds up the process of packet capturing by utilising [`zizzania`](https://github.com/cyrus-and/zizzania) to send DeAuth frames to the stations whose handshake is needed. However, this script currently has compatibility issues with newer devices, including all Apple silicon MacBooks.

## Prerequisites

You must have `python3` installed. You will need to install any other outstanding requirements:

| Command | Installation |
| --- | --- |
| `hashcat`, `mergecap` | Install via [brew](https://brew.sh) by running `brew install hashcat wireshark` |
| `~/hashcat-utils/src/cap2hccapx.bin` | Clone [this](https://github.com/hashcat/hashcat-utils) repository then run `make` from inside `src` |

Only needed for `WiFiCrackPy-DeAuth.py`:

| Command | Installation |
| --- | --- |
| `libpcap`, `wget` | Install via [brew](https://brew.sh) by running `brew install libpcap wget` |
| `~/zizzania/src/zizzania` | Clone [this](https://github.com/cyrus-and/zizzania) repository then run `make -f config.Makefile && make` from the same directory |

## Usage

Download with:
```
git clone https://github.com/Tommrodrigues/WiFiCrackPy.git
pip3 install -r requirements.txt
```

Run from the same directory with:
```
python3 WiFiCrackPy.py
```

The script is fairly easy to use, simply run it using the command above and enter your `sudo` password when prompted. Here are some flags you can add:

| Flag | Description |
| --- | --- |
| `-w <wordlist>` | Wordlist: Define a wordlist path (script will prompt you otherwise) |
| `-i <interface>` | Interface: Set Wi-Fi interface (script can auto-detect default interface) |
| `-m <method>` | Method: Define the attack method (script will prompt you otherwise) |
| `-p <pattern>` | Pattern: Define a brute-force pattern in advance (script will prompt you if required otherwise) |

After running the script, you will be asked to choose a network to crack

Following the selection of a network, if you are using `WiFiCrackPy.py`, you may have to wait for a while for a handshake occurs naturally on the target network (i.e. for a device to (re)connect to the network), but this process is forced when using `WiFiCrackPy-DeAuth.py`, which should be much quicker.

Once a handshake is captured, `hashcat` will be initialised to extract the Wi-Fi password. This step may take quite a while depending on several factors including your machine's processing power and the attack method chosen. If successfull, you will be presented with the password for the target network.

WiFiCrackPy will retain the handshake in its directory if you would like to perform another type of attack against the capture.
