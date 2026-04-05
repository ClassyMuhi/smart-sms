
# Smart SMS

An intelligent messaging system developed to simplify and organize SMS communication.

## Overview

Smart SMS enables users to send predefined messages, schedule SMS delivery, and efficiently manage conversations in a structured manner. The system is designed to reduce manual effort by automating routine messaging tasks such as reminders, notifications, and repeated communications.

## Project Structure

```
smart-sms/
├── smartsms/                    # Django project root
│   ├── smartsms/               # Django settings & configuration
│   ├── auth_module/            # Authentication & user management
│   ├── contact_management/     # Contact management module
│   ├── manage.py              # Django management script
│   ├── requirements.txt        # Python dependencies
│   └── db.sqlite3             # Database
├── docs/                        # Documentation
│   ├── QUICKSTART.md
│   ├── API_EXAMPLES.md
│   ├── MODELS_DOCUMENTATION.md
│   ├── CONTACT_MANAGEMENT_GUIDE.md
│   └── ...
├── scripts/                     # Utility scripts
│   ├── create_admin.py         # Admin user creation
│   ├── summa.py
│   ├── startup.sh              # Linux startup script
│   └── startup.bat             # Windows startup script
├── tests/                       # Test files
│   └── test_register.py
├── .env.example                # Environment variables template
├── .gitignore
├── README.md
└── venv/                        # Virtual environment (excluded from git)
```

## Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ClassyMuhi/smart-sms.git
   cd smart-sms
   ```

2. **Set up Python virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   cd smartsms
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create admin user**
   ```bash
   python scripts/create_admin.py
   ```

7. **Start the server**
   ```bash
   python manage.py runserver
   ```

## Features

- Send predefined messages
- Schedule SMS delivery
- Contact management
- Message templates
- User authentication
- Conversation tracking

## Documentation

See the [docs/](./docs/) folder for detailed documentation:
- [API Examples](./docs/API_EXAMPLES.md)
- [Models Documentation](./docs/MODELS_DOCUMENTATION.md)
- [Contact Management Guide](./docs/CONTACT_MANAGEMENT_GUIDE.md)

## Scripts

Utility scripts are located in the [scripts/](./scripts/) folder:
- `startup.sh` / `startup.bat` - Start the application
- `create_admin.py` - Create an admin user

## Testing

Run tests from the project root:
```bash
cd smartsms
python manage.py test
```

Or run specific test files from the [tests/](./tests/) folder.

## Technology Stack

- **Backend**: Django
- **Database**: SQLite
- **Language**: Python
- **API**: REST API

## License

[Add your license here]

## Author

ClassyMuhi
