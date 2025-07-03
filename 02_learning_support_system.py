from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from python_a2a import A2AClient, run_server
from python_a2a.langchain import to_a2a_server
import threading

# สร้าง LangChain LLM สำหรับระบบช่วยเหลือการเรียน
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# แปลง LLM เป็น A2A server
llm_server = to_a2a_server(llm)

# สร้าง Workflow สำหรับระบบช่วยเหลือการเรียน
# Prompt Template สำหรับการตอบคำถามเกี่ยวกับเนื้อหาวิชาเรียน
template = "You are a helpful learning assistant.\n\nQuestion: {query}\n\nAnswer:"
prompt = PromptTemplate.from_template(template)
learning_chain = prompt | llm | StrOutputParser()

# แปลง Workflow เป็น A2A server
learning_server = to_a2a_server(learning_chain)

# รันเซิร์ฟเวอร์ใน background threads
llm_thread = threading.Thread(
    target=lambda: run_server(llm_server, port=5001),
    daemon=True
)
llm_thread.start()

learning_thread = threading.Thread(
    target=lambda: run_server(learning_server, port=5002),
    daemon=True
)
learning_thread.start()

# ทดสอบเซิร์ฟเวอร์
llm_client = A2AClient("http://localhost:5001")
learning_client = A2AClient("http://localhost:5002")

llm_result = llm_client.ask("What is the capital of France?")
learning_result = learning_client.ask('{"query": "Explain the concept of Big Data."}')

print("LLM Result:", llm_result)
print("Learning Assistant Result:", learning_result)