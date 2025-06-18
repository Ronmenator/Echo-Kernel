# EchoKernel

EchoKernel is a flexible and extensible Python framework for building AI-powered applications. It provides a modular architecture for working with various language models, embedding providers, and vector storage solutions, making it easy to create sophisticated AI applications with tool integration capabilities.

## Features

- 🔌 **Modular Provider System**: Easily switch between different AI providers (Azure OpenAI, OpenAI)
- 🛠️ **Tool Integration**: Register and use custom tools with your language models
- 💾 **Vector Storage**: Built-in support for vector storage and similarity search
- 🧠 **Memory Management**: Store and retrieve text with associated embeddings
- 🔄 **Async Support**: Built with asyncio for efficient async/await operations
- 🤖 **Advanced Agent System**: Create complex multi-agent workflows with specialized agents

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Ronmenator/Echo-Py.git
cd Echo-Py
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Create a `config.py` file with your API credentials:

```python
AZURE_OPENAI_API_KEY = "your-azure-openai-api-key"
AZURE_OPENAI_API_BASE = "your-azure-openai-endpoint"
AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
AZURE_OPENAI_TEXT_MODEL = "your-deployment-name"
AZURE_OPENAI_EMBEDDING_MODEL = "your-embedding-deployment-name"

# Optional: For Qdrant vector storage
QDRANT_URL = "your-qdrant-url"
QDRANT_COLLECTION_NAME = "your-collection-name"
QDRANT_API_KEY = "your-qdrant-api-key"
```

## Basic Usage

Here's a simple example of how to use EchoKernel:

```python
import asyncio
from echo_kernel import EchoKernel, AzureOpenAITextProvider, AzureOpenAIEmbeddingProvider
from config import *

async def main():
    # Initialize providers
    text_provider = AzureOpenAITextProvider(
        api_key=AZURE_OPENAI_API_KEY,
        api_base=AZURE_OPENAI_API_BASE,
        api_version=AZURE_OPENAI_API_VERSION,
        model=AZURE_OPENAI_TEXT_MODEL
    )
    
    # Create and configure the kernel
    kernel = EchoKernel()
    kernel.register_provider(text_provider)
    
    # Generate text
    result = await kernel.generate_text("Tell me a joke about programming")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Features

### 1. Tool Integration

You can create and register custom tools:

```python
from echo_kernel.Tool import EchoTool

@EchoTool(description="A custom tool that does something")
def my_custom_tool(param1: str, param2: int) -> str:
    """Tool documentation"""
    # Tool implementation
    return f"Processed {param1} with {param2}"

# Register the tool
kernel.register_tool(my_custom_tool)
```

### 2. Code Interpreter Tool

EchoKernel comes with a built-in code interpreter tool that allows you to execute Python code in a sandboxed environment:

```python
from tools.CodeInterpreterTool import execute_python_code

# Register the code interpreter tool
kernel.register_tool(execute_python_code)

# Use the tool through text generation
result = await kernel.generate_text(
    "Using the code interpreter tool, write a python script that prints 'Hello, World!'"
)
print(result)
```

The code interpreter tool:
- Executes Python code in a sandboxed environment
- Has resource limits for safety
- Returns execution results including stdout and stderr
- Indicates success/failure of code execution

### 3. Vector Memory

Set up vector memory for semantic search capabilities:

```python
from echo_kernel import VectorMemoryProvider, QdrantStorageProvider

# Initialize providers
embedding_provider = AzureOpenAIEmbeddingProvider(
    api_key=AZURE_OPENAI_API_KEY,
    api_base=AZURE_OPENAI_API_BASE,
    api_version=AZURE_OPENAI_API_VERSION,
    model=AZURE_OPENAI_EMBEDDING_MODEL
)

storage_provider = QdrantStorageProvider(
    url=QDRANT_URL,
    collection_name=QDRANT_COLLECTION_NAME,
    api_key=QDRANT_API_KEY
)

memory_provider = VectorMemoryProvider(embedding_provider, storage_provider)

# Register with kernel
kernel.register_provider(embedding_provider)
kernel.register_provider(memory_provider)

# Use memory
await memory_provider.add_text("Important information to remember", {"source": "docs"})
similar_texts = await memory_provider.search_similar("What information do we have?")
```

## 🤖 Agent System

EchoKernel provides a powerful agent system that makes it incredibly easy to create complex, multi-agent workflows. With just a few lines of code, you can build sophisticated AI systems that decompose tasks, route to specialists, iterate on solutions, and maintain context.

### Available Agents

- **EchoAgent**: Basic agent with persona and tool capabilities
- **TaskDecomposerAgent**: Breaks complex tasks into subtasks and coordinates execution
- **LoopAgent**: Iteratively improves results until a stop condition is met
- **RouterAgent**: Routes tasks to the most appropriate specialist agent
- **SpecialistRouterAgent**: Enhanced router with retry logic and validation
- **MemoryAgent**: Maintains context across conversations using vector memory

### Complex Agent Example

Here's how easy it is to create a sophisticated multi-agent system that can handle complex tasks:

```python
import asyncio
from echo_kernel import EchoKernel, AzureOpenAITextProvider
from echo_kernel.EchoAgent import EchoAgent
from echo_kernel.agents.TaskDecomposerAgent import TaskDecomposerAgent
from config import *

async def main():
    # Set up the kernel
    text_provider = AzureOpenAITextProvider(
        api_key=AZURE_OPENAI_API_KEY,
        api_base=AZURE_OPENAI_API_BASE,
        api_version=AZURE_OPENAI_API_VERSION,
        model=AZURE_OPENAI_TEXT_MODEL
    )
    
    kernel = EchoKernel()
    kernel.register_provider(text_provider)
    
    # Create a basic worker agent
    executor = EchoAgent("PythonWorker", kernel, persona="You are a helpful Python expert.")
    
    # Create a task-decomposing coordinator
    planner = TaskDecomposerAgent("Planner", kernel, executor)
    
    # Run a complex task - the system will automatically:
    # 1. Break it down into subtasks
    # 2. Execute each subtask
    # 3. Coordinate the results
    task = "Create a weather notification system that fetches data and alerts users if it's raining"
    result = await planner.run(task)
    print("\n[Final Output]\n", result)

if __name__ == "__main__":
    asyncio.run(main())
```

### Example Output

When you run this code, the TaskDecomposerAgent automatically breaks down the complex task and coordinates execution:

```
[Planner] Plan generated:
1. **Research Weather APIs**: Identify and select a reliable weather API that provides real-time data and supports rain alerts.

2. **Set Up API Integration**: Implement the necessary code to fetch weather data from the chosen API, ensuring proper authentication and data retrieval.

3. **Develop Rain Detection Logic**: Create a function that analyzes the fetched weather data to determine if it indicates rain and set the criteria for what constitutes a rain alert.

4. **Implement Notification System**: Design and develop a notification mechanism (e.g., email, SMS, or app notification) that alerts users when rain is detected.

5. **Test the System**: Conduct thorough testing of the entire system, including API integration, rain detection logic, and notification delivery, to ensure it works correctly and reliably.

[Planner] Executing Subtask 1: **Research Weather APIs**: Identify and select a reliable weather API that provides real-time data and supports rain alerts.
[Planner] Executing Subtask 2: **Set Up API Integration**: Implement the necessary code to fetch weather data from the chosen API, ensuring proper authentication and data retrieval.
[Planner] Executing Subtask 3: **Develop Rain Detection Logic**: Create a function that analyzes the fetched weather data to determine if it indicates rain and set the criteria for what constitutes a rain alert.
[Planner] Executing Subtask 4: **Implement Notification System**: Design and develop a notification mechanism (e.g., email, SMS, or app notification) that alerts users when rain is detected.
[Planner] Executing Subtask 5: **Test the System**: Conduct thorough testing of the entire system, including API integration, rain detection logic, and notification delivery, to ensure it works correctly and reliably.

[Final Output]
Subtask 1 Result:
When researching weather APIs, several options stand out for their reliability, real-time data provision, and features like rain alerts. Here are a few notable ones:

### 1. **OpenWeatherMap API**
- **Overview**: A widely used weather API that provides current weather data, forecasts, and historical data.
- **Features**:
  - Real-time weather data
  - Rain alerts through notifications
  - Global coverage
  - Free tier available with limited requests
- **Documentation**: [OpenWeatherMap API Documentation](https://openweathermap.org/api)

### 2. **WeatherAPI (formerly WeatherStack)**
- **Overview**: A robust weather API that provides real-time weather information and forecasts.
- **Features**:
  - Current weather, forecast, and historical data
  - Supports rain alerts
  - Free tier with basic features
- **Documentation**: [WeatherAPI Documentation](https://www.weatherapi.com/docs/)

### 3. **Climacell (Tomorrow.io) API**
- **Overview**: Provides hyper-local weather data and has become popular for its accuracy and detail.
- **Features**:
  - Real-time weather updates
  - Rain alerts and severe weather notifications
  - Global coverage with high-resolution data
- **Documentation**: [Tomorrow.io API Documentation](https://www.tomorrow.io/weather-api/)

### 4. **AccuWeather API**
- **Overview**: A well-known weather service that offers detailed weather forecasts and alerts.
- **Features**:
  - Real-time weather data and alerts
  - Rain and severe weather alerts
  - Global weather coverage
- **Documentation**: [AccuWeather API Documentation](https://developer.accuweather.com/)

### 5. **Weatherbit API**
- **Overview**: Provides a variety of weather data including current conditions and forecasts.
- **Features**:
  - Real-time data and alerts
  - Supports rain alerts
  - Free tier available with limited access
- **Documentation**: [Weatherbit API Documentation](https://www.weatherbit.io/api)

### Conclusion
Among these options, **OpenWeatherMap** and **Tomorrow.io** (Climacell) are particularly well-regarded for their comprehensive data and alert features. The choice of API may depend on specific needs such as geographic coverage, pricing, and ease of integration.

Subtask 2 Result:
To set up API integration for fetching weather data, we typically use an API like OpenWeatherMap, WeatherAPI, or similar. Below, I'll provide a step-by-step guide including code snippets for fetching weather data using the OpenWeatherMap API as an example.

### Step 1: Sign Up for an API Key
1. Go to the [OpenWeatherMap website](https://openweathermap.org/).
2. Sign up for a free account and obtain your API key.

### Step 2: Install Required Libraries
You will need the `requests` library to make API calls. You can install it using pip if you haven't already:

```bash
pip install requests
```

### Step 3: Write Python Code to Fetch Weather Data

Here's a simple implementation:

```python
import requests

def get_weather_data(city, api_key):
    # OpenWeatherMap API endpoint
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        # Send a GET request to the API
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the JSON response
        data = response.json()

        # Extract relevant information
        weather = {
            'city': data['name'],
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed']
        }

        return weather

    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")

# Example usage
if __name__ == "__main__":
    city = "London"
    api_key = "YOUR_API_KEY"  # Replace with your OpenWeatherMap API key
    weather_data = get_weather_data(city, api_key)

    if weather_data:
        print(f"Weather in {weather_data['city']}:")
        print(f"Temperature: {weather_data['temperature']}°C")
        print(f"Description: {weather_data['description']}")
        print(f"Humidity: {weather_data['humidity']}%")
        print(f"Wind Speed: {weather_data['wind_speed']} m/s")
```

### Step 4: Replace Placeholder
Make sure to replace `YOUR_API_KEY` with the actual API key you received from OpenWeatherMap.

### Step 5: Run the Code
You can run the script, and it should print the current weather data for the specified city.

### Optional: Handle Additional Features
You might want to enhance the script by:
- Adding command-line arguments to specify the city and API key.
- Implementing caching for frequent requests to avoid hitting the API limits.
- Handling more exceptions or error responses based on your requirements.

This code provides a basic structure for fetching weather data from an API, and you can modify it as needed for your specific use case.

Subtask 3 Result:
To create a rain detection logic, we can define a function that takes in weather data as input and checks if it meets certain criteria that indicate rain. The criteria can depend on various factors such as precipitation probability, amount of rainfall, or specific weather conditions.

Here's a sample function that analyzes weather data and sets criteria for a rain alert:

```python
def rain_detection(weather_data):
    """
    Analyzes the weather data to determine if it indicates rain.

    Parameters:
    weather_data (dict): A dictionary containing weather information.
                         Expected keys:
                         - 'precipitation_probability': (int) Probability of precipitation (0-100)
                         - 'rain_amount': (float) Amount of rain (in mm)
                         - 'weather_conditions': (str) Describes the weather (e.g., 'rain', 'clear', etc.)

    Returns:
    bool: True if rain alert is triggered, False otherwise.
    str: Message describing the rain alert status.
    """

    precipitation_probability = weather_data.get('precipitation_probability', 0)
    rain_amount = weather_data.get('rain_amount', 0.0)
    weather_conditions = weather_data.get('weather_conditions', '').lower()

    # Criteria for rain alert
    if precipitation_probability > 50 or rain_amount > 2.0 or 'rain' in weather_conditions:
        return True, "Rain alert: Conditions indicate rain."

    return False, "No rain alert: Conditions do not indicate rain."

# Example usage:
weather_data_example = {
    'precipitation_probability': 60,
    'rain_amount': 3.0,
    'weather_conditions': 'Light rain'
}

alert_status, message = rain_detection(weather_data_example)
print(message)
```

### Explanation:
1. **Function Definition**: The `rain_detection` function takes a dictionary called `weather_data` as input.
2. **Extracting Data**: It extracts the probability of precipitation, amount of rain, and weather conditions from the input data.
3. **Setting Criteria**:
   - A rain alert is triggered if:
     - The probability of precipitation is greater than 50%.
     - The amount of rain is more than 2.0 mm.
     - The weather conditions include the word 'rain'.
4. **Return Values**: The function returns a boolean indicating whether a rain alert is triggered and a message describing the status.

You can modify the thresholds and conditions based on specific requirements or local weather patterns.

Subtask 4 Result:
To implement a notification system that alerts users when rain is detected, we can break down the process into several key components:

1. **Weather Data Source**: We need a reliable source to get real-time weather data, especially rain predictions. This can be done using a weather API (e.g., OpenWeatherMap).

2. **Notification Service**: We will choose a notification method (e.g., email, SMS, or app notification). For simplicity, we can use email notifications.

3. **Scheduling**: We need to periodically check the weather data to determine if rain is expected.

4. **User Management**: Store user information (e.g., email addresses) to send notifications.

5. **Integration**: Combine all these components into a cohesive system.

### Implementation Steps

1. **Set Up a Weather API**:
   - Sign up for a weather API (e.g., OpenWeatherMap) and get an API key.

2. **Email Notification**:
   - Use an email service (e.g., SMTP, SendGrid, etc.) for sending notifications.
   - For this example, we will use Python's built-in `smtplib`.

3. **Schedule Periodic Checks**:
   - Use a scheduling library like `schedule` or `APScheduler` to run the weather check at regular intervals.

4. **User Management**:
   - For simplicity, we will store emails in a list.

### Example Code

Here's a simple implementation in Python:

```python
import requests
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Weather API Configuration
API_KEY = 'YOUR_API_KEY'
CITY = 'YOUR_CITY'
WEATHER_URL = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}'

# Email Configuration
SMTP_SERVER = 'smtp.example.com'
SMTP_PORT = 587
USERNAME = 'your_email@example.com'
PASSWORD = 'your_password'
RECIPIENTS = ['recipient@example.com']  # List of email recipients

def check_weather():
    response = requests.get(WEATHER_URL)
    if response.status_code == 200:
        data = response.json()
        weather_description = data['weather'][0]['description']
        if 'rain' in weather_description:
            send_notification(weather_description)
    else:
        print("Error fetching weather data.")

def send_notification(weather_description):
    subject = 'Rain Alert!'
    body = f'Alert! Rain is detected: {weather_description}'

    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = ', '.join(RECIPIENTS)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(USERNAME, PASSWORD)
        server.send_message(msg)
        print("Notification sent!")

def run_notification_system():
    while True:
        check_weather()
        time.sleep(3600)  # Check every hour

if __name__ == "__main__":
    run_notification_system()
```

### Explanation:

1. **Weather Check**: The `check_weather` function fetches weather data from the OpenWeatherMap API. If rain is detected in the weather description, it calls the `send_notification` function.

2. **Sending Email**: The `send_notification` function constructs an email message and sends it using SMTP.

3. **Scheduling**: The `run_notification_system` function runs an infinite loop that checks the weather every hour (3600 seconds).

### Notes:
- Replace placeholders like `YOUR_API_KEY`, `YOUR_CITY`, and SMTP server details with actual values.
- For production use, consider using environment variables for sensitive information.
- Implement error handling and logging for better reliability.
- You can expand the user management system to store user preferences in a database for more complex applications.

This is a basic implementation and can be extended or modified based on specific requirements or preferences.

Subtask 5 Result:
To conduct thorough testing of a system, especially one involving API integration, rain detection logic, and notification delivery, we can approach it methodically:

### Step 1: Define Test Cases
1. **API Integration Tests**:
   - Test successful API calls to fetch weather data.
   - Test handling of API errors (e.g., 404, 500 responses).
   - Test the API response format (ensure it matches expectations).

2. **Rain Detection Logic Tests**:
   - Test scenarios with various weather conditions (rain, no rain, varying intensities).
   - Test boundary conditions (e.g., light rain thresholds).
   - Test the logic's response to unexpected data formats from the API.

3. **Notification Delivery Tests**:
   - Test successful delivery of notifications.
   - Test handling of notification failures (e.g., network issues).
   - Test different notification channels (email, SMS, push notifications).

### Step 2: Implement Test Functions
We can implement mock functions to simulate the API calls, rain detection logic, and notification delivery.

### Step 3: Execute Tests
We can execute the tests and check the results.

Since I can't perform real API calls or send notifications, I will provide a sample mock implementation in Python to illustrate how you might set up these tests.

```python
import requests
from unittest.mock import patch

# Sample weather API function
def fetch_weather_data(api_url):
    response = requests.get(api_url)
    if response.status_code != 200:
        raise Exception("API error")
    return response.json()

# Sample rain detection logic
def is_raining(weather_data):
    if "rain" in weather_data:
        return weather_data["rain"]["1h"] > 0
    return False

# Sample notification function
def send_notification(message):
    # Simulate sending a notification
    print(f"Notification sent: {message}")

# Test Cases
def test_fetch_weather_data_success():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"rain": {"1h": 0.5}}

        data = fetch_weather_data("http://mockapi/weather")
        assert data == {"rain": {"1h": 0.5}}, "Failed to fetch weather data correctly"

def test_fetch_weather_data_failure():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 404

        try:
            fetch_weather_data("http://mockapi/weather")
        except Exception as e:
            assert str(e) == "API error", "Failed to handle API error correctly"

def test_is_raining():
    weather_data = {"rain": {"1h": 0.5}}
    assert is_raining(weather_data) == True, "Rain detection failed"

    weather_data_no_rain = {}
    assert is_raining(weather_data_no_rain) == False, "Rain detection failed"

def test_send_notification():
    import io
    import sys

    # Redirect stdout to capture print statements
    captured_output = io.StringIO()
    sys.stdout = captured_output

    send_notification("It's raining!")

    # Reset redirect.
    sys.stdout = sys.__stdout__

    assert captured_output.getvalue().strip() == "Notification sent: It's raining!", "Notification not sent correctly"

# Execute tests
test_fetch_weather_data_success()
test_fetch_weather_data_failure()
test_is_raining()
test_send_notification()

print("All tests passed!")
```

### Explanation
- **Mocking**: We use mocking to simulate API responses without making actual network requests.
- **Assertions**: Each test checks if the expected output matches the actual output.
- **Print Capturing**: For the notification function, we capture printed output to verify that the correct message is sent.

### Conclusion
This is a simplified way to test the system. In a real-world scenario, you would likely use a testing framework like `unittest` or `pytest` and have more comprehensive tests, including performance testing and integration testing.
```

### More Agent Examples

#### Iterative Improvement with LoopAgent

```python
# Create an agent that iteratively improves its output
python_agent = EchoAgent("PythonDev", kernel, "You are an expert Python developer.")
looping_agent = LoopAgent("IterativePythonAgent", agent=python_agent, max_steps=5)

query = "Write a script to get weather data using the OpenWeatherMap API. Make it production ready, and state 'final version' when you are done."
result = await looping_agent.run(query)
print("\n[Final Output]\n", result)
```

#### Multi-Agent Routing

```python
# Create specialized agents
python_agent = EchoAgent("PythonCoder", kernel, "You write working Python code.")
web_agent = EchoAgent("WebResearcher", kernel, "You search and summarize online content.")

# Create a router that chooses the best agent for each task
router = RouterAgent("TaskRouter", 
                    agents={"PythonCoder": python_agent, "WebResearcher": web_agent}, 
                    router_prompt="You are a router agent. Choose PythonCoder or WebResearcher.", 
                    kernel=kernel)

result = await router.run("Write Python code to fetch weather data from an API")
print(result)
```

#### Memory-Enhanced Agent

```python
# Create an agent that remembers previous conversations
memory_agent = MemoryAgent("MemoryAgent", kernel, memory_interface, base_agent)
result = await memory_agent.run("What did we discuss about weather APIs?")
```

The agent system makes it incredibly easy to build sophisticated AI workflows. With just a few lines of code, you can create systems that:

- **Automatically decompose complex tasks** into manageable subtasks
- **Route work to specialists** based on task requirements
- **Iteratively improve results** until they meet quality standards
- **Maintain context** across multiple conversations
- **Coordinate multiple agents** to work together seamlessly

This is the power of EchoKernel's agent system - complex AI workflows made simple!

## 🚀 Quick Start Examples

To see the agent system in action, check out the examples in the `examples/` directory:

### Install in Development Mode (Recommended)

```bash
pip install -e .
```

### Run Examples

```bash
# Complex multi-agent routing example
python examples/agent-routing.py

# Task decomposition example
python examples/task-decomposer.py
```

For more details on running examples, see [examples/README.md](examples/README.md).

## Available Providers

### Text Providers
- `AzureOpenAITextProvider`: For Azure OpenAI API
- `OpenAITextProvider`: For OpenAI API

### Embedding Providers
- `AzureOpenAIEmbeddingProvider`: For Azure OpenAI embeddings
- `OpenAIEmbeddingProvider`: For OpenAI embeddings

### Storage Providers
- `QdrantStorageProvider`: For Qdrant vector database
- `InMemoryStorageProvider`: For in-memory vector storage (default)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Your License Here] 