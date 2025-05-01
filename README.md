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

- Linux/Unix-based operating system
- C compiler (gcc recommended)
- Basic understanding of networking concepts and HTTP protocol

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mini-web-server.git
   cd mini-web-server
   ```

2. Compile the server:
   ```bash
   make
   ```

## Usage

1. Start the server:
   ```bash
   ./server [port]
   ```
   If no port is specified, the server will run on the default port (8080).

2. Access the server:
   Open your web browser and navigate to `http://localhost:8080`

## Configuration

The server can be configured by modifying the following settings in the configuration file:

- Port number
- Document root directory
- Log file location
- Maximum concurrent connections
- Timeout settings

## Project Structure

```
mini-web-server/
├── src/
│   ├── main.c
│   ├── server.c
│   ├── http.c
│   └── utils.c
├── include/
│   ├── server.h
│   ├── http.h
│   └── utils.h
├── public/
│   └── index.html
├── Makefile
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by the Nginx web server architecture
- Thanks to all contributors who have helped with the project

## Contact

Your Name - your.email@example.com
Project Link: https://github.com/yourusername/mini-web-server 