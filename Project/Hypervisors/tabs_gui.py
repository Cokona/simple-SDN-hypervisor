from tkinter import *
from tkinter.ttk import Notebook,Entry
import Hypervisor_multi

class Gui(object):
    def __init__(self, number_of_slices, number_of_switches, switches):
        #test value
        self.ports = "1,2,3"



        self.switches = switches #list of SWITCHes
        self.n_slices = number_of_slices
        self.n_switches = number_of_switches

        self.window = Tk()
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






    def update(self):
        print("Called update")
        self.window.update()

    def refresh(self):
        # print("update")
        #label1.configure(text='Balance :$' + str(max_amount))
        # self.window.update()
        #self.window.after(500, refresh)

        for slice in range(1,self.n_slices+1):
            self.insert_slice_rows(slice)
            pass
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
        n_switches = slef.number_of_switches


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

        for slice in range(1,self.n_slices+1):
            self.insert_slice_rows(slice)
            pass

        rows = 1 + 3 * self.n_slices

        refresh_bt = Button(self.tab2, text = "refresh", state = 'normal', padx = 1,pady = 3, command=self.refresh, fg = 'black', bg='white')
        refresh_bt.grid(row=rows+1, column=0, sticky="nsew", columnspan=1,rowspan=1, padx=1, pady=(1,3))
        self.tablayout.add(self.tab2,text="Switch Statistics")

        change_value_bt = Button(self.tab2, text="change values", state='normal', padx=1, pady=3, command=self.test_change_value, fg='black',
                            bg='white')
        change_value_bt.grid(row=rows + 1, column=1, sticky="nsew", columnspan=1, rowspan=1, padx=1, pady=(1, 3))

        self.tablayout.add(self.tab2, text="Switch Statistics")




    def insert_slice_rows(self, slice_no):  # slice_no = 1, 2, 3, ...
        '''
        for each slice, insert it rows of ports, max flow entries and #flow entries, for each switch
        '''
        label_slice = Label(self.tab2, text="Slice " + str(slice_no), bg="#0059b3", fg="white", padx=3, pady=3)
        label_slice.config(font=('Arial', 12))
        label_slice.grid(row=3 * (slice_no - 1) + 1, column=0, sticky="nsew", columnspan=1, rowspan=3, padx=1,
                         pady=(1, 3))

        label_ports = Label(self.tab2, text="ports", bg="white", fg="black", padx=3, pady=3)
        label_ports.config(font=('Arial', 12))
        label_ports.grid(row=3 * (slice_no - 1) + 1, column=1, sticky="nsew", columnspan=1, rowspan=1, padx=1,
                         pady=1)

        for col in range(2, 2 + self.n_switches):
            label_cell = Label(self.tab2, text= "", bg="white", fg="black", padx=3, pady=3)
            label_cell.config(font=('Arial', 12))
            if len(self.switches) < col -1:
                text = ""
            else:
                text = []
                ports =  self.switches[col-1].ports
                for port in ports:
                    if slice_no in port.list_of_slices:
                        text.append(port_no)
                    else:
                        pass
                
            port = self.switches
            label_cell.config(text = str(text))
            label_cell.grid(row=1 + 3 * (slice_no - 1), column=col, sticky="nsew", columnspan=1, rowspan=1,
                            padx=1, pady=1)

        label_maxflows = Label(self.tab2, text="max flow entries", bg="white", fg="black", padx=3, pady=3)
        label_maxflows.config(font=('Arial', 12))
        label_maxflows.grid(row=2 + 3 * (slice_no - 1), column=1, sticky="nsew", columnspan=1, rowspan=1,
                            padx=1, pady=1)

        for i in range(2, 2 + self.n_switches):
            label_cell = Label(self.tab2, text="", bg="white", fg="black", padx=3, pady=3)
            label_cell.config(font=('Arial', 12))
            label_cell.grid(row=2 + 3 * (slice_no - 1), column=i, sticky="nsew", columnspan=1, rowspan=1,
                            padx=1, pady=1)

        label_n_flows = Label(self.tab2, text="# flow entries", bg="white", fg="black", padx=3, pady=3)
        label_n_flows.config(font=('Arial', 12))
        label_n_flows.grid(row=3 + 3 * (slice_no - 1), column=1, sticky="nsew", columnspan=1, rowspan=1,
                           padx=1, pady=(1, 3))

        for i in range(2, 2 + self.n_switches):
            label_cell = Label(self.tab2, text="", bg="white", fg="black", padx=3, pady=3)
            label_cell.config(font=('Arial', 12))
            label_cell.grid(row=3 + 3 * (slice_no - 1), column=i, sticky="nsew", columnspan=1, rowspan=1,
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


gui = Gui(number_of_controllers,number_of_switches,[]) #server.proxy_port_switch_dict.values()
gui.update()

