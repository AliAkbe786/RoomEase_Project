# RoomEase_Project
RoomEase is a web-based platform that matches students with compatible roommates using structured questionnaires and an automated matching algorithm. It leverages Flask, Google Sheets, and OpenAI to provide real-time data management and natural language summaries of user preferences.

# Flask Roommate App

A Flask application for managing roommate requests.

## Getting Started

This project is designed to be run in a Docker container. Follow the instructions below to get started.

### Prerequisites

- [Docker](https://www.docker.com/get-started) installed on your machine.
- (Optional) [Docker Compose](https://docs.docker.com/compose/install/) if you are using a `docker-compose.yml` file.

### Cloning the Repository

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/YourUsername/YourRepositoryName.git
   ```

   Replace `YourUsername` and `YourRepositoryName` with your actual GitHub username and repository name.

2. Navigate to the project directory:

   ```bash
   cd YourRepositoryName
   ```

### Setting Up Credentials

3. **Create Your Credentials File**: 
   - If your application requires a `credentials.json` file, create it based on the provided `credentials.example.json` template. 
   - Make sure to fill in the necessary details for your application.

### Building the Docker Image

4. Build the Docker image:

   ```bash
   docker build -t your-dockerhub-username/your-repo-name .
   ```

   Replace `your-dockerhub-username` and `your-repo-name` with your actual Docker Hub username and repository name.

### Running the Docker Container

5. Run the Docker container:

   ```bash
   docker run -p 5001:5001 your-dockerhub-username/your-repo-name
   ```

   This command maps port **5001** on your local machine to port **5001** in the Docker container.

### Accessing the Application

6. Open your web browser and go to:

   ```
   http://localhost:5001
   ```

   You should see the Flask application running.

## Project Structure

The project includes the following directories and files:

- `app.py`: The main Flask application file.
- `requirements.txt`: Lists the Python dependencies.
- `Dockerfile`: Instructions for building the Docker image.
- `docker-compose.yml`: (Optional) If you're using Docker Compose.
- `templates/`: Contains HTML templates used for rendering the user interface.
- `.gitignore`: Specifies files to ignore in the repository, including sensitive files like `credentials.json`.
- `README.md`: Documentation about your project.
- `credentials.example.json`: Template for creating your own `credentials.json` file.

## License

This project is licensed under the MIT License.
