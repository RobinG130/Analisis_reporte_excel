from customtkinter  import CTk, CTkFrame, CTkEntry, CTkLabel,CTkButton,CTkCheckBox
import customtkinter


def login():
    print("login")


#interfaz grafica


root = CTk() 
root.geometry("300x500")
customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("green")

root.title("Iniciar Sesion")

frame = CTkFrame(root)
frame.pack(padx = 10, pady = 10, fill = "both", expand = True)

label = customtkinter.CTkLabel(master = frame, text= "Application Login", font  = ("Roboto", 28))
label.pack(pady = 60, padx = 20)

entry1 =customtkinter.CTkEntry (master=frame, placeholder_text="Username")
entry1.pack(pady=12, padx=10)

entry2 =customtkinter.CTkEntry (master=frame, placeholder_text="Password", show = "*")
entry2.pack(pady=12, padx=10)

Login_Button = customtkinter.CTkButton(master= frame, text= 'Login', command= login)
Login_Button.pack(pady=12, padx=10)

CheckBox = customtkinter.CTkCheckBox(master=frame, text="RemenberMe", checkbox_height =17,checkbox_width = 17)
CheckBox.pack()

root.mainloop()

