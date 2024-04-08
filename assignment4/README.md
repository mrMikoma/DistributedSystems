# How to use?

This guide will walk you through the process of initializing a Python 3 project with Pip's virtual environment (venv) and running Redis database using Docker.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Docker: [Install Docker](https://docs.docker.com/get-docker/)
- Python 3: [Install Python 3](https://www.python.org/downloads/)

Disclaimer that I have used Linux while developing and testing this project. I cannot ensure that everything works with other operating systems.

## Database setup 

0. **Change Directory into the Redis Directory:**
   Run the following command in your terminal to change into correct directory:
   ```bash
   cd server/redis/
   ```

1. **Create .env File in the Redis Directory:**
   Create `.env` file inside the redis directory and add following lines:
   ```bash      
   REDIS_PASSWORD=my_password
   ```
   Please change variables according to your Redis database.

2. **Run Redis Database:**
   Execute the following command to run the Redis database:
   ```bash
   docker-compose up -d
   ```

## Server setup

0. **Change Directory into the Node Directory:**
   Run the following command in your terminal to change into correct directory:
   ```bash
   cd server/node/
   ```

1. **Create a Python Virtual Environment:**
   Run the following command in your terminal to create a Python virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. **Install Dependencies:**
   Install the required dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Activate the Virtual Environment:**
   Activate the virtual environment using the appropriate command for your operating system:
   - On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Create .env File in the Node Directory:**
   Create `.env` file inside the node directory and add following lines:
   ```bash
   REDIS_HOST=localhost        
   REDIS_PASSWORD=my_password
   ```

   Please change variables according to your Redis database.


5. **Start the Server:**
   Once the Redis database is running, run the Python server with:
   ```bash
   python3 ./main.py
   ```

6. **Stop the Server:**
   You can stop the server by pressing: Control + C, in the console.

## Client usage 

0. **Change Directory into the Client Directory:**
   Run the following command in your terminal to change into correct directory:
   ```bash
   cd client/
   ```
2. **Run Client**
   Execute the following command to run the Python client:
   ```bash
   python3 ./main.py
   ```

## Additional Notes

- Don't forget to deactivate the virtual environment once you're done:
   ```bash
   deactivate
   ```
- Don't forget to stop the Redis database in the redis directory once you're done:
   ```bash
   docker-compose down
   ```

## Troubleshooting

- Check Redis database using docker commands.
