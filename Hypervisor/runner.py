# Run FROM the Project directory with:
# python3 Hypervisor/runner.py

from subprocess import Popen, call           # Popen doesn't wait for return of command, call does
import sys

if __name__ == '__main__':
    try:
        call(['gnome-terminal', '-e', "ryu-manager --observe-links Controllers/simple_switch_13.py"])
        for i in range(int(sys.argv[1])-1):
            call(['gnome-terminal', '-e', "ryu-manager --ofp-tcp-listen-port " + str(6633+int(i)+1) + " Controllers/simple_switch_13.py"])
        call(['gnome-terminal', '-e', "python3 Hypervisor/Hypervisor.py "+sys.argv[1]+" "+sys.argv[2]])
        call(['gnome-terminal', '-e', "sudo mn --custom Topologies/sdn_topo_"+sys.argv[1]+"_"+sys.argv[2]+".py --topo=mytopo --controller=remote,ip=127.0.0.1,port=65432,protocols=OpenFlow13 --mac"])

    except KeyboardInterrupt:
        print("Ctrl C - Stopping server")
        sys.exit(1)

    except Exception as e:
        print("There is an error with the runner {}".format(str(e)))    


