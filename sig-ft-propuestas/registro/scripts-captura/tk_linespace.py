import customtkinter as ctk, tkinter.font as tf
r = ctk.CTk()
for t in (11, 12, 13, 14, 16, 24):
    for w in ("normal", "bold"):
        f = tf.Font(root=r, family="Roboto", size=-t, weight=w)
        print(t, w, f.metrics(), f.actual("family"))
