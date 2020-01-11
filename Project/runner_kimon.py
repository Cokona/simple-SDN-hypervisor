from subprocess import Popen
import sys

if __name__ == '__main__':
        try:
            Popen(['gnome-terminal', '-e', "ryu-manager --observe-links /home/kimon/Documents/software_defined_networks_lab/sdn/Project/Controllers/simple_switch_13.py"])
            Popen(['gnome-terminal', '-e', "python3 /home/kimon/Documents/software_defined_networks_lab/sdn/Project/Hypervisors/TCP_proxy.py"])
            Popen(['gnome-terminal', '-e', "sudo mn --custom Project/Topologies/sdn_topo_2.py --topo=mytopo --controller=remote,ip=127.0.0.1,port=65432,protocols=OpenFlow13"])
        except KeyboardInterrupt:
            print("Ctrl C - Stopping server")
            sys.exit(1)
        except:
            print("There is an error with the runner")

