import tkinter as tk

root = tk.Tk()

root.configure(background="yellow")
root.minsize(500, 500)
root.maxsize(1000, 1000)
root.update_idletasks()

root.geometry("700x700+300+300")

# create two labels
tk.Label(root, text="I am SPONGEBOBBY").pack()
tk.Label(root, text="I am yellowboy").pack()

# root.eval('tk::PlaceWindow . center')

root.mainloop()
