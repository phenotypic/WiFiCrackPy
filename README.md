# WiFiCrackPy

WiFiCrackPy demonstrates some of the security flaws associated with WPA(2) networks by performing simple and efficient cracking. The tool is for educational purposes and should not be misused.

The script captures the necessary Wi-Fi packets associated with WPA(2) handshakes using [`zizzania`](https://github.com/cyrus-and/zizzania), processes them with [`hcxpcapngtool`](https://github.com/ZerBea/hcxtools), and then utilises [`hashcat`](https://github.com/hashcat/hashcat) to extract the hashed passkey.

## Prerequisites

You must have `python3` installed. You will need to install any other outstanding requirements:

| Command | Installation |
| --- | --- |
| `hashcat`, `libpcap`, `wget`, `hcxpcapngtool` | Install via [brew](https://brew.sh) by running `brew install hashcat libpcap wget hcxtools` |
| `~/zizzania/src/zizzania` | Clone [this](https://github.com/cyrus-and/zizzania) repository then run `make -f config.Makefile && make -j "$(sysctl -n hw.logicalcpu)"` from inside the directory |

## Compatibility issues

- `zizzania` has the ability to send deauthentication frames to force a handshake. This feature is disabled by default as there are major compatibility issues with newer Macs (~2018 onwards)
- `hashcat` currently has major compatibility issues with Apple silicon Macs. Cracking may not be possible on these Macs so you can use the manual option to export the capture

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
| `-p <pattern>` | Pattern: Define a brute-force pattern in advance (script will prompt you if required) |
| `-o` | Optimised: Enable optimised kernels for `hashcat` |
| `-d` | Deauthentication: Activates zizzania's deauthentication feature to force a handshake (do not misuse) |

After running the script, you will be asked to choose a network to crack

Following the selection of a network, you may have to wait for a while for a handshake to occur naturally on the target network (i.e. for a device to (re)connect to the network) unless you are using the `-d` flag which will force a handshake to hasten the process.

Once a handshake is captured, `hashcat` can be used to crack the Wi-Fi password. This step may take quite a while depending on several factors including your Mac's processing power and the attack method chosen. If successfull, you will be presented with the password for the target network.

WiFiCrackPy retains the handshake in its directory if you would like to perform another type of attack against the capture.
