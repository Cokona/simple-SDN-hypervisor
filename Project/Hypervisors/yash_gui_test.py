from tkinter import *
from tkinter.ttk import Notebook,Entry
import queue

class Gui(object):
    def __init__(self, master, queue, number_of_slices, number_of_switches, switches):
        #test value
        self.ports = "1,2,3"

        self.queue = queue

        self.switches = switches #list of SWITCHes
        self.n_slices = number_of_slices
        self.n_switches = number_of_switches

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

    def update(self):
        print("Called update")
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
        self.tablayout.add(self.tab2,text="Switch Statistics")

        change_value_bt = Button(self.tab2, text="change values", state='normal', padx=1, pady=3, command=self.test_change_value, fg='black',
                            bg='white')
        change_value_bt.grid(row=rows + 1, column=1, sticky="nsew", columnspan=1, rowspan=1, padx=1, pady=(1, 3))

        self.tablayout.add(self.tab2, text="Switch Statistics")




    def insert_slice_rows(self, slicer):  # slice_no = 1, 2, 3, ...
        '''
        for each slice, insert it rows of ports, max flow entries and #flow entries, for each switch
        '''
        

        for col in range(2, 2 + self.n_switches):
            label_cell = Label(self.tab2, text= "", bg="white", fg="black", padx=3, pady=3)
            label_cell.config(font=('Arial', 12))
            if len(self.switches) < col -1:
                text = ""
            else:
                text = ""
                ports =  list(self.switches[col-2].ports.values())
                for port in ports:
                    if slicer in port.list_of_slices:
                        text += str(port.port_no) + ", "
                    else:
                        pass
                
            #port = self.switches
            label_cell.config(text = str(text))
            label_cell.grid(row=2 * (slicer - 1) + 1, column=col, sticky="nsew", columnspan=1, rowspan=1,
                            padx=1, pady=1)

        

        # for i in range(2, 2 + self.n_switches):
        #     label_cell_max_flow = Label(self.tab2, text="", bg="white", fg="black", padx=3, pady=3)
        #     label_cell_max_flow.config(font=('Arial', 12))
        #     label_cell_max_flow.grid(row=2 + 3 * (slice_no - 1), column=i, sticky="nsew", columnspan=1, rowspan=1,
        #                     padx=1, pady=1)

        

        # for i in range(2, 2 + self.n_switches):
            label_cell_no_flow = Label(self.tab2, text="", bg="white", fg="black", padx=3, pady=3)
            label_cell_no_flow.config(font=('Arial', 12))
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

        self.tablayout.add(self.tab3,text="Slice Information")

        self.tablayout.pack(fill="both")


# gui = Gui(2,3,0)
# gui.mainloop()

