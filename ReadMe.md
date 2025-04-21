# YouTube RAG Project

## Overview
The YouTube RAG project is designed to provide a robust framework for building applications that integrate with YouTube and utilize Retrieval-Augmented Generation (RAG) techniques.
## Project Structure
```
app.py
docker-compose.yml
main.py
server.py
ReadMe.md
__pycache__/
```

- **app.py**: Entry point for the Flask server.
- **docker-compose.yml**: Configuration for containerized deployment.
- **main.py**: Main script for the application.
- **server.py**: Backend server logic.
- **ReadMe.md**: Documentation for the project.
- **__pycache__/**: Compiled Python files.

## Prerequisites
- Python 3.12 or higher
- Docker

## Setup Instructions

### Backend
1. Navigate to the `
YouTube_RAG_ChatApp` directory and create a virtual env:
   ```bash
   python -m venv venv
   ```
2. Activate the virtual env:
   ```bash
   .\.venv\Scripts\activate
   ```
3. Install the require modules:
   ```bash
   pip install -r requirements.txt
   ```

## Running Docker
1. Make sure docker engine is running:

2. Start qdrant db server.
    ```bash
   docker compose up -d
   ```
## Running the Project
```bash
streamlit run app.py
```

## Contributing
Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License.