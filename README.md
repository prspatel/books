# Books


# Overview

In this project, I have built a book review website. Users are able to register for the website and then log in using their username and password. Once they log in, they will be able to search for books, leave reviews for individual books, and see the reviews made by other people. The websote also uses a third-party API by Goodreads, another book review website, to pull in ratings from a broader audience. Finally, users are able to query for book details and book reviews programmatically via website’s API.

# Description
### Register
![register](https://user-images.githubusercontent.com/27906355/85608421-09a2db80-b623-11ea-81da-d23cb215e57e.JPG)
### Login
![login](https://user-images.githubusercontent.com/27906355/85608467-16bfca80-b623-11ea-844a-e8b7366ab50a.JPG)
### Search a book by ISBN, author, year or nothing specific.
![search](https://user-images.githubusercontent.com/27906355/85608529-263f1380-b623-11ea-90a9-1d92012292ab.JPG)
### Search results
![search results](https://user-images.githubusercontent.com/27906355/85608576-31923f00-b623-11ea-8809-e0bc91f2cdac.JPG)
### Book description
![book page](https://user-images.githubusercontent.com/27906355/85608580-32c36c00-b623-11ea-97c2-6ac942dda2bc.JPG)
### API call for book
![API](https://user-images.githubusercontent.com/27906355/85609143-c39a4780-b623-11ea-9ab2-443fed2bbaa6.JPG)

# Set up your own (Instructions for windows)

1) git clone repository_address
2) cd project1 #move to the project directory
3) set FLASK_APP=application.py
4) set DATABASE_URL=postgres database url
5) set GOODREADS_KEY=goodreads key
6) flask run
7) if error on 'flask run' command, try setting FLASK_ENV=development and run command 'python -m flask run'

# Database Schema
![db_schema](https://user-images.githubusercontent.com/27906355/85610650-2d672100-b625-11ea-8dc7-f8e49643996b.JPG)
