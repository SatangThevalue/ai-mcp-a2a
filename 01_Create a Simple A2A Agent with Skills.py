from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState
import requests  # สำหรับการเชื่อมต่อกับ OpenWeatherMap API

@agent(
    name="Weather Agent",
    description="Provides weather information",
    version="1.0.0"
)
class WeatherAgent(A2AServer):
    
    @skill(
        name="Get Weather",
        description="Get current weather for a location",
        tags=["weather", "forecast"]
    )
    def get_weather(self, location):
        """Get weather for a location using OpenWeatherMap API."""
        try:
            # เชื่อมต่อกับ OpenWeatherMap API
            api_key = "your_openweathermap_api_key"  # ใส่ API Key ของคุณที่นี่
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
            response = requests.get(url)
            response.raise_for_status()  # ตรวจสอบว่าไม่มีข้อผิดพลาด HTTP
            data = response.json()

            # ดึงข้อมูลสภาพอากาศจาก JSON
            weather_description = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            return f"The weather in {location} is {weather_description} with a temperature of {temperature}°C."
        except requests.exceptions.RequestException as e:
            # จัดการข้อผิดพลาดจาก API
            return f"Failed to get weather data: {e}"
        except KeyError:
            # จัดการข้อผิดพลาดกรณีข้อมูลไม่ครบถ้วน
            return "Weather data is incomplete or unavailable."

    def handle_task(self, task):
        """Handle incoming tasks and provide weather information."""
        # Extract location from message
        message_data = task.message or {}
        content = message_data.get("content", {})
        text = content.get("text", "") if isinstance(content, dict) else ""

        if "weather" in text.lower() and "in" in text.lower():
            location = text.split("in", 1)[1].strip().rstrip("?.")

            # Get weather and create response
            weather_text = self.get_weather(location)
            task.artifacts = [{
                "parts": [{"type": "text", "text": weather_text}]
            }]
            task.status = TaskStatus(state=TaskState.COMPLETED)
        else:
            # กรณีข้อความไม่ชัดเจน
            location = "Lam Luk Ka, Thailand"  # ตั้งค่าที่ตั้งเป็นประเทศไทย เมืองหลวง อำเภอลำลูกกา

            # Get weather for default location
            weather_text = self.get_weather(location)
            task.artifacts = [{
                "parts": [{"type": "text", "text": weather_text}]
            }]
            task.status = TaskStatus(state=TaskState.COMPLETED)
        return task

# Run the server
if __name__ == "__main__":
    agent = WeatherAgent()
    run_server(agent, port=5000)