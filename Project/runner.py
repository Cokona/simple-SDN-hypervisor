from subprocess import Popen
import sys

if __name__ == '__main__':
    try:
        Popen(['gnome-terminal', '-e', "ryu-manager --observe-links Project/Controllers/simple_switch_13.py"])
        Popen(['gnome-terminal', '-e', "python3 Project/Hypervisors/TCP_proxy_multiple_controllers.py"])
        #Popen(['gnome-terminal', '-e', "python3 Project/Hypervisors/TCP_proxy.py"])
        Popen(['gnome-terminal', '-e', "sudo mn --custom Project/Topologies/sdn_topo_2.py --topo=mytopo --controller=remote,ip=127.0.0.1,port=65432,protocols=OpenFlow13"])
    except KeyboardInterrupt:
        print("Ctrl C - Stopping server")
        sys.exit(1)
    except:
        print("There is an error with the runner")


# Run FROM the sdn directory with:
# python3 Project/runner.py

