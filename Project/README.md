Lab project "Enabling Virtualisation in SDN Networks with a Hypervisor"
for the lecture Software Defined Networking class at the Technical University of TUM

Project creators:
    Kimon Cokona    - kimon.cokona@tum.de
    Yash Deshpande  - yash.deshpande@tum.de
    Duan Shen       - duan.shen@tum.de

A general description for the project can be found in the Project Report pdf.


Short description of the git organization:
    The folder Hypervisor has inside it all necessary parts to run the hypervisor.
        Hypervisor.py is the main part of the code and project. Inside it the following files are used:
            hyperobjects.py: Switch, Port and Slice classes have been defined to store and manipulate relevant information.
            hyper_parser.py: The parsing of Openflow messages is handled here, and specific fucntions are called according 
                             to the packet types. The python-openflow package (2019.2) from the Kytos SDN project has been used.
            hyperGUI.py:     The GUI object has been created to track some information related to the Hypervisor process
        
        runner.py is the code that is run to initiate all the necessary components of this projects. These are:
            The Hypervisor
            Multiple controllers
            Mininet, to create the necessary topology
    
    The folder Topologies includes many mininet topologies created for testing. These topologies have been named as
        sdn_topo_x_y.py, with x being the number of controllers, thus slices, and y being the number of switches.
        For simplicity these topologies have been created with the switches connected linearly, and so that every switch
        will have a single host for every different slice/controller/tenant.
    
    The folder Controllers includes a couple of different RYU controllers used to test the Hypervisor.
        The one that has been used mostly is simple_swith_13.py, which is a slightly modified version
        of the ryu example. The flag for Flow_Removed messages has been set, and an idle timeout has 
        been assigned to the flows.
    
    The folder Tester includes a TCP client and TCP server application, found online, to run through the host xterms
        to visualise the demonstration of the hypervisor.
    

**HOW TO RUN**

The runner has to be run with python3 from inside the Project directory. The user needs to add a number of controllers and a number of switches seperated with spaces. These numbers need to be according to the created topologies in the Topologies folder. The number of Controllers momentarily ranges between 1-4 and the number of switches between 1-7. One can easily add more topologies by changing:
        no_of_slices    = x
		no_of_switches  = y
in the beginning of the topology scripts and saving them as new files accordingly.

--> python3 Hypervisor/runner.py x y
    e.g. python3 Hypervisor/runner.py 2 3

Parameters that can be set are:
    - the idle_timeout: time for the controller created flows. This can be done inside the simple_switch_13.py script. It is also possible to use one's own controller by changing the runner.py file. Here also the allocated listening TCP ports can be changed, as long as they are also changed inside the Hypervisor.py. This is defined in the beginning of the script.
    - The FLOW_ENTRY_MAX: which is located in the first lines of the Hypervisor.py. This is the per controller allowed number of Flow rule entries per switch


The used setup was as follows, one might need to install the necessary python packets.
    The Hypervisor has been written using Python 3.7.4. 
    The Linux installation it has been tested on is an Ubuntu 16.04 with Open vSwitch (OVS) 2.11.0 and Mininet version 2.3.0d6. 
    All the implementations have been done using OpenFlow 1.3. 
    The default Python packages socket, select and tkinter have been used for the packet forwarding and the GUI respectively. 
    Additional Python packages are needed to fully use the created Hypervisor. These are: 

        RYU:                       A Python based SDN controller framework, used for the North Bound controller applications in the project.
        NetworkX:                  Easy to use package for topology graphs.
        python-openflow (2019.2) : Part of the Kytos SDN Project \cite{openflowlib}, used to parse OpenFlow1.3 packets.
        pypacker:                  Package to parse other packet types, such as Ethernet, ARP, IPv6, etc.
        