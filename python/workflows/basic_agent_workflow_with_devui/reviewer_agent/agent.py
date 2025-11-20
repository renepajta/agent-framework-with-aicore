from pathlib import Path

from dotenv import load_dotenv  # 📁 Secure configuration loading

from sap_genai_client import build_sap_chat_client

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

chat_client = build_sap_chat_client()

REVIEWER_NAME = "Concierge"
REVIEWER_INSTRUCTIONS = """
    You are an are hotel concierge who has opinions about providing the most local and authentic experiences for travelers.
    The goal is to determine if the front desk travel agent has recommended the best non-touristy experience for a traveler.
    If so, state that it is approved.
    If not, provide insight on how to refine the recommendation without using a specific example. 
    """



reviewer_agent = chat_client.create_agent(
    instructions=REVIEWER_INSTRUCTIONS,
    name=REVIEWER_NAME,
)