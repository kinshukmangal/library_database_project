# library_database_project
# 📚 Library Database Management System

This repository contains a comprehensive Library Database Management System developed as part of the CS470 (Database Systems) course at Western Illinois University. The project demonstrates the integration of **Python** with **Oracle SQL Server** to simulate a secure and scalable digital library system.

---

## 🎯 Project Objectives

The system is designed to:
- Manage book inventory and borrower records
- Support admin and user login systems
- Track borrowing history, overdue returns, and book availability
- Implement face recognition for secure access to administrative functions
- Demonstrate full-stack interaction between a Python application and a relational database

---

## 🛠 Technologies Used

| Component     | Technology         |
|---------------|--------------------|
| Frontend      | Python (Tkinter, OpenCV) |
| Backend       | Oracle SQL Server (via `cx_Oracle`) |
| Image Capture | OpenCV (Face Recognition) |
| Environment   | Jupyter Notebook (development), CLI (deployment) |

---

## 🗂 Project Structure

├── DB_implementation.ipynb # Main database logic: table creation, queries
├── face_recognition.ipynb # Face detection & login authentication
├── known_face.jpg # Reference image for matching
├── captured_face.jpg # Image captured during authentication
├── library-app/ # UI and application logic (Python)
├── ERD_diagram.png (optional) # Entity-relationship diagram of the DB
├── demo_video.mp4 (optional) # Demonstration of app usage

---

## 🔐 Key Features

- 🔐 **Login System**: Distinct roles for admin and student users
- 📘 **Book Module**: Add, delete, and update book inventory
- 🧍‍♂️ **Borrower Module**: Track issue/return logs by user
- 📸 **Face Recognition**: Uses OpenCV to verify user identity
- 🧾 **SQL Queries**: All data handling via stored procedures and SQL commands
- 🧠 **Checkpoints**: Uses backups and checkpoints for safer development

---

## 📹 Demo Video

🎥 [Watch the Project Demo in the repo files!)  

---
