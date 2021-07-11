# WiFiCrackPy

WiFiCrackPy demonstrates some of the security flaws associated with WPA(2) networks by performing simple and efficient cracking. The tool is for educational purposes and should not be misused.

The script captures the necessary Wi-Fi packets associated with WPA(2) handshakes using [`zizzania`](https://github.com/cyrus-and/zizzania), and then utilises [`hashcat`](https://github.com/hashcat/hashcat) to extract the hashed passkey.

Zizzania has the ability to send deauthentication frames to the stations whose handshake is needed, though this feature is disabled by default as there are major compatibility issues with newer devices (~2018 onwards).

## Prerequisites

You must have `python3` installed. You will need to install any other outstanding requirements:

| Command | Installation |
| --- | --- |
| `hashcat`, `libpcap`, `wget` | Install via [brew](https://brew.sh) by running `brew install hashcat libpcap wget` |
| `~/hashcat-utils/src/cap2hccapx.bin` | Clone [this](https://github.com/hashcat/hashcat-utils) repository then run `make` from inside `src` |
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
| `-d` | Deauthentication: Activates zizzania's deauthentication feature to force a handshake (do not misuse) |

After running the script, you will be asked to choose a network to crack

Following the selection of a network, you may have to wait for a while for a handshake to occur naturally on the target network (i.e. for a device to (re)connect to the network) unless you are using the `-d` flag which will force a handshake and hasten the process.

Once a handshake is captured, `hashcat` will be initialised to extract the Wi-Fi password. This step may take quite a while depending on several factors including your machine's processing power and the attack method chosen. If successfull, you will be presented with the password for the target network.

WiFiCrackPy will retain the handshake in its directory if you would like to perform another type of attack against the capture.
