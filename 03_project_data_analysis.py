"""
LLM Server:

- ใช้ ChatOpenAI เพื่อสร้างโมเดล LLM (GPT-3.5 Turbo) สำหรับการตอบคำถามทั่วไป
- แปลงโมเดลเป็น A2A server ที่รันบนพอร์ต 5001

Data Analysis Workflow:

- ใช้ PromptTemplate เพื่อกำหนดคำถามในบริบทของการวิเคราะห์ข้อมูล เช่น "Sales data for Q1 2025: Revenue = $1M, Profit = $200K"
- สร้าง Workflow ที่รวม Prompt, LLM และ Output Parser
- แปลง Workflow เป็น A2A server ที่รันบนพอร์ต 5002

การรันเซิร์ฟเวอร์:

- ใช้ threading เพื่อรันเซิร์ฟเวอร์ทั้งสองใน background threads

การทดสอบ:

- ใช้ A2AClient เพื่อส่งคำถามไปยังเซิร์ฟเวอร์และรับคำตอบ

พารามิเตอร์ที่ใช้:

- **model**: กำหนดโมเดลที่ใช้ เช่น "gpt-3.5-turbo"
- **temperature**: ควบคุมความสร้างสรรค์ของคำตอบ (0 = คาดเดาได้, 1 = สร้างสรรค์)
- **port**: พอร์ตที่เซิร์ฟเวอร์แต่ละตัวรัน

คำแนะนำการใช้งาน:

1. **การตั้งค่าโมเดล**: ปรับค่า temperature ให้เหมาะสมกับบริบทของคำถาม เช่น ค่า 0 สำหรับคำตอบที่ต้องการความแม่นยำสูง และค่า 0.7-1 สำหรับคำตอบที่ต้องการความหลากหลาย
2. **การปรับแต่ง Prompt**: ปรับข้อความใน PromptTemplate ให้เหมาะสมกับบริบทของข้อมูลที่ต้องการวิเคราะห์
3. **การทดสอบและปรับปรุง**: ใช้ A2AClient เพื่อทดสอบ Workflow และปรับปรุงคำถามหรือโครงสร้าง Workflow ตามผลลัพธ์ที่ได้
"""

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from python_a2a import A2AClient, run_server
from python_a2a.langchain import to_a2a_server
import threading

# สร้าง LangChain LLM สำหรับการวิเคราะห์ข้อมูลโครงการ
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# แปลง LLM เป็น A2A server
llm_server = to_a2a_server(llm)

# สร้าง Workflow สำหรับการวิเคราะห์ข้อมูลโครงการ
# Prompt Template สำหรับการวิเคราะห์ข้อมูลและสร้างรายงาน
template = "You are a data analysis assistant.\n\nRaw Data: {data}\n\nAnalysis Report:"
prompt = PromptTemplate.from_template(template)
data_analysis_chain = prompt | llm | StrOutputParser()

# แปลง Workflow เป็น A2A server
data_analysis_server = to_a2a_server(data_analysis_chain)

# รันเซิร์ฟเวอร์ใน background threads
llm_thread = threading.Thread(
    target=lambda: run_server(llm_server, port=5001),
    daemon=True
)
llm_thread.start()

data_analysis_thread = threading.Thread(
    target=lambda: run_server(data_analysis_server, port=5002),
    daemon=True
)
data_analysis_thread.start()

# ทดสอบเซิร์ฟเวอร์
llm_client = A2AClient("http://localhost:5001")
data_analysis_client = A2AClient("http://localhost:5002")

llm_result = llm_client.ask("What is the capital of France?")
data_analysis_result = data_analysis_client.ask('{"data": "Sales data for Q1 2025: Revenue = $1M, Profit = $200K"}')

print("LLM Result:", llm_result)
print("Data Analysis Result:", data_analysis_result)