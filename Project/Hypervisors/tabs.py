from tkinter import *
from tkinter.ttk import Notebook,Entry

def insert_slice_rows(slice_no): #slice_no = 1, 2, 3, ...
    label_slice = Label(tab2, text="Slice " + str(slice_no), bg="#0059b3", fg="white", padx=3,pady=3)
    label_slice.config(font=('Arial', 12))
    label_slice.grid(row=3*(slice_no-1)+1, column=0, sticky="nsew", columnspan=1, rowspan=3, padx=1, pady=1)

    label_ports = Label(tab2, text="ports", bg="white", fg="black", padx=3,pady=3)
    label_ports.config(font=('Arial', 12))
    label_ports.grid(row=3*(slice_no-1)+1, column=1, sticky="nsew", columnspan=1, rowspan=1, padx=1, pady=1)

    for i in range(2, 2+n_switches):
        label_cell = Label(tab2, text="", bg="white", fg="black", padx=3,pady=3)
        label_cell.config(font=('Arial', 12))
        label_cell.grid(row=1+3*(slice_no-1), column=i, sticky="nsew", columnspan=1, rowspan=1, padx=1, pady=1)

    label_maxflows = Label(tab2, text="max flow entries", bg="white", fg="black", padx=3,pady=3)
    label_maxflows.config(font=('Arial', 12))
    label_maxflows.grid(row=2+3*(slice_no-1), column=1, sticky="nsew", columnspan=1, rowspan=1, padx=1, pady=1)

    for i in range(2, 2+n_switches):
        label_cell = Label(tab2, text="", bg="white", fg="black", padx=3,pady=3)
        label_cell.config(font=('Arial', 12))
        label_cell.grid(row=2+3*(slice_no-1), column=i, sticky="nsew", columnspan=1, rowspan=1, padx=1, pady=1)

    label_n_flows = Label(tab2, text="# flow entries", bg="white", fg="black", padx=3, pady=3)
    label_n_flows.config(font=('Arial', 12))
    label_n_flows.grid(row=3 + 3 * (slice_no - 1), column=1, sticky="nsew", columnspan=1, rowspan=1, padx=1, pady=1)

    for i in range(2, 2 + n_switches):
        label_cell = Label(tab2, text="", bg="white", fg="black", padx=3, pady=3)
        label_cell.config(font=('Arial', 12))
        label_cell.grid(row=3 + 3 * (slice_no - 1), column=i, sticky="nsew", columnspan=1, rowspan=1, padx=1, pady=1)
    pass

def getValue(value):
    print(value)

def set_number_of_slices(number_of_slices):
    n_slices = number_of_slices
def set_number_of_switches(number_of_switches):
    n_switches = number_of_switches

window=Tk()
window.title("SDN hypervisor API")
window.geometry("600x400")

frame=Frame(window)
frame.pack(fill="both")

tablayout=Notebook(frame)

#tab1
tab1=Frame(tablayout)
tab1.pack(fill="both")

tablayout.add(tab1,text="Network Topology")

#tab2
tab2=Frame(tablayout)
tab2.pack(fill="both")

n_slices = 3
n_switches = 4
#adding table into tab2
label_sw_no = Label(tab2, text="Slice \ Switch", bg="#0059b3", fg="white", padx=3,pady=3) #, anchor = "n"
label_sw_no.config(font=('Arial',12))
label_sw_no.grid(row=0, column=0, columnspan=2,rowspan=1,sticky="nsew",  padx=1, pady=1)
tab2.grid_columnconfigure(0, weight=1)
tab2.grid_columnconfigure(1, weight=1)

for col in range(1,n_switches+1):
    label_sw = Label(tab2, text="Switch " + str(col), bg="#0059b3", fg="white", padx=3,pady=3)
    label_sw.config(font=('Arial', 12))
    label_sw.grid(row=0, column=col+1, sticky="nsew", columnspan=1,rowspan=1, padx=1, pady=1)
    tab2.grid_columnconfigure(col+1, weight=1)

for slice in range(1,n_slices+1):
    insert_slice_rows(slice)
    pass

tablayout.add(tab2,text="Switch Statistics")




#tab3
tab3=Frame(tablayout)
tab3.pack(fill="both")

#adding table into tab

#input box Table
for row in range(5):
    for column in range(6):
        if row==0:
            label = Entry(tab3, text="Heading : " + str(column))
            label.config(font=('Arial',14))
            label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
            tab3.grid_columnconfigure(column, weight=1)
        else:
            label=Entry(tab3,text="Row : "+str(row)+" , Column : "+str(column))
            label.grid(row=row,column=column,sticky="nsew",padx=1,pady=1)
            tab3.grid_columnconfigure(column,weight=1)


tablayout.add(tab3,text="Slice Information")


tablayout.pack(fill="both")

window.mainloop()