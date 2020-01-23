from tkinter import *
from tkinter.ttk import Notebook,Entry
import queue
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

class Gui(object):
    def __init__(self, master, queue, graphqueue, number_of_slices, number_of_switches, switches, flow_entry_max):
        #test value
        #self.ports = "1,2,3"

        self.queue = queue
        self.graphqueue = graphqueue
        self.graphtopo = None
        self.switches = switches #list of SWITCHes
        self.n_slices = number_of_slices
        self.n_switches = number_of_switches
        self.flow_entry_max = flow_entry_max
    

        self.window = master
        self.window.title("SDN hypervisor API")
        self.window.geometry("600x400")

        self.frame = Frame(self.window)
        self.frame.pack(fill="both")

        self.tablayout = Notebook(self.frame)

        self.tab1 = Frame(self.tablayout)
        self.tab2 = Frame(self.tablayout)
        self.tab3 = Frame(self.tablayout)

        self.create_tab_1()
        self.create_tab_2()
        self.create_tab_3()
        
    def processIncoming(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        while self.queue.qsize():
            try:
                self.switches = self.queue.get(0)
                # Check contents of message and do what it says
                # As a test, we simply print it
                #print(self.switches)
                self.update_refresh()
            except queue.Empty:
                pass

    def processTopology(self):
        """
        Hande all the message in the topology queue
        """
        while self.graphqueue.qsize():
            try:
                self.graphtopo = self.graphqueue.get(0)
                self.update_graph()
                print(self.graphtopo.nodes)
                print(self.graphtopo.edges)
            except queue.Empty:
                pass


    def update_graph(self):
        f = plt.figure(figsize=(5,5),dpi=100)
        # f.add_subplot(122)
        nx.draw(self.graphtopo, with_labels=True)
        canvas = FigureCanvasTkAgg(f,master=self.tab1)
        canvas.draw()
        canvas.get_tk_widget().pack(side=TOP,fill=BOTH,expand=1)
        
        self.window.update()

        pass


    def update(self):
        #print("Called update")
        self.window.update()
        #self.window.after(500, refresh)

    def update_refresh(self):
        # print("update")
        #label1.configure(text='Balance :$' + str(max_amount))
        # self.window.update()
        #self.window.after(500, refresh)
        #print("Update Refresh Called")
        for slicer in range(1,self.n_slices+1):
            self.insert_slice_rows(slicer)
        #print("Slices Inserted")
        self.window.update()
        #print("Window Updated")
        pass

    def test_change_value(self):
        self.ports = "a,b,c"
        # print(self.ports)
        pass
    

    def getValue(self):
        pass

    def set_number_of_slices(self):
        n_slices = self.number_of_slices

    def set_number_of_switches(self):
        n_switches = self.number_of_switches


    def create_tab_1(self):
        # tab1

        self.tab1.pack(fill="both")
        self.tablayout.add(self.tab1, text="Network Topology")



    def create_tab_2(self):
        # tab2
        self.tab2.pack(fill="both")


        #adding table into tab2
        label_sl_sw = Label(self.tab2, text="Slice \ Switch", bg="#0059b3", fg="white", padx=3,pady=3) #, anchor = "n"
        label_sl_sw.config(font=('Arial',12))
        label_sl_sw.grid(row=0, column=0, columnspan=2,rowspan=1,sticky="nsew",  padx=1, pady=(1,3))
        self.tab2.grid_columnconfigure(0, weight=1)
        self.tab2.grid_columnconfigure(1, weight=1)

        for col in range(1,self.n_switches+1):
            label_sw = Label(self.tab2, text="Switch " + str(col), bg="#0059b3", fg="white", padx=3,pady=3)
            label_sw.config(font=('Arial', 12))
            label_sw.grid(row=0, column=col+1, sticky="nsew", columnspan=1,rowspan=1, padx=1, pady=(1,3))
            self.tab2.grid_columnconfigure(col+1, weight=1)
        
        

        for slicer in range(1,self.n_slices+1):
            label_slice = Label(self.tab2, text="Slice " + str(slicer), bg="#0059b3", fg="white", padx=3, pady=3)
            label_slice.config(font=('Arial', 12))
            label_slice.grid(row=2 * (slicer - 1) + 1, column=0, sticky="nsew", columnspan=1, rowspan=2, padx=1,
                            pady=(1, 3))

            label_ports = Label(self.tab2, text="ports", bg="white", fg="black", padx=3, pady=3)
            label_ports.config(font=('Arial', 12))
            label_ports.grid(row=2 * (slicer - 1) + 1, column=1, sticky="nsew", columnspan=1, rowspan=1, padx=1,
                            pady=1)

            label_n_flows = Label(self.tab2, text="# flow entries", bg="white", fg="black", padx=3, pady=3)
            label_n_flows.config(font=('Arial', 12))
            label_n_flows.grid(row=2 * (slicer - 1) + 2, column=1, sticky="nsew", columnspan=1, rowspan=1,
                            padx=1, pady=(1, 3))

            # label_maxflows = Label(self.tab2, text="max flow entries", bg="white", fg="black", padx=3, pady=3)
            # label_maxflows.config(font=('Arial', 12))
            # label_maxflows.grid(row=2 + 3 * (slicer - 1), column=1, sticky="nsew", columnspan=1, rowspan=1,
            #                     padx=1, pady=1)
            self.insert_slice_rows(slicer)
            pass

        rows = 1 + 3 * self.n_slices

        update_bt = Button(self.tab2, text = "update", state = 'normal', padx = 1,pady = 3, command=self.update_refresh, fg = 'black', bg='white')
        update_bt.grid(row=rows+1, column=0, sticky="nsew", columnspan=1,rowspan=1, padx=1, pady=(1,3))
        self.tablayout.add(self.tab2,text="Slice informantion")

        





    def insert_slice_rows(self, slicer):  # slice_no = 1, 2, 3, ...
        '''
        for each slice, insert it rows of ports, max flow entries and #flow entries, for each switch
        '''
        

        for col in range(2, 2 + self.n_switches):
            label_cell_port = Label(self.tab2, text= "", bg="white", fg="black", padx=3, pady=3)
            label_cell_port.config(font=('Arial', 12))
            label_cell_no_flow = Label(self.tab2, text="", bg="white", fg="black", padx=3, pady=3)
            label_cell_no_flow.config(font=('Arial', 12))
            
            if len(self.switches) < col -1:
                text_port = ""
                text_flow = ""
                #getting flows
                
            else:
                text_port = ""
                text_flow = self.switches[col-2].no_of_flow_entries[slicer]
                ports =  list(self.switches[col-2].ports.values())
                for port in ports:
                    #getting ports for the slice
                    if slicer in port.list_of_slices:
                        if text_port != "":
                            text_port += str(",")
                        text_port += str(port.port_no)
                    else:
                        pass
            

                
            
            label_cell_port.config(text = str(text_port))
            label_cell_port.grid(row=2 * (slicer - 1) + 1, column=col, sticky="nsew", columnspan=1, rowspan=1,
                            padx=1, pady=1)

            label_cell_no_flow.config(text = str(text_flow))
            

            if text_flow == self.flow_entry_max:
                label_cell_no_flow.config(fg = "red")

            label_cell_no_flow.grid(row=2 * (slicer - 1) + 2, column=col, sticky="nsew", columnspan=1, rowspan=1,
                            padx=1, pady=(1, 3))
            

            


    def create_tab_3(self):
        #tab3
        #tab3=Frame(self.tablayout)
        self.tab3.pack(fill="both")

        #adding table into tab

        #input box Table
        for row in range(5):
            for column in range(6):
                if row==0:
                    label = Entry(self.tab3, text="Heading : " + str(column))
                    label.config(font=('Arial',14))
                    label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                    self.tab3.grid_columnconfigure(column, weight=1)
                else:
                    label=Entry(self.tab3,text="Row : "+str(row)+" , Column : "+str(column))
                    label.grid(row=row,column=column,sticky="nsew",padx=1,pady=1)
                    self.tab3.grid_columnconfigure(column,weight=1)

        self.tablayout.add(self.tab3,text="Switch Statistics")

        self.tablayout.pack(fill="both")


# gui = Gui(2,3,0)
# gui.mainloop()

