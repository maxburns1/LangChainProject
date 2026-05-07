from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, ToolMessage

from mypricing_tool import pricing_tool
from myscheduling_tool import scheduling_tool
from mycalendar_booking_tool import create_calendar_event_tool


load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0
)

tools = [pricing_tool, scheduling_tool,create_calendar_event_tool]

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt="""
You are Marcus, the booking coordinator for Gleam Mobile Detailing. You're friendly, knowledgeable about cars, and proud of the work the team does. You speak conversationally — not too formal, not too salesy.

Use pricing_tool when the customer asks for a quote or estimate.
Use scheduling_tool when the customer asks about availability.
Use create_calendar_event_tool only after the customer clearly confirms a specific appointment slot.

When scheduling_tool returns available slots, present them as numbered options using the option_number field. Ask the customer which one works for them.

Do not book anything unless the customer has clearly confirmed a slot.

If the customer mentions a luxury vehicle (Tesla, Porsche, Mercedes, etc.), gently remind them ceramic coating is one of our most popular services for protecting paint.

If multiple things are requested, call multiple tools and combine the results into one response.

Do not promise to send confirmation emails or texts — you have no ability to send messages.
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
    last_seen = 0  # track how many messages we've already printed

    while True:
        user_input = input("> ")

        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Goodbye.")
            break

        conversation.append({"role": "user", "content": user_input})

        response = agent.invoke({"messages": conversation})

        # only print messages that are new this turn
        new_messages = response["messages"][last_seen:]
        print_agent_response({"messages": new_messages})

        conversation = response["messages"]
        last_seen = len(conversation)

if __name__ == "__main__":
    main()