# Mini Web Server (Nginx-like)

A lightweight web server implementation inspired by Nginx, built for learning and demonstration purposes.

## Features

- Static file serving
- Basic HTTP request handling
- Simple routing system
- Support for common HTTP methods (GET, POST)
- Error handling and logging
- Configurable server settings

## Prerequisites



## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hackerspider09/Mini-Nginx.git
   cd Mini-Nginx/mini-nginx
   ```

2. Run server:
   ```bash
   python3 main.py  
   ```

## Usage



## Configuration



## Project Structure

```
├── mini-nginx
│   ├── config.yaml
│   ├── core
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── helper.py
│   │   ├── logger.py
│   │   ├── proxy.py
│   │   ├── router.py
│   │   ├── server.py
│   │   └── worker.py
│   ├── logs
│   ├── main.py
│   ├── requirements.txt
│   └── static
│       ├── errors
│       │   ├── 400.html
│       │   └── 404.html
│       ├── index.html
│       └── root.html
├── README.md
└── web_app
    ├── socket_client.py
    └── web_application.py
```
