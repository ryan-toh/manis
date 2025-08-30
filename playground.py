import tkinter as tk

root = tk.Tk()
root.attributes('-fullscreen', True)

# root.configure(background="yellow")
# root.minsize(500, 500)
# root.maxsize(1000, 1000)
# root.update_idletasks()

# root.geometry("700x700+300+300")
image = tk.PhotoImage(file="logo.png")
tk.Label(root, image=image).pack()

root.mainloop()
