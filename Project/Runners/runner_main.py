from subprocess import Popen, call          # Popen doesn't wait for return of command, call does
import sys

if __name__ == '__main__':
    try:
        call(['gnome-terminal', '-e', "ryu-manager --observe-links Project/Controllers/simple_switch_13.py"])
        for i in range(int(sys.argv[1])-1):
            call(['gnome-terminal', '-e', "ryu-manager --ofp-tcp-listen-port " + str(6633+int(i)+1) + " --observe-links Project/Controllers/simple_switch_13.py"])
        call(['gnome-terminal', '-e', "python3 Project/Hypervisors/Hypervisor_main.py " + sys.argv[1]])
        call(['gnome-terminal', '-e', "sudo mn --custom Project/Topologies/sdn_topo_3.py --topo=mytopo --controller=remote,ip=127.0.0.1,port=65432,protocols=OpenFlow13"])
        # call(['gnome-terminal', '-e', "sudo mn --controller=remote,ip=127.0.0.1,port=65432,protocols=OpenFlow13"])      

    except KeyboardInterrupt:
        print("Ctrl C - Stopping server")
        sys.exit(1)

    except Exception as e:
        print("There is an error with the runner {}".format(str(e)))    


# Run FROM the sdn directory with:
# python3 Project/runner.py

