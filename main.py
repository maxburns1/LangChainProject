from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, ToolMessage

from mypricing_tool import pricing_tool
from myscheduling_tool import scheduling_tool
from mycalendar_booking_tool import create_calendar_event_tool

# later add:
# from mycalendar_booking_tool import create_calendar_event_tool
# from mycommunication_tool import communication_tool

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

tools = [pricing_tool, scheduling_tool,create_calendar_event_tool]

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt="""
You are a handyman service assistant.

Use pricing_tool when the user asks for a quote or estimate.
Use scheduling_tool when the user asks for appointment availability.
Use create_calendar_event_tool only after the user clearly confirms a specific appointment slot.

When scheduling_tool returns available slots, present them as numbered options using the option_number field.
Encourage the user to reply with the option number they want.

Do not book anything unless the user has clearly confirmed a slot.

If multiple things are requested, call multiple tools and combine the results into one response.
"""
)

def print_agent_response(response):
    messages = response["messages"]

    print("\n===== AGENT TRACE =====\n")

    for msg in messages:
        if isinstance(msg, AIMessage):
            if getattr(msg, "tool_calls", None):
                for tc in msg.tool_calls:
                    print(f"TOOL CALL: {tc.get('name')}")
                    print(f"ARGUMENTS: {tc.get('args')}")
                    print()
            else:
                if isinstance(msg.content, str):
                    print("FINAL RESPONSE:")
                    print(msg.content)
                    print()
                elif isinstance(msg.content, list):
                    text_parts = []
                    for part in msg.content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            text_parts.append(part.get("text", ""))
                    output = "\n".join(text_parts).strip()
                    print("FINAL RESPONSE:")
                    print(output)
                    print()

        elif isinstance(msg, ToolMessage):
            print(f"TOOL OUTPUT ({msg.name}):")
            print(msg.content)
            print()


def main():
    conversation = []

    while True:
        user_input = input("> ")

        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Goodbye.")
            break

        conversation.append({"role": "user", "content": user_input})

        response = agent.invoke({"messages": conversation})
        print_agent_response(response)

        conversation.extend(response["messages"])


if __name__ == "__main__":
    main()