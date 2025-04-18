# Movie Review Web App

This project is a movie review web application built using Flask, DynamoDB, and MySQL. Users can add, update, delete, and view movie reviews, as well as explore movies by genre, language, and runtime.

---

## Project Summary

The application allows users to:
- Create accounts (usernames)
- Add, update, and delete movie reviews
- Browse all user reviews 
- Query movies by genre, language, runtime, and more

## Technologies Used

- **Python 3**
- **Flask** 
- **AWS DynamoDB** 
- **MySQL** 
- **HTML** 
- **Boto3** 

---

It integrates:
- **DynamoDB** to store user accounts and nested reviews
- **MySQL** to manage movie data (such as titles, genres, languages, etc.)
- **Flask** as the web framework for handling routes, forms, and rendering HTML templates

---

## Setup & Run Instructions

1. Create a **creds.py** file that includes:

    host = "your-rds-endpoint"
    user = "your-user"
    password = "your-password"
    db = "your-database"

2. In your project directory, run:
   
    python3 flaskapp.py

3. In a browser go to:  

    http://your-ip:8080
