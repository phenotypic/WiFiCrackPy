# WiFiCrackPy

WiFiCrackPy demonstrates some of the security flaws associated with WPA(2) networks by performing simple and efficient cracking. The tool is for educational purposes and should not be misused.

The script captures the necessary Wi-Fi packets associated with WPA(2) handshakes using [`zizzania`](https://github.com/cyrus-and/zizzania), processes them with [`hcxpcapngtool`](https://github.com/ZerBea/hcxtools), and then utilises [`hashcat`](https://github.com/hashcat/hashcat) to extract the hashed passkey.

## Prerequisites

You must have `python3` installed.

> **Important:** Use the [official Python installer for macOS](https://www.python.org/downloads/mac-osx/) instead of installing Python via Homebrew. Homebrew installs Python with *ad-hoc code signing*, which causes macOS to deny location access required by the script. The official installer signs Python with proper entitlements, allowing full functionality.

You will also need to install any other outstanding requirements:

| Command | Installation |
| --- | --- |
| `libpcap`, `wget`, `hcxpcapngtool` | Install via [brew](https://brew.sh) by running `brew install libpcap wget hcxtools` |
| `~/zizzania/src/zizzania` | 1. Clone repository: `git clone https://github.com/cyrus-and/zizzania.git ~/zizzania`<br>2. Change directory: `cd ~/zizzania`<br>3. Build : `make -f config.Makefile && make` |
| `~/hashcat/hashcat` | 1. Clone repository: `git clone https://github.com/hashcat/hashcat.git ~/hashcat`<br>2. Change directory: `cd ~/hashcat`<br>3. Build: `make` |

## Usage

Clone the repository:
```
git clone https://github.com/phenotypic/WiFiCrackPy.git
```

Change to the project directory:
```
cd WiFiCrackPy
```

Install dependencies:
```
pip3 install -r requirements.txt
```

Run the script:
```
python3 WiFiCrackPy.py
```

The script is fairly easy to use, simply run it using the command above and enter your `sudo` password when prompted. The script also requires authorisaiton for location services in order to perform Wi-Fi scanning.

Here are some flags you can add:

| Flag | Description |
| --- | --- |
| `-w <wordlist>` | Wordlist: Define a wordlist path (script will prompt you otherwise) |
| `-i <interface>` | Interface: Set Wi-Fi interface (script can auto-detect default interface) |
| `-m <method>` | Method: Define the attack method (script will prompt you otherwise) |
| `-p <pattern>` | Pattern: Define a [brute-force pattern](https://hashcat.net/wiki/doku.php?id=mask_attack) in advance (script will prompt you if required) |
| `-o` | Optimised: Enable optimised kernels for `hashcat` |
| `-d` | Deauthentication: Activates zizzania's deauthentication feature to force a handshake (do not misuse) |

After running the script, you will be asked to choose a network to crack

Following the selection of a network, you may have to wait for a while for a handshake to occur naturally on the target network (i.e. for a device to (re)connect to the network) unless you are using the `-d` flag which will force a handshake to hasten the process.

Once a handshake is captured, `hashcat` can be used to crack the Wi-Fi password. This step may take quite a while depending on several factors including your Mac's processing power and the attack method chosen. If successfull, you will be presented with the password for the target network.

WiFiCrackPy retains the handshake in its directory if you would like to perform another type of attack against the capture.

## Compatibility

- `zizzania` has the ability to send deauthentication frames to force a handshake. This feature is disabled by default as frame injection is not possible from macOS 12 (Monterey) onwards.
