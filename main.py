from tkinter import *
from tkinter import messagebox
import tkinter.filedialog as filedialog
from tkinter.simpledialog import askinteger
from tkinter.ttk import Combobox
from Ciphers import *
from utilities import *
import logging, os

params = []
log = logging.getLogger("main")

root = Tk()
h = 25
(x, y) = (500, 7*h)
root.geometry("{0}x{1}".format(x, y))
root.title("Crypto")
root.resizable(False, False)

ciphers = [file[:-3] for file in os.listdir('Ciphers') if file[0] != '_']
drop = Combobox(root, values=ciphers)
drop.current(0)

mode = StringVar(value="Encrypt")

encrypt_mode = Radiobutton(root, text="Encrypt", variable=mode, indicatoron=False, value="encrypt")
decrypt_mode = Radiobutton(root, text="Decrypt", variable=mode, indicatoron=False, value="decrypt")
encrypt_mode.invoke()

entry = Entry(root, text="")

def input():
    input_path = filedialog.askopenfilename()
    entry.delete(0, END)  # Remove current text in entry
    entry.insert(0, input_path)  # Insert the 'path'

browse = Button(root, text="Browse", command=input)

def collectParameters():
    full_reqs = getattr(globals()[drop.get()], "get_parameters")()
    reqs = full_reqs[mode.get().lower()]
    params = []

    def submit(p, params, req, frame):
        p = req[1](p)
        params.append(p)
        success = True
        for c in req[2]:
            if not eval(c[0]):
                params.pop(-1)
                messagebox.showerror("Invalid", c[1])
                success = False

        if success:
            frame.destroy()
        
    def collectEntry(req):
        p_frame = Toplevel(root)
        p_frame.resizable(False, False)


        p_label = Label(p_frame, text=req[0] + " = ")
        p_label.grid(row=0, column=0)

        p_entry = Entry(p_frame, text="")
        p_entry.grid(row=0, column=1)
        p_entry.bind("<Return>", lambda event: submit(p_entry.get(), params, req, p_frame))
        p_submit = Button(p_frame, text="Submit", command=lambda: submit(p_entry.get(), params, req, p_frame))
        p_submit.grid(row=0, column=2)

        for i in range(len(req[2])):
            p_conditionLabel = Label(p_frame, text=req[2][i][1])
            p_conditionLabel.grid(row=(i+1), columnspan=3)

        root.wait_window(p_frame)

    for req in reqs:
        if req[1] == int:
            collectEntry(req)
    return params

def process():
    assert entry.get()[-4:] == ".txt", "Invalid Path"

    file = open(entry.get(), "r", encoding='utf-8')
    text = file.read()
    file.close()
    
    func = getattr(globals()[drop.get()], mode.get().lower())
    
    ciphertext = func(text, collectParameters())

    file = filedialog.asksaveasfile(initialfile="Output.txt", defaultextension=".txt", filetypes=[("Text Documents", ".txt")])
    file.write(ciphertext)
    os.startfile(file.name)
    file.close()

process = Button(root, text="Process", command=process)

drop.place(relwidth=0.5, relx=0.05, y=h, height=h)

encrypt_mode.place(relwidth=0.2, relx=0.55, y=h, height=h)
decrypt_mode.place(relwidth=0.2, relx=0.75, y=h, height=h)

entry.place(relwidth=0.7, relx=0.05, y=3*h, height=h)
browse.place(relwidth=0.2, relx=0.75, y=3*h, height=h)

process.place(relwidth=0.9, relx=0.05, y=5*h, height=h)

mainloop()
