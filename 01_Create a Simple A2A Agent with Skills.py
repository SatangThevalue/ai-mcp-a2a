"""
WeatherAgent เป็นคลาสที่สืบทอดมาจาก A2AServer ซึ่งมีหน้าที่ให้ข้อมูลสภาพอากาศ

- @agent: ใช้สำหรับกำหนดข้อมูลเมตาของ Agent เช่น ชื่อ คำอธิบาย และเวอร์ชัน
- @skill: ใช้สำหรับกำหนดทักษะ (Skill) ที่ Agent มี เช่น การดึงข้อมูลสภาพอากาศ
- get_weather: ฟังก์ชันที่ใช้สำหรับดึงข้อมูลสภาพอากาศ (ในที่นี้เป็น Mock Data)
- handle_task: ฟังก์ชันที่ใช้จัดการ Task โดยตรวจสอบข้อความที่ได้รับและตอบกลับด้วยข้อมูลสภาพอากาศ

แนวทางการปรับปรุง:
1. เชื่อมต่อกับ API จริงสำหรับดึงข้อมูลสภาพอากาศ เช่น OpenWeatherMap API
2. เพิ่มการจัดการข้อผิดพลาด เช่น กรณีที่ข้อความไม่ชัดเจนหรือ API ล้มเหลว
3. เพิ่มการรองรับหลายภาษาในข้อความตอบกลับ
"""
from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState

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
        """Get weather for a location."""
        # Mock implementation
        return f"It's sunny and 75°F in {location}"
    
    def handle_task(self, task):
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
            task.status = TaskStatus(
                state=TaskState.INPUT_REQUIRED,
                message={"role": "agent", "content": {"type": "text", 
                         "text": "Please ask about weather in a specific location."}}
            )
        return task

# Run the server
if __name__ == "__main__":
    agent = WeatherAgent()
    run_server(agent, port=5000)