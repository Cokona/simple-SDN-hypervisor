from subprocess import Popen,call 
import sys

if __name__ == '__main__':
    try:
        call(['gnome-terminal', '-e', "ryu-manager --observe-links Project/Controllers/simple_switch_13.py"])
        #Popen(['gnome-terminal', '-e', "python3 Project/Hypervisors/TCP_proxy.py"])
        call(['gnome-terminal', '-e', "ryu-manager --ofp-tcp-listen-port 6643 --observe-links Project/Controllers/simple_switch_13.py"])
        call(['gnome-terminal', '-e', "python3 Project/Hypervisors/Hypervisor_main.py"])
        call(['gnome-terminal', '-e', "sudo mn --custom Project/Topologies/sdn_topo_2.py --topo=mytopo --controller=remote,ip=127.0.0.1,port=65432,protocols=OpenFlow13"])
    except KeyboardInterrupt:
        print("Ctrl C - Stopping server")
        sys.exit(1)
    except:
        print("There is an error with the runner")

