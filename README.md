# NTPU LineBot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://hub.docker.com/r/garyellow/ntpu-linebot)
[![Sanic](https://img.shields.io/badge/framework-sanic-blue.svg)](https://sanic.dev/)

A LINE Bot for querying National Taipei University (NTPU) public information. This bot provides convenient access to student information, course data, and contact details through an intuitive chat interface.

## ✨ Features

### 📚 Course Information
- **Course Search**: Find courses by course name (Day & Night divisions)
- **Teacher Search**: Find courses taught by specific teachers (Day & Night divisions)
- **Course Details**: View detailed course information including syllabus, schedule, and location

### 📞 Contact Information
- **Directory Search**: Find contact information for departments and staff
- **Organization Search**: Browse administrative and academic units
- **Emergency Contacts**: Quick access to campus emergency phone numbers
- **Individual Contacts**: Find staff members with their extensions and email addresses

### 🎓 Student Information (Legacy)
- **Student ID → Name**: Query student name by ID (Day & Night divisions)
- **Name → Student ID**: Query student ID by name (Day division only)
- **Department Name → Code**: Get department code by name (Day division only)
- **Department Code → Name**: Get department name by code (Day division only)
- **Student Lists**: Get student list by admission year and department (Day division only)

## 📞 Add as Friend

**LINE ID**: [@148wrcch](https://lin.ee/QiMmPBv)

[![Add Friend](add_friend/S_add_friend_button.png)](https://lin.ee/QiMmPBv)

![QR Code](add_friend/S_gainfriends_qr.png)

## 🏗️ Architecture

This project is built with modern async Python technologies:

- **Framework**: Sanic (Async web framework)
- **LINE SDK**: line-bot-sdk v3 (LINE Bot API support)
- **Web Scraping**: BeautifulSoup4 + httpx (Async HTTP client)
- **Caching**: asyncache + cachetools (TTL and LRU caching)
- **Containerization**: Docker with multi-stage builds
- **Error Handling**: Comprehensive exception handling and service monitoring

### Core Components
- **Message Router**: Intelligent message routing between bot modules
- **Bot Modules**: Specialized handlers for ID, Course, and Contact queries
- **Health Monitoring**: Service health checks and automatic recovery
- **Rich Menu Support**: Enhanced user interaction capabilities

## 📊 Data Sources

1. [NTPU Campus Directory](https://sea.cc.ntpu.edu.tw/pls/ld/campus_dir_m.main) - Contact information and organizational structure
2. [NTPU Course Query System](https://sea.cc.ntpu.edu.tw/pls/dev_stud/course_query_all.CHI_MAIN) - Course schedules and information
3. [NTPU Digital Learning Platform 2.0](https://lms.ntpu.edu.tw) *(Legacy student data only)*

> **Important Note**: Student-related functions contain data only up to Academic Year 113 (2024). Course and contact information are updated dynamically.

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- [Poetry](https://python-poetry.org/) (for development)
- Docker (for production deployment)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/garyellow/ntpu-linebot.git
   cd ntpu-linebot
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Activate virtual environment**
   ```bash
   poetry shell
   ```

4. **Set environment variables**
   ```bash
   # Option 1: Copy and edit .env file
   cp .env.example .env
   # Edit .env with your LINE channel credentials

   # Option 2: Export directly (Windows CMD)
   set LINE_CHANNEL_ACCESS_TOKEN=your_access_token
   set LINE_CHANNEL_SECRET=your_channel_secret

   # Option 2: Export directly (PowerShell)
   $env:LINE_CHANNEL_ACCESS_TOKEN="your_access_token"
   $env:LINE_CHANNEL_SECRET="your_channel_secret"

   # Option 2: Export directly (Unix/Linux/macOS)
   export LINE_CHANNEL_ACCESS_TOKEN="your_access_token"
   export LINE_CHANNEL_SECRET="your_channel_secret"
   ```

5. **Run development server**
   ```bash
   sanic app:app --debug
   ```

The server will start on `http://localhost:8000`

## 🐳 Production Deployment

### Using Docker Compose

1. **Prepare environment file**
   ```bash
   cd docker
   cp .env.example .env
   # Edit .env with your LINE channel credentials
   ```

2. **Deploy**
   ```bash
   docker compose up -d
   ```

The service will be available on port `10000`.

### Manual Docker Run

```bash
docker run -d \
  -p 10000:10000 \
  -e LINE_CHANNEL_ACCESS_TOKEN="your_token" \
  -e LINE_CHANNEL_SECRET="your_secret" \
  garyellow/ntpu-linebot:latest
```

### Update to Latest Version

```bash
cd docker
docker compose down
docker compose pull
docker compose up -d
```

Or use the provided update script:
```bash
chmod +x update.sh
./update.sh
```

## 📖 Usage Examples

### Student Queries
```
學生 412345678          # Query by student ID
學生 小明                # Query by name (partial match)
學生 林小明              # Query by full name
```

### Department Queries
```
科系 資工系              # Get department code by short name
科系 資訊工程學系        # Get department code by full name
系代碼 85                # Get department name by code
所有系代碼               # Display all department codes
```

### Year-based Student Lists
```
學年 112                 # Select department for year 112 students
學年 113                 # Select department for year 113 students
```

### Course Queries
```
課程 程式設計            # Find programming courses
教師 李小美              # Find courses by teacher name
```

### Contact Queries
```
聯繫 資工系              # Find contact info for CS department
聯繫 註冊組              # Find contact info for registration office
緊急                     # Display emergency contact numbers
```

### Help and Instructions
```
使用說明                 # Show detailed usage instructions
help                     # Show usage instructions (English)
```

### Interactive Features
- **Rich Menus**: Use buttons for easy navigation
- **Postback Actions**: Click on course names for detailed information
- **Carousel Templates**: Browse multiple results easily
- **Copy Actions**: One-click copy for phone numbers and emails

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Bot channel access token | Yes |
| `LINE_CHANNEL_SECRET` | LINE Bot channel secret | Yes |

### Health Checks

- `GET /healthz` - Basic health check endpoint
- `GET /healthy` - Comprehensive service health check (verifies all modules)

### API Endpoints

- `GET /` - Redirects to project GitHub repository
- `POST /callback` - LINE Bot webhook endpoint for message processing

## 📁 Project Structure

```
ntpu-linebot/
├── app.py                        # Main Sanic application with webhook handling
├── pyproject.toml                # Project dependencies and build configuration
├── poetry.lock                   # Locked dependency versions
├── Dockerfile                    # Multi-stage Docker build configuration
├── ntpu_linebot/                 # Core bot modules
│   ├── __init__.py               # Package initialization and exports
│   ├── abs_bot.py                # Abstract bot base class
│   ├── line_api_util.py          # LINE API client wrapper
│   ├── line_bot_util.py          # LINE Bot message utilities
│   ├── route_util.py             # Message routing and event handling
│   ├── normal_util.py            # Common utility functions
│   ├── sticker_util.py           # Sticker message handling
│   ├── contact/                  # Contact search module
│   │   ├── __init__.py           # Module exports
│   │   ├── bot.py                # Contact bot implementation
│   │   ├── contact.py            # Contact data models
│   │   ├── request.py            # Web scraping for contact data
│   │   └── util.py               # Contact utility functions
│   ├── course/                   # Course search module
│   │   ├── __init__.py           # Module exports
│   │   ├── bot.py                # Course bot implementation
│   │   ├── course.py             # Course data models
│   │   ├── request.py            # Web scraping for course data
│   │   └── util.py               # Course utility functions
│   └── id/                       # Student ID module
│       ├── __init__.py           # Module exports
│       ├── bot.py                # ID bot implementation
│       ├── request.py            # Student data handling
│       └── util.py               # ID utility functions
├── docker/                       # Docker deployment configurations
│   ├── docker-compose.yml        # Production deployment setup
│   ├── update.sh                 # Automated update script
│   └── .env.example              # Environment variables template
├── rich_menu/                    # LINE Rich Menu assets
│   └── default/                  # Default rich menu configuration
│       ├── default.png           # Menu background image
│       └── default_richmenu.json # Menu structure definition
├── add_friend/                   # Friend invitation assets
│   ├── *_add_friend_button.png   # Add friend buttons
│   └── *_gainfriends_qr.png      # QR codes for different sizes
└── assets/                       # Static application assets
    └── rip.png                   # Application assets
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and feature requests.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ⚠️ Disclaimer

This bot aggregates publicly available information from NTPU systems. The data may not always be accurate or up-to-date. Use at your own discretion.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
