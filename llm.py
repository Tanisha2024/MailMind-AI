import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")

client = Groq(api_key=api_key)


def analyze_email(email_text):

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": """
You are MailMind AI, an intelligent email analysis assistant.

Analyze the email and return the following information:

- summary
- category
- priority
- action_items
- suggested_reply

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations outside the JSON.
"""
            },
            {
                "role": "user",
                "content": email_text
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "email_analysis",
                "schema": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string"
                        },
                        "category": {
                            "type": "string"
                        },
                        "priority": {
                            "type": "string"
                        },
                        "action_items": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "suggested_reply": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "summary",
                        "category",
                        "priority",
                        "action_items",
                        "suggested_reply"
                    ],
                    "additionalProperties": False
                }
            }
        }
    )

    result = json.loads(
        response.choices[0].message.content
    )

    return result
def generate_reply(email_text):

    stream = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": """
You are MailMind AI, a professional email reply assistant.

Write a natural, concise, professional reply to the email.

Rules:
- Respond directly to the sender.
- Acknowledge the email.
- Address the main request or action.
- Keep the reply brief.
- Do not invent information.
- Do not add placeholders such as [Phone Number] or [LinkedIn].
- Do not add a subject line unless explicitly requested.
- Do not add explanations before or after the reply.
- Return only the email body.
"""
            },
            {
                "role": "user",
                "content": email_text
            }
        ],
        stream=True
    )

    for chunk in stream:
        content = chunk.choices[0].delta.content

        if content:
            yield content

def create_task(task, deadline):
    return {
        "status": "success",
        "task": task,
        "deadline": deadline
    }

tools = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a task when an email requires the user to take an action.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The action the user needs to complete."
                    },
                    "deadline": {
                        "type": "string",
                        "description": "The deadline for completing the task."
                    }
                },
                "required": ["task", "deadline"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_email",
            "description": "Save an email when the user wants to store or archive it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email_text": {
                        "type": "string",
                        "description": "The complete email text."
                    },
                    "category": {
                        "type": "string",
                        "description": "The category of the email."
                    }
                },
                "required": ["email_text", "category"],
                "additionalProperties": False
            }
        }
    }
]
def handle_tool_request(email_text):

    messages = [
        {
            "role": "system",
            "content": """
You are MailMind AI.

Analyze the email and choose the appropriate tool.

Use create_task when the email contains an action the user
needs to complete.

Use save_email when the email should be stored or archived.

Use a tool only when appropriate.
"""
        },
        {
            "role": "user",
            "content": email_text
        }
    ]

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    if not message.tool_calls:
        return message.content

    messages.append(message)

    tool_results = []

    for tool_call in message.tool_calls:

        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        if function_name == "create_task":

            result = create_task(
                arguments["task"],
                arguments["deadline"]
            )

        elif function_name == "save_email":

            result = save_email(
                arguments["email_text"],
                arguments["category"]
            )

        else:
            result = {
                "status": "error",
                "message": "Unknown tool."
            }

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })

        tool_results.append(result)

    final_response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages
    )

    return final_response.choices[0].message.content

def save_email(email_text, category, priority="", summary=""):
    import json
    from datetime import datetime

    try:
        with open("emails.json", "r", encoding="utf-8") as file:
            emails = json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        emails = []

    new_email = {
        "id": len(emails) + 1,
        "category": category,
        "priority": priority,
        "summary": summary,
        "email": email_text,
        "saved_at": datetime.now().isoformat()
    }

    emails.append(new_email)

    with open("emails.json", "w", encoding="utf-8") as file:
        json.dump(emails, file, indent=4)

    return {
        "status": "success",
        "message": "Email saved successfully.",
        "email_id": new_email["id"]
    }
def load_emails():
    import json

    try:
        with open("emails.json", "r", encoding="utf-8") as file:
            return json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        return []