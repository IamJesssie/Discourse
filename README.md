# Discourse Forum

A Django-based discussion forum application with topic management, post editing with time windows, and media attachment capabilities.

## Features

- User authentication (login/logout)
- Topic creation and management
- Post replies with formatting tools
- Post edit window (2 minutes by default)
- Image upload and link embedding
- Post history tracking

## Installation

### Prerequisites

- Python 3.13+
- MySQL database
- pip package manager

### Setup Steps

1. **Clone the repository**

2. **Create and activate a virtual environment**

```
python -m venv .venv
.venv\Scripts\activate
```

3. **Install dependencies**

```
pip install django
pip install mysqlclient
```

4. **Database Configuration**

The project is configured to use MySQL by default. You may need to adjust database settings in `discourse/settings.py` to match your environment:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'discourse',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

5. **Run migrations**

```
python manage.py migrate
```

6. **Create a superuser**

```
python manage.py createsuperuser
```

7. **Start the development server**

```
python manage.py runserver
```

## Testing Guide

### Login Test

1. Navigate to http://127.0.0.1:8000/
2. Log in with your superuser credentials
3. Verify redirect to topics page

### Create Topic Test

1. Click "Create New Topic"
2. Fill in title, content, and category
3. Submit the form
4. Verify topic creation success

### Post Reply Test

1. On a topic page, write a reply with text
2. Use the image upload feature to add an image
3. Use the link embedding tool to add a URL
4. Submit the reply
5. Verify the reply appears with all content types displayed correctly

### Edit Window Test (Critical Feature)

1. Immediately after posting, verify the edit button is visible
2. Click edit, make a change, and save
3. Wait exactly 2 minutes (use a timer)
4. Without refreshing the page, verify the edit button disappears automatically
5. Verify the history button remains visible
6. Refresh the page and confirm the edit button remains hidden

### Logout Test

1. Click the Logout button
2. Verify redirect to login page

## Important Note on Edit Window Functionality

The post edit window is set to 2 minutes by default. This means:
- Authors can edit their posts for only 2 minutes after posting or last edit
- After 2 minutes, the edit button will automatically disappear (via JavaScript)
- The edit button should disappear without requiring a page refresh
- The History button remains accessible even after the edit window expires

## Known Issues

- The time zone is set to UTC in settings.py, which might affect how the edit window behaves if you're in a different time zone
- If you don't see the edit button disappear after 2 minutes, check the browser console for JavaScript errors

## Developer Notes

- The post edit window duration can be changed in `settings.py` by modifying the `POST_EDIT_WINDOW_MINUTES` value
- Categories can have their own edit window duration that overrides the global setting
- Moderators and superusers can edit posts regardless of the time window