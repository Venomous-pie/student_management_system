from tkinter import filedialog
from CTkMessagebox import CTkMessagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
from pyzbar import pyzbar
import os
import pyqrcode
import mysql.connector

ctk.set_default_color_theme("dark-blue")
ctk.set_appearance_mode("system")


class Auth:
    def __init__(self, master):
        self.master = master
        master.title("Student Attendance Manager")

        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x_center = (screen_width - 300) / 2
        y_center = (screen_height - 300) / 2

        # Set window position
        master.geometry(f"300x300+{int(x_center)}+{int(y_center)}")

        # frame for credentials
        self.credential_frame = ctk.CTkFrame(master, border_color="white", width=300)
        self.credential_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        # image for credentials
        self.user_png = Image.open("user1.png")
        self.user_img = ctk.CTkImage(self.user_png, size=(70, 70))

        # label for image
        self.user_image_label = ctk.CTkLabel(self.credential_frame, image=self.user_img, text="")
        self.user_image_label.grid(padx=5, pady=30, row=0, column=1)

        # label for page
        self.login_label = ctk.CTkLabel(self.credential_frame, text="Login", font=("", 20))
        self.login_label.grid(padx=5, pady=2, row=1, column=1)

        # username
        self.username_entry = ctk.CTkEntry(self.credential_frame, width=140, height=20, placeholder_text="username")
        self.username_entry.grid(padx=50, pady=10, row=2, column=1)
        self.username_entry.bind("<Return>", self.login)

        # passkey
        self.passkey_entry = ctk.CTkEntry(self.credential_frame, width=140, height=20, placeholder_text="passkey",
                                          show="*")
        self.passkey_entry.grid(padx=40, pady=10, row=3, column=1)
        self.passkey_entry.bind("<Return>", self.login)

        # buttons login/register
        self.login_button = ctk.CTkButton(self.credential_frame, text="login", height=25, width=140, command=self.login)
        self.login_button.grid(padx=0, pady=20, row=4, column=1)

        # register
        self.register_label = ctk.CTkLabel(self.credential_frame, text="Don't have an account?")
        self.register_label.grid(padx=5, pady=1, row=5, column=1)

        self.register_button = ctk.CTkButton(self.credential_frame, text="register", height=25, width=135,
                                             command=self.op_register)
        self.register_button.grid(padx=0, pady=1, row=6, column=1)

        # filler
        self.blank = ctk.CTkLabel(self.credential_frame, text="")
        self.blank.grid(padx=5, pady=10)

    # login logic
    def login(self, event=None):
        username = self.username_entry.get()
        passkey = self.passkey_entry.get()

        if username and passkey:
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    username="root",
                    password="",
                    database="SAMS"
                )

                cursor = conn.cursor()

                cursor.execute("SELECT * FROM users WHERE username=%s AND passkey=%s",
                               (username, passkey))
                fetch_result = cursor.fetchone()

                if fetch_result:
                    self.master.destroy()
                    self.wn_attendance(username, passkey, fetch_result[0])
                else:
                    CTkMessagebox(title="Credential Error",
                                  message="Invalid credentials.",
                                  icon="cancel",
                                  width=50,
                                  height=35)
            except mysql.connector.Error as e:
                CTkMessagebox(title="Database Error",
                              message=f"{e}",
                              icon="cancel",
                              width=50,
                              height=30,
                              button_height=5,
                              justify="center")

    def wn_attendance(self, username, passkey, user_database):
        root = ctk.CTk()
        app = AttendanceApp(root, username, passkey, user_database)
        root.after(0, root.state, "zoomed")
        root.mainloop()

    def op_register(self):
        wn_register = ctk.CTkToplevel(self.master)
        wn_register.after(0, wn_register.state, "zoomed")
        wn_register.attributes("-topmost", True)
        RegisterApp(wn_register)


class RegisterApp:
    def __init__(self, master):
        self.master = master
        master.title("Register Window")

        # frame for credentials
        self.credential_frame = ctk.CTkFrame(master, border_color="white", width=300)
        self.credential_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        # image for credentials
        self.user_png = Image.open("user1.png")
        self.user_png_resized = self.user_png.resize((90, 90))
        self.user_image = ImageTk.PhotoImage(self.user_png_resized)

        self.user_img = ctk.CTkImage(self.user_png, size=(70, 70))

        # label for image
        self.user_image_label = ctk.CTkLabel(self.credential_frame, image=self.user_img, text="")
        self.user_image_label.grid(padx=5, pady=30, row=0, column=1)

        # label for page
        self.login_label = ctk.CTkLabel(self.credential_frame, text="Register", text_color="white", font=("", 20))
        self.login_label.grid(padx=5, pady=2, row=1, column=1)

        # username
        self.username_entry = ctk.CTkEntry(self.credential_frame, width=140, height=20, placeholder_text="username")
        self.username_entry.grid(padx=40, pady=10, row=2, column=1)

        # passkey
        self.passkey_entry = ctk.CTkEntry(self.credential_frame, width=140, height=20, placeholder_text="passkey")
        self.passkey_entry.grid(padx=40, pady=10, row=3, column=1)

        # confirm passkey
        self.passkey_entry_confirm = ctk.CTkEntry(self.credential_frame, width=140, height=20,
                                                  placeholder_text="confirm passkey")
        self.passkey_entry_confirm.grid(padx=40, pady=10, row=4, column=1)

        # buttons login/register
        self.register_button = ctk.CTkButton(self.credential_frame, text="register", height=25, width=135,
                                             command=self.register)
        self.register_button.grid(padx=0, pady=20, row=5, column=1)

        # filler
        self.blank = ctk.CTkLabel(self.credential_frame, text="")
        self.blank.grid(padx=5, pady=10)

    def register(self):
        username = self.username_entry.get()
        passkey = self.passkey_entry.get()
        c_passkey = self.passkey_entry_confirm.get()

        if c_passkey != passkey:
            CTkMessagebox(title="Credential Error",
                          message="Passkey does not match.",
                          icon="cancel",
                          width=50,
                          height=30,
                          button_height=5,
                          justify="center")
        else:
            if not (username and passkey and c_passkey):
                CTkMessagebox(title="Credential Error",
                              message="All fields are required.",
                              icon="warning",
                              width=50,
                              height=30,
                              button_height=5,
                              justify="center")
            else:
                if username and passkey:
                    try:
                        conn = mysql.connector.connect(
                            host="localhost",
                            username="root",
                            password="",
                            database="SAMS"
                        )

                        cursor = conn.cursor()

                        user_db = f"username: {username}"

                        cursor.execute("INSERT INTO users (username, passkey, user_db) VALUES (%s, %s, %s)",
                                       (username, passkey, user_db))
                        conn.commit()
                        cursor.close()

                        self.master.destroy()

                        CTkMessagebox(title="User Registered",
                                      message=f"User {username}, successfully registered.",
                                      icon="check",
                                      width=50,
                                      height=30,
                                      button_height=5,
                                      justify="center")

                    except mysql.connector.Error as e:
                        CTkMessagebox(title="Database Error",
                                      message=f"{e}",
                                      icon="cancel",
                                      width=50,
                                      height=30,
                                      button_height=5,
                                      justify="center")
                else:
                    CTkMessagebox(title="Data Error",
                                  message="Error parsing the data.",
                                  icon="cancel",
                                  width=50,
                                  height=30,
                                  button_height=5,
                                  justify="center")


class AttendanceApp:
    def __init__(self, master, username, passkey, user_database):
        self.master = master
        master.title("Attendance Page")

        self.qr_code_app = QRcode(master, username, passkey, user_database)

        # determine window width and height
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()

        # side panel frame
        self.sidepanel_frame = ctk.CTkFrame(self.master, border_color="white", width=screen_width - 1010,
                                            height=screen_height - 70, corner_radius=0)
        self.sidepanel_frame.place(relx=0, rely=0.5, anchor=ctk.W)

        # image for credentials
        self.user_png = Image.open("user1.png")
        self.user_png_resized = self.user_png.resize((90, 90))
        self.user_image = ImageTk.PhotoImage(self.user_png_resized)

        self.user_img = ctk.CTkImage(self.user_png, size=(70, 70))

        # label for image
        self.user_image_label = ctk.CTkLabel(self.sidepanel_frame, image=self.user_img, text="")
        self.user_image_label.place(relx=0.5, rely=0.1, anchor=ctk.CENTER)

        # label for user
        self.login_label = ctk.CTkLabel(self.sidepanel_frame, text=f"{username.capitalize()}", font=("", 20))
        self.login_label.place(relx=0.5, rely=0.2, anchor=ctk.CENTER)

        # filler line
        self.filler_line = ctk.CTkLabel(self.sidepanel_frame, text="________________________________________")
        self.filler_line.place(relx=0.5, rely=0.24, anchor=ctk.CENTER)

        # label for page
        self.login_label = ctk.CTkLabel(self.sidepanel_frame, text="Menu", font=("", 20))
        self.login_label.place(relx=0.5, rely=0.29, anchor=ctk.CENTER)

        # class button
        self.class_button = ctk.CTkButton(self.sidepanel_frame, text="Class", width=250, height=30, corner_radius=1,
                                          command=self.check_classnames_exist)
        self.class_button.place(relx=0.5, rely=0.36, anchor=ctk.CENTER)

        # history button
        self.history_button = ctk.CTkButton(self.sidepanel_frame, text="History", width=250, height=30, corner_radius=1,
                                            command=self.history_page)
        self.history_button.place(relx=0.5, rely=0.42, anchor=ctk.CENTER)

        # qr code button
        self.setting_button = ctk.CTkButton(self.sidepanel_frame, text="Generate QR", width=250, height=30,
                                            corner_radius=1, command=self.qr_code_generator_open)
        self.setting_button.place(relx=0.5, rely=0.48, anchor=ctk.CENTER)

        # settings button
        self.setting_button = ctk.CTkButton(self.sidepanel_frame, text="Settings", width=250, height=30,
                                            corner_radius=1, command=self.setting_page)
        self.setting_button.place(relx=0.5, rely=0.54, anchor=ctk.CENTER)

        # qr camera button
        self.qr_camera_button = ctk.CTkButton(self.sidepanel_frame, text="QR reader", width=250, height=30,
                                              corner_radius=1, command=self.qr_code_app.read_qr_codes_camera)
        self.qr_camera_button.place(relx=0.5, rely=0.60, anchor=ctk.CENTER)

        # content frame
        self.content_frame = ctk.CTkFrame(self.master, width=screen_width - 270, height=screen_height - 70,
                                          corner_radius=0)
        self.content_frame.place(relx=1, rely=0.5, anchor=ctk.E)

        # dictionary to store page frames
        self.page_frames = {}
        self.current_page = None

        # page frame reference
        self.page_frame = None

        # classroom frame reference
        self.classroom_frame = None

        # classroom_n reference
        self.classroom_n = None

        # classnames list reference
        self.classnames = []

        # register_class_button reference
        self.register_class_button = None

        self.fetch_classnames()
        self.check_classnames_exist()
        
        self.generate_classroom_frames()

    def content_container(self, page_label):
        self.master.update()

        w_content_frame = self.content_frame.winfo_width()
        h_content_frame = self.content_frame.winfo_height()

        self.master.update()

        # hide current page
        if self.current_page:
            self.page_frames[self.current_page].place_forget()

        self.page_frame = ctk.CTkFrame(self.content_frame, width=w_content_frame - 515, height=h_content_frame - 326)
        self.page_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        page_label_widget = ctk.CTkLabel(self.page_frame, text=f"{page_label}", font=("", 20))
        page_label_widget.place(relx=0.07, rely=0.02, anchor=ctk.N)

        # store page frame
        self.page_frames[page_label] = self.page_frame
        self.current_page = page_label

        if self.current_page == "Classroom":
            # register new class button
            self.register_class_button = ctk.CTkButton(self.page_frame, text="New Class", width=20,
                                                       height=35, corner_radius=2, command=self.register_class_open)
            self.register_class_button.place(relx=0.98, rely=0.035, anchor=ctk.E)
        else:
            pass

    def fetch_classnames(self):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                username="root",
                password="",
                database="SAMS"
            )

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM classes")

            fetch_result = cursor.fetchall()
            self.classnames.clear()

            for i in fetch_result:
                self.classnames.append(i[1])

            conn.commit()
            cursor.close()

        except mysql.connector.Error as e:
            CTkMessagebox(title="Database Error",
                          message=f"{e}",
                          icon="cancel",
                          width=50,
                          height=30,
                          button_height=5,
                          justify="center")

    @staticmethod
    def delete_classroom_db(classname):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                username="root",
                password="",
                database="SAMS"
            )

            cursor = conn.cursor()
            cursor.execute("DELETE FROM classes WHERE class_name = %s", (classname,))

            conn.commit()
            cursor.close()
            conn.close()

        except mysql.connector.Error as e:
            CTkMessagebox(title="Database Error",
                          message=f"{e}",
                          icon="cancel",
                          width=50,
                          height=30,
                          button_height=5,
                          justify="center")

    def delete_classroom(self, classname):
        confirmation = CTkMessagebox(title="Are you sure?", message=f"Do you want to delete \"{classname}\"?",
                                     icon="warning", option_1="No", option_2="Yes")
        response = confirmation.get()

        if response == "Yes":
            if classname not in self.classnames:
                print(f"Classroom '{classname}' does not exist.")
            else:
                self.delete_classroom_db(classname)
                self.classroom_n.destroy()
                self.fetch_classnames()

                if len(self.classnames) > 0:
                    self.display_classroom()
                else:
                    self.display_empty_classroom()

    def check_classnames_exist(self):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                username="root",
                password="",
                database="SAMS"
            )

            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) > 0 AS table_has_content FROM classes")
            class_database = cursor.fetchall()

            for i in class_database:
                class_database_index = i[0]
                if class_database_index > 0:
                    self.display_classroom()
                else:
                    self.display_empty_classroom()

        except mysql.connector.Error as e:
            CTkMessagebox(title="Database Error",
                          message=f"{e}",
                          icon="cancel",
                          width=50,
                          height=30,
                          button_height=5,
                          justify="center")

    def display_classroom(self):
        self.content_container("Classroom")
        self.fetch_classnames()

        if not self.check_classnames_exist:
            self.display_empty_classroom()
        else:
            # UI for the classrooms
            self.classroom_frame = ctk.CTkScrollableFrame(self.page_frame, width=980, height=600, corner_radius=1)
            self.classroom_frame.place(relx=0.5, rely=1, anchor=ctk.S)

            self.generate_classroom_frames()

        # self.master.after(1000, self.display_classroom())

    def display_empty_classroom(self):
        self.content_container("Class")

        # image for empty classroom
        empty_class_png = Image.open("folder.png")
        empty_class_img = ctk.CTkImage(empty_class_png, size=(90, 90))

        # empty class image label
        empty_class_image_label = ctk.CTkLabel(self.page_frame, image=empty_class_img, text="")
        empty_class_image_label.place(relx=0.5, rely=0.4, anchor=ctk.CENTER)

        # if class db is empty
        empty_class_db_label = ctk.CTkLabel(self.page_frame, text="Empty classroom, register new class.")
        empty_class_db_label.place(relx=0.5, rely=0.55, anchor=ctk.CENTER)

        register_class_button = ctk.CTkButton(self.page_frame, text="Register New Class", width=250,
                                              height=30, corner_radius=1, command=self.register_class_open)
        register_class_button.place(relx=0.5, rely=0.6, anchor=ctk.CENTER)

    def classroom_gen(self, classname, row_n, column_n):
        self.classroom_n = ctk.CTkFrame(self.classroom_frame, width=300, height=300, corner_radius=2, border_width=1,
                                        border_color="gray")
        self.classroom_n.grid(padx=15, pady=10, row=row_n, column=column_n)

        classroom_name = ctk.CTkLabel(self.classroom_n, text=f"{classname}")
        classroom_name.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        class_del_button = ctk.CTkButton(self.classroom_n, width=5, text="Delete", fg_color="#bb2124",
                                         command=lambda cn=classname: self.delete_classroom(cn))
        class_del_button.place(relx=0.88, rely=0.98, anchor=ctk.S)

        class_open = ctk.CTkButton(self.classroom_n, width=5, text="Open", fg_color="#5bc0de",
                                   command=lambda cn=classname: self.open_classroom(cn))
        class_open.place(relx=0.70, rely=0.98, anchor=ctk.S)

    def generate_classroom_frames(self):
        classnames_len = len(self.classnames)
        max_cols = 3
        row_val = 0
        col_val = 0

        for i in range(classnames_len):
            class_name = self.classnames[i]
            self.classroom_gen(class_name, row_val, col_val)
            col_val += 1
            if col_val >= max_cols:
                col_val = 0
                row_val += 1

    def open_classroom(self, classname):
        self.content_container(f"{classname}")

        self.fetch_student_data(classname)

        self.classroom_frame = ctk.CTkScrollableFrame(self.page_frame, width=980, height=600, corner_radius=1)
        self.classroom_frame.place(relx=0.5, rely=1, anchor=ctk.S)

        # Headers
        headers = ["No.", "Name", "School Days", "Excused"]
        for i, header in enumerate(headers):
            header_label = ctk.CTkLabel(self.classroom_frame, text=header)
            header_label.grid(row=0, column=i, pady=5, padx=10, sticky=ctk.W)

        student_data = self.fetch_student_data(classname)

        id_counter = 1

        students = []
        for i in student_data:
            name = i[1] + " " + i[2] + " " + i[3]
            students.append({"ID": str(id_counter).zfill(3), "Name": name, "School Days": i[4], "Excused": i[5]})
            id_counter += 1

        for row_index, student in enumerate(students, start=1):
            for col_index, (key, value) in enumerate(student.items()):
                student_label = ctk.CTkLabel(self.classroom_frame, text=value)
                student_label.grid(row=row_index, column=col_index, pady=5, padx=10, sticky=ctk.W)

    def fetch_student_data(self, classname):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="SAMS"
            )

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE section_or_strand=%s", (classname,))
            fetch_result = cursor.fetchall()

            student_data = []

            for i in fetch_result:
                student_data.append(i)

            conn.commit()
            cursor.close()

            return student_data

        except mysql.connector.Error as e:
            CTkMessagebox(title="Database Error",
                          message=f"{e}",
                          icon="cancel",
                          width=50,
                          height=30,
                          button_height=5,
                          justify="center")

    def history_page(self):
        self.content_container("History")

    def setting_page(self):
        self.content_container("Settings")

    def register_class_open(self):
        wn_register_class = ctk.CTkToplevel(self.master)
        wn_register_class.geometry("500x500")
        wn_register_class.attributes("-topmost", True)
        RegisterClass(wn_register_class, "%s", "%s", "%s")

    def qr_code_generator_open(self):
        wn_qr_code_generator = ctk.CTkToplevel(self.master)
        wn_qr_code_generator.geometry("500x500")
        wn_qr_code_generator.attributes("-topmost", True)
        QRcode(wn_qr_code_generator, "%s", "%s", "%s")


# from here on out, may God guide me through this project

# QR code Generator and Reader
class QRcode:
    def __init__(self, master, username, passkey, user_database):
        self.master = master
        master.title("QR generator")

        self.qr_code_gen_frame = ctk.CTkFrame(self.master, width=200, height=500)
        self.qr_code_gen_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        self.entry_first_name = ctk.CTkEntry(self.qr_code_gen_frame, width=150, height=5, placeholder_text="first name")
        self.entry_first_name.grid(row=0, column=1, padx=10, pady=10)

        self.entry_middle_name = ctk.CTkEntry(self.qr_code_gen_frame, width=150, height=5,
                                              placeholder_text="middle name")
        self.entry_middle_name.grid(row=1, column=1, padx=10, pady=10)

        self.entry_last_name = ctk.CTkEntry(self.qr_code_gen_frame, width=150, height=5, placeholder_text="last name")
        self.entry_last_name.grid(row=2, column=1, padx=10, pady=10)

        self.entry_age = ctk.CTkEntry(self.qr_code_gen_frame, width=150, height=5, placeholder_text="age")
        self.entry_age.grid(row=3, column=1, padx=10, pady=10)

        self.entry_social_media = ctk.CTkEntry(self.qr_code_gen_frame, width=150, height=5, placeholder_text="fb link")
        self.entry_social_media.grid(row=4, column=1, padx=10, pady=10)

        self.section_or_strand_option = ctk.CTkComboBox(self.qr_code_gen_frame, width=150, height=20,
                                                        values=["STEM", "HUMMS"], command=self.combobox_callback, state="readonly")
        self.section_or_strand_option.grid(row=5, column=1, padx=10, pady=10)

        # Button to generate QR code
        self.generate_button = ctk.CTkButton(self.qr_code_gen_frame, text="Generate QR Code",
                                             command=self.generate_qr_code)
        self.generate_button.grid(row=6, column=1, pady=10)

        # qr detected flag
        self.qr_detected = None

    def combobox_callback(self, choice):
        print("Combobox selected:", choice)

    def generate_qr_code(self):
        first_name = self.entry_first_name.get()
        middle_name = self.entry_middle_name.get()
        last_name = self.entry_last_name.get()
        age = self.entry_age.get()
        social_media = self.entry_social_media.get()

        # Create QR code data string
        qr_data = f"Name: {first_name} {middle_name} {last_name}\nAge: {age}\nSocial Media: {social_media}"

        # Generate QR code
        qr_code = pyqrcode.create(qr_data)

        # folder path of saved QR code
        folder_path = 'D:\\SAMS QR'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Save the QR code in the specified folder
        qr_code_file_path = os.path.join(folder_path, f"{last_name}.png")
        qr_code.png(qr_code_file_path, scale=5)

        self.add_students_to_db()

        # clear entries after enrolling students
        self.entry_first_name.delete(0, ctk.END)
        self.entry_middle_name.delete(0, ctk.END)
        self.entry_last_name.delete(0, ctk.END)
        self.entry_age.delete(0, ctk.END)
        self.entry_social_media.delete(0, ctk.END)
        self.section_or_strand_option.option_clear()

    @staticmethod
    def read_qr_from_image():
        image_path = filedialog.askopenfilename()
        if image_path:
            image = cv2.imread(image_path)
            qr_codes = pyzbar.decode(image)
            for qr_code in qr_codes:
                qr_code_data = qr_code.data.decode('utf-8')
                print(f"Data: {qr_code_data}")

    def read_qr_codes_camera(self):
        # Initialize the camera
        cap = cv2.VideoCapture(0)  # '0' is usually the default value for the primary camera

        # Initialize the QR Code detector
        detector = cv2.QRCodeDetector()

        self.qr_detected = False

        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()

            # Check if frame is not empty
            if not ret:
                continue

            # Detect and decode the QR code
            data, bbox, _ = detector.detectAndDecode(frame)

            # If there is a QR code
            if bbox is not None and data:
                # Display the bounding box
                for i in range(len(bbox)):
                    pt1 = (int(bbox[i][0][0]), int(bbox[i][0][1]))
                    pt2 = (int(bbox[(i + 1) % len(bbox)][0][0]), int(bbox[(i + 1) % len(bbox)][0][1]))
                    cv2.line(frame, pt1, pt2, color=(255, 0, 255), thickness=2)

                # Print the QR code data
                print(f"QR Code Data: {data}")
                self.qr_detected = True

            # Display the resulting frame
            cv2.imshow('QR Code Reader', frame)

            # Press 'q' to exit the loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            if self.qr_detected:
                break

        # When everything is done, release the capture
        cap.release()
        cv2.destroyAllWindows()

    def add_students_to_db(self):
        # Retrieve user inputs
        first_name = self.entry_first_name.get()
        middle_name = self.entry_middle_name.get()
        last_name = self.entry_last_name.get()
        age = self.entry_age.get()
        social_media = self.entry_social_media.get()
        section = self.section_or_strand_option.get()

        if not middle_name.strip():
            middle_name = "Null"

        try:
            conn = mysql.connector.connect(
                host="localhost",
                username="root",
                password="",
                database="SAMS"
            )

            cursor = conn.cursor()
            students_db = f"Section: {section}"

            cursor.execute(
                "INSERT INTO students (first_name, middle_name, last_name, section_or_strand, age, social_media, students_db) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (first_name, middle_name, last_name, section, age, social_media, students_db))

            CTkMessagebox(title="Success",
                          message=f"Student {first_name} {middle_name} {last_name} has been added successfully.",
                          icon="check",
                          width=50,
                          height=30,
                          button_height=5,
                          justify="center")

            conn.commit()
            cursor.close()

        except mysql.connector.Error as e:
            CTkMessagebox(title="Database Error",
                          message=f"{e}",
                          icon="cancel",
                          width=100,
                          height=30,
                          button_height=5,
                          justify="center")


# register a new class
class RegisterClass:
    def __init__(self, master, username, passkey, user_database):
        self.master = master
        master.title("Register New Class")

        # main frame for register class
        self.class_register_frame = ctk.CTkFrame(self.master, width=200, height=300)
        self.class_register_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        # image for register class
        self.classroom_png = Image.open("presentation.png")
        self.classroom_image = ctk.CTkImage(self.classroom_png, size=(90, 90))

        self.classroom_image_label = ctk.CTkLabel(self.class_register_frame, image=self.classroom_image, text="")
        self.classroom_image_label.grid(padx=20, pady=15, row=0, column=0)

        # register page label
        self.class_register_label = ctk.CTkLabel(self.class_register_frame, text="Register", font=("", 20))
        self.class_register_label.grid(padx=20, pady=5, row=1, column=0)

        # classname entry
        self.class_name_entry = ctk.CTkEntry(self.class_register_frame, width=150, height=10,
                                             placeholder_text="classroom name")
        self.class_name_entry.grid(padx=20, pady=5, row=2, column=0)

        # number of students entry
        self.class_number_of_students = ctk.CTkEntry(self.class_register_frame, width=150, height=10,
                                                     placeholder_text="number of students")
        self.class_number_of_students.grid(padx=20, pady=5, row=3, column=0)

        # add classroom button
        self.class_add_button = ctk.CTkButton(self.class_register_frame, text="Add Class", width=150, height=7,
                                              command=self.add_class)
        self.class_add_button.grid(padx=20, pady=5, row=4, column=0)

        # filler
        self.blank = ctk.CTkLabel(self.class_register_frame, text="")
        self.blank.grid(padx=20, pady=10)

    def add_class(self):
        class_name = self.class_name_entry.get()
        student_number = self.class_number_of_students.get()

        # classname entry and number only in entry for student number validation
        if class_name and student_number.isdigit() or student_number == "":
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    username="root",
                    password="",
                    database="SAMS"
                )

                cursor = conn.cursor()
                class_database = f"class_name - {class_name}"
                cursor.execute("INSERT INTO classes(class_name, student_number, class_database) VALUES (%s, %s, %s)",
                               (class_name, student_number, class_database))
                conn.commit()
                cursor.close()

                self.master.destroy()

            except mysql.connector.Error as e:
                CTkMessagebox(title="Database Error",
                              message=f"{e}",
                              icon="cancel",
                              width=50,
                              height=30,
                              button_height=5,
                              justify="center")
        else:
            CTkMessagebox(title="Data Error",
                          message="Error parsing the data.",
                          icon="cancel",
                          width=50,
                          height=30,
                          button_height=5,
                          justify="center")


def main():
    root = ctk.CTk()
    app = Auth(root)
    root.after(0, root.state, "zoomed")
    root.mainloop()


if __name__ == "__main__":
    main()
