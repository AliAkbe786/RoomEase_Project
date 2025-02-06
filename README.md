# RoomEase_Project
RoomEase is a web-based platform that matches students with compatible roommates using structured questionnaires and an automated matching algorithm. It leverages Flask, Google Sheets, and OpenAI to provide real-time data management and natural language summaries of user preferences.

# Flask Roommate App

A Flask application for managing roommate requests.

## Getting Started

This project is designed to be run in a Docker container. Follow the instructions below to get started.

## Pulling the Docker Image from Docker Hub

If you prefer to run the application directly from the Docker image hosted on Docker Hub, follow these steps:

### Prerequisites

- Ensure that you have [Docker](https://www.docker.com/get-started) installed on your machine.

### Pulling the Docker Image

1. **Open Your Terminal**: Launch your terminal or command prompt.

2. **Log in to Docker Hub** (if necessary): If the image is private, you will need to log in to your Docker Hub account. Run the following command and enter your credentials when prompted:

   ```bash
   docker login
   ```

3. **Pull the Docker Image**: Use the following command to pull the Docker image from your Docker Hub repository. Replace `your-dockerhub-username` and `your-repo-name` with your actual Docker Hub username and repository name:

   ```bash
   docker pull alia53/roomease_project
   ```

### Running the Docker Container

4. **Run the Docker Container**: After pulling the image, run the following command to start the container:

   ```bash
   docker run -p 5001:5001 ## Pulling the Docker Image from Docker Hub

If you prefer to run the application directly from the Docker image hosted on Docker Hub, follow these steps:

### Prerequisites

- Ensure that you have [Docker](https://www.docker.com/get-started) installed on your machine.

### Pulling the Docker Image

1. **Open Your Terminal**: Launch your terminal or command prompt.

2. **Log in to Docker Hub** (if necessary): If the image is private, you will need to log in to your Docker Hub account. Run the following command and enter your credentials when prompted:

   ```bash
   docker login
   ```

3. **Pull the Docker Image**: Use the following command to pull the Docker image from your Docker Hub repository. Replace `your-dockerhub-username` and `your-repo-name` with your actual Docker Hub username and repository name:

   ```bash
   docker pull your-dockerhub-username/your-repo-name
   ```

   For example, if your Docker Hub username is `alia53` and your repository name is `roomease_project`, the command would be:

   ```bash
   docker pull alia53/roomease_project
   ```

### Running the Docker Container

4. **Run the Docker Container**: After pulling the image, run the following command to start the container:

   ```bash
   docker run -p 5001:5001 your-dockerhub-username/your-repo-name
   ```

   This command maps port **5001** on your local machine to port **5001** in the Docker container.

### Accessing the Application

5. **Open Your Web Browser**: After the container is running, open your web browser and go to:

   ```
   http://localhost:5001
   ```

   You should see the Flask application running./your-repo-name
   ```

   This command maps port **5001** on your local machine to port **5001** in the Docker container.

### Accessing the Application

5. **Open Your Web Browser**: After the container is running, open your web browser and go to:

   ```
   http://localhost:5001
   ```

   You should see the Flask application running.

### Database
Google Sheets is used as database in this project. Below is the link to view the database:
[https://docs.google.com/spreadsheets/d/1BzfvLFMHfbQb5x_YOFf63G4jPt02YLlvvAUQMq1M0xA/edit?usp=sharing]

### How Does The Application Work?

1. The student first logins the application with the IC Number and Matric Number
2. They are then required to answer a questionaire for compatibility assessment
3. Then they are able to request and accept roommates of their choice.

(Note: The question_status column in the database changes from False to True once the student has answered the questionaire) 

## Project Structure (If clone Github Repository)

The project includes the following directories and files:

- `app.py`: The main Flask application file.
- `requirements.txt`: Lists the Python dependencies.
- `Dockerfile`: Instructions for building the Docker image.
- `docker-compose.yml`: (Optional) If you're using Docker Compose.
- `templates/`: Contains HTML templates used for rendering the user interface.
- `.gitignore`: Specifies files to ignore in the repository, including sensitive files like `credentials.json`.
- `README.md`: Documentation about your project.
- `credentials.example.json`: Template for creating your own `credentials.json` file.

Note:
Create your own credentials.json and insert the credentials into the app.py to run the application.

## License

This project is licensed under the MIT License.
