# 🌐 Multi-Agent System with Tools (OpenAI Agents SDK)

This project demonstrates how to build a **multi-agent system** using the [OpenAI Agents Python SDK](https://openai.github.io/openai-agents-python/agents/).

It shows how to:  
- Configure agents with **custom instructions** (static & dynamic)  
- Use **function tools** for tasks like weather queries  
- Handle **custom tool results** (`ToolsToFinalOutputResult`)  
- Work with **handoffs** between agents  
- Integrate external models (Gemini via `AsyncOpenAI`)  
- Define **typed outputs** with `pydantic` models  
- Clone agents for reusability  

## **🤖 Agents Overview**

### **1. Weather Agent**

* Uses @function_tool → get_weather(city)
* Dynamic instructions via a Python function
* Enforced tool use with ModelSettings(tool_choice="get_weather")
* Configured with tool_use_behavior="stop_on_first_tool"

### **2. Calendar Agent**

* Extracts structured calendar events
* Output type defined using a pydantic.BaseModel

```python
class CalenderEvent(BaseModel):
    name: str
    date: str
    participants: list[str]
```

### **3. User Context Agent**

* Works with a dataclass context
```python
@dataclass
class UserContext:
    name: str
    uid: str
    is_pro_user: bool
```
### **4. Main Agent**

* Delegates queries to specialist agents (handoffs)
* Can clone existing agents and adjust their behavior

## **🔧 Custom Tool Handling**

* This project demonstrates custom tool result handling with ToolsToFinalOutputResult:

```python
def custom_tool_handle(context, tool_result):
    for result in tool_result:
        if result.output and "sunny" in result.output:
            return ToolsToFinalOutputResult(
                is_final_output=True,
                final_output=f"Final Weather: {result.output}",
            )
```
