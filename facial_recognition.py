from cv2 import VideoCapture,imshow,imread,flip,imwrite,waitKey,destroyAllWindows,resize
from face_recognition import face_encodings,face_locations,compare_faces
from os import listdir,remove
from requests import get
from json import loads
from customtkinter import CTk,CTkLabel,CTkFrame,CTkButton,CTkRadioButton
from tkinter import ttk,END,messagebox,IntVar
from serial import Serial

def get_faces():
    global known_face_encodings
    global ids
    known_face_encodings = []
    ids = []
    for face in listdir(path):
            image = imread(path+face)
            try:
                face_loc = face_locations(image)[0]
                face_image_encodings = face_encodings(image,known_face_locations=[face_loc])[0]
                known_face_encodings.append(face_image_encodings)
                ids.append(face)
            except:
                print("Face not located in:",face)

def get_users(table):
    try:
        response = get("http://localhost:3000/api/v1/users/workers")
        if response.status_code == 200:
            usersText = response.text
            users_json = loads(usersText)
            table.delete(*table.get_children())
            for user in users_json:
                table.insert("",END,text=user["_id"],values=(user["name"],user["lastName"],user["email"],user["status"]["status"]))
    except:
        messagebox.showwarning(message="Web service is down. Try refresh the table", title="Error")

def get_one(id):
    response = get("http://localhost:3000/api/v1/users/workers/{}".format(id))
    if response.status_code == 200:
        userText = response.text
        user_json = loads(userText)
        return user_json
    
def show_user(id):
    try:
        user = get_one(id)
        for data in user:
            if data["status"]["status"] == "Up":
                user_name = data["name"] + " " + data["lastName"]
                try:
                    pic.write(b'o')
                    pic.write(b'c')
                except:
                    messagebox.showwarning(message="Pic Connection Failed", title="Error")
                    serial_connection(conn_info)
                messagebox.showinfo(message="Hi: {}".format(user_name), title="Successful")
            else:
                messagebox.showinfo(message="Your status is Down", title="¡Access Denied!")
    except:
        messagebox.showwarning(message="Web service is down. Try refresh the table", title="Error")

def register_face(table):
    try:
        item = table.selection()[0]
    except IndexError:
        messagebox.showwarning(
            message="You must select an user!",
            title="No selection"
        )
    else:
        text = table.item(item, option="text")
        cap = VideoCapture(radio_var.get())#CAMBIAR A 2 PARA WEB CAM EXTERNA 0 PARA INTERNA
        while True:
            ret, frame = cap.read()
            if ret == False:
                messagebox.showwarning(message="The selected camera are disabled. Choose another one.", title="Error")
                break
            frame = flip(frame,1)
            imshow("Web Cam",frame)

            key = waitKey(1) & 0xFF
            if(key == ord(' ')):
                try:
                    fileName = text+".jpg"
                    imwrite(path+fileName,frame)
                    image = imread(path+fileName)
                    face_loc = face_locations(image)[0]
                    face_image_encodings = face_encodings(image,known_face_locations=[face_loc])[0]
                    known_face_encodings.append(face_image_encodings)
                    ids.append(fileName)
                    text = "Face has been saved in the server!"
                    messagebox.showinfo(message=text, title="Successful")
                except:
                    remove(path+fileName)
                    print("Face has not been saved because the system not detected a face in current image!")
                    
                break
            elif(key == ord('e')):
                break

        cap.release()
        destroyAllWindows()

def read_face():
    cap = VideoCapture(radio_var.get())#CAMBIAR A 2 PARA WEB CAM EXTERNA 0 PARA INTERNA
    id = ""
    flag = ""
    while True:
        ret, frame = cap.read()
        frame = resize(frame, (0, 0), fx=0.40, fy=0.40)
        frame = frame[:, :, ::-1]
        if ret == False:
            messagebox.showwarning(message="The selected camera are disabled. Choose another one.", title="Error")
            break
        frame = flip(frame,1)
        imshow("Web Cam",frame)

        face_locationsM = face_locations(frame)
        if face_locationsM != []:
            i = 0
            for face_location in face_locationsM:
                face_frame_encodings = face_encodings(frame,known_face_locations=[face_location])[0]
                for face in known_face_encodings:
                    result = compare_faces([face_frame_encodings],face,tolerance=0.50)
                    if result[0] == True:
                        id = ids.__getitem__(i).split(".")[0]
                        show_user(id)
                        break
                    i+=1

        key = waitKey(1) & 0xFF
        if(key == ord('e')):
            flag = "end"
            break
        if id != "":
            flag = "continue"
            break

    cap.release()
    destroyAllWindows()
    return flag

def serial_connection(label):
    global pic
    try:
        if pic.is_open:
            pic.close()
    except:
        pass
    try:
        pic = Serial("/dev/ttyUSB0",9600)
        if pic.is_open:
            label.configure(text="Pic Status: Connected",text_color=c_green)
    except:
        label.configure(text="Pic Status: Not Connected",text_color=c_red)
        messagebox.showwarning(message="Serial Connection Failed. Try Again.", title="Error")

def repeat_read_face():
    flag = "continue"
    while flag == "continue":
        flag = read_face()
        root.update()

path = "/home/gary/iaProject/faces/"

c_black = "#010101"
c_green = "#2cb67d"
c_purple = "#7f5af0"
c_white = "#ffffff"
c_red = "#FF0000"

root = CTk()
root.geometry("100+50")
root.title("SECURITY SYSTEM")

frame1 = CTkFrame(root)
frame1.grid(column = 0,row = 0,sticky = 'nsew',padx = 20,pady = 20)

radio_var = IntVar()
radiobutton_1 = CTkRadioButton(frame1, text="Internal Camera", variable= radio_var, value=0, hover_color=c_green)
radiobutton_2 = CTkRadioButton(frame1, text="External Camera", variable= radio_var, value=2, hover_color=c_green)
radiobutton_1.grid(column = 0,row = 0,pady = 10)
radiobutton_2.grid(column = 2,row = 0,pady = 10)

btn_register_face = CTkButton(frame1, text="Add Face",hover_color=c_green,command=lambda:register_face(table))
btn_register_face.grid(column = 0,row = 1,pady = 10)

btn_read_face = CTkButton(frame1, text="Scan Face",hover_color=c_green,command=repeat_read_face)
btn_read_face.grid(column = 1,row = 1,pady = 10)

btn_read_face = CTkButton(frame1, text="Refresh Table",hover_color=c_green,command=lambda:get_users(table))
btn_read_face.grid(column = 2,row = 1,pady = 10)

table_tittle = CTkLabel(frame1,font=("",20),text="- - - - - - - - - - - - - - USERS - - - - - - - - - - - - - -",text_color=c_black)
table_tittle.grid(columnspan = 3,column = 0,row = 2)

'''------------------------------------ TABLA ------------------------------------'''

table = ttk.Treeview(frame1,columns=("name","lastName","email","status"))

table.grid(columnspan = 3,column = 0,row = 3,padx=20)

table.heading("#0",text="Id")
table.heading("name",text="Name")
table.heading("lastName",text="Last Name")
table.heading("email",text="Email")
table.heading("status",text="Status")

root.columnconfigure(0,weight = 1)
root.rowconfigure(0,weight = 1)

btn_serial = CTkButton(frame1, text="Connect",hover_color=c_green,command=lambda:serial_connection(conn_info))
btn_serial.grid(column = 0,row = 4,pady = 10)

conn_info = CTkLabel(frame1,font=("",20),text="",text_color=c_black)
conn_info.grid(column = 1,row = 4,pady = 10)

btn_exit = CTkButton(frame1, text="Exit",hover_color=c_green,command=root.destroy)
btn_exit.grid(column = 2,row = 4,pady = 10)

get_users(table)
get_faces()
serial_connection(conn_info)

root.mainloop()
try:
    pic.close()
except: 
    pass