import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import csv


# Define global variables
users = {
    'user1': 'password1',
    'user2': 'password2',
    # Add more usernames and passwords as needed
}
def authenticate_user():
    def check_credentials():
        username = username_entry.get()
        password = password_entry.get()

        if username in users and password == users[username]:
            root.destroy()  # Close the GUI window upon successful authentication
        else:
            messagebox.showerror("Authentication Error", "Authentication failed. Please try again.")

    root = tk.Tk()
    root.title("Face Recognition Login")
    root.geometry("700x550")  # Set the window size

    # Create a colorful background
    background_color = "#3498db"
    root.configure(bg=background_color)
    hello_label = tk.Label(root, text="Made With❤️by Himanshu Yadav , CSE - 5th Sem", font=("Comic Sans MS", 14), fg="white", bg=background_color)
    hello_label.pack(side="bottom", pady=10)
    label_username = tk.Label(root, text="Username:", bg=background_color, fg="white")
    label_password = tk.Label(root, text="Password:", bg=background_color, fg="white")

    username_entry = tk.Entry(root)
    password_entry = tk.Entry(root, show="*")  # Show asterisks for the password

    login_button = tk.Button(root, text="Login", command=check_credentials, bg="green", fg="white")

    label_username.pack(pady=10)
    username_entry.pack(pady=5)
    label_password.pack()
    password_entry.pack(pady=5)
    login_button.pack(pady=10)

    root.mainloop()

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def updateAttendance(name, category, date, time):
    # Specify the full path to the external CSV file
    external_csv_path = 'Attendance.csv'  # Update the path as needed

    # Check if the person is already in the attendance list
    found = False
    updated_lines = []

    with open(external_csv_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > 0 and row[0] == name:
                found = True
                # Update the attendance record with the current category, date, and time
                if len(row) < 4:
                    row.extend([category, date, time])
                else:
                    row[1] = category
                    row[2] = date
                    row[3] = time
                updated_lines.append(row)
            else:
                updated_lines.append(row)

    if not found:
        # Add the new attendance record with category, date, and time
        updated_lines.append([name, category, date, time])

    # Write the updated attendance data back to the external CSV file
    with open(external_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(updated_lines)

    if found:
        print(f'Attendance for {name} updated at Category: {category}')
    else:
        print(f'Attendance marked for {name} at Category: {category}')

if __name__ == "__main__":
    authenticate_user()  # Call the authentication function first

    # Continue with face recognition code
    path = 'Images_Attendance'
    images = []
    classNames = []
    myList = os.listdir(path)
    print(myList)
    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
    print(classNames)

    encodeListKnown = findEncodings(images)
    print('Encoding Complete')

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open the webcam.")
        exit()

    while True:
        success, img = cap.read()

        if not success:
            print("Error: Failed to read from the webcam.")
            break

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            print(faceDis)
            matchIndex = np.argmin(faceDis)
            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
                print(name)

                # Get the current category (e.g., month), date, and time
                category = datetime.now().strftime('%B')
                date = datetime.now().strftime('%d/%m/%Y')
                time = datetime.now().strftime('%H:%M:%S')

                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 250, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

                # Update attendance with the new data
                updateAttendance(name, category, date, time)

        cv2.imshow('webcam', img)
        if cv2.waitKey(10) == 13:
            break

    cap.release()
    cv2.destroyAllWindows()
