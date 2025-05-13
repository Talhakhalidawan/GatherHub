# GatherHub

GatherHub is a feature-rich social networking platform built with Django. The application provides a space for users to connect, share posts, follow friends, and engage through comments and likes.

## Features

- **User Authentication & Profiles**
  - User registration and login
  - Customizable user profiles with profile pictures and cover images
  - User verification system

- **Social Interaction**
  - Follow/unfollow other users
  - News feed with posts from followed users
  - Like and comment on posts
  - Comment replies and likes on comments
  - Real-time notifications for activities

- **Posts & Media**
  - Create posts with multiple images
  - Privacy settings for posts (Public, Private, Friends Only)
  - View post details and engagement metrics

- **Messaging**
  - Direct messaging between users
  - Chat list and conversation views

- **Additional Features**
  - Profile verification request system
  - Password reset functionality
  - User settings and profile customization
  - Help/support system

## Technical Stack

- **Backend**: Django
- **Database**: SQLite (default)
- **Frontend**: HTML, CSS, JavaScript (based on Django templates)
- **Media Storage**: Local storage

## Installation & Setup

### Prerequisites
- Python 3.8+ installed
- Git installed
- pip package manager

### Clone the Repository

```bash
git clone https://github.com/Talhakhalidawan/GatherHub.git
cd GatherHub
```

### Create a Virtual Environment (Optional but Recommended)

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Database Setup

```bash
python manage.py migrate
```

### Create a Superuser (Admin)

```bash
python manage.py createsuperuser
```

### Run the Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser to access the application.

## Usage

1. Register a new account or log in with existing credentials
2. Complete your profile setup with images and personal information
3. Start following other users to see their posts in your feed
4. Create posts, interact with other posts through likes and comments
5. Explore other users through the people directory
6. Use the messaging feature to connect with other users

## Admin Access

Access the admin panel at `http://127.0.0.1:8000/admin/` using the superuser credentials created earlier.

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some feature'`)
5. Push to the branch (`git push origin feature-branch`)
6. Open a Pull Request

## License

This project is open-source and available under the MIT License. 