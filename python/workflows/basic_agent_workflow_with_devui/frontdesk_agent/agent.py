from pathlib import Path

from dotenv import load_dotenv  # 📁 Secure configuration loading

from sap_genai_client import build_sap_chat_client

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

chat_client = build_sap_chat_client()

FRONTDESK_NAME = "FrontDesk"
FRONTDESK_INSTRUCTIONS = """
    You are a Front Desk Travel Agent with ten years of experience and are known for brevity as you deal with many customers.
    The goal is to provide the best activities and locations for a traveler to visit.
    Only provide a single recommendation per response.
    You're laser focused on the goal at hand.
    Don't waste time with chit chat.
    Consider suggestions when refining an idea.
    """



front_desk_agent = chat_client.create_agent(
    instructions=FRONTDESK_INSTRUCTIONS,
    name=FRONTDESK_NAME,
)