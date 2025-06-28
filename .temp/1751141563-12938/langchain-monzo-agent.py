import asyncio
import os
import json
import logging
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from dotenv import load_dotenv
from anyio import ClosedResourceError
import urllib.parse
from langchain_ollama import ChatOllama
import requests
from datetime import datetime
import traceback

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(override=True)

base_url = os.getenv("CORAL_SSE_URL")
agentID = os.getenv("CORAL_AGENT_ID")

params = {
    #"waitForAgents": 1,
    "agentId": agentID,
    "agentDescription": """An agent responsible for answering banking-related questions based on the user's Monzo account. 
    You must only use the provided tools to fulfill user requests."""
}
query_string = urllib.parse.urlencode(params)
MCP_SERVER_URL = f"{base_url}?{query_string}"

def get_tools_description(tools):
    return "\n".join(f"Tool: {t.name}, Schema: {json.dumps(t.args).replace('{', '{{').replace('}', '}}')}" for t in tools)
    
@tool
def get_monzo_balance() -> dict:
    """
    Call Monzo /balance endpoint and return all fields, formatting numeric
    values (like balance and spend_today) as decimal strings in GBP (e.g., "129.69").
    """
    token = os.getenv("MONZO_ACCESS_TOKEN")
    acc_id = os.getenv("MONZO_ACCOUNT_ID")
    if not token or not acc_id:
        raise RuntimeError("Please set MONZO_ACCESS_TOKEN and MONZO_ACCOUNT_ID in environment")

    resp = requests.get(
        "https://api.monzo.com/balance",
        headers={"Authorization": f"Bearer {token}"},
        params={"account_id": acc_id}
    )
    resp.raise_for_status()
    data = resp.json()

    def fmt(val):
        return f"{val / 100:.2f}" if isinstance(val, int) else val

    return {
        "balance": fmt(data.get("balance")),
        "total_balance": fmt(data.get("total_balance")),
        "balance_including_flexible_savings": fmt(data.get("balance_including_flexible_savings")),
        "currency": data.get("currency"),
        "spend_today": fmt(data.get("spend_today")),
        "local_currency": data.get("local_currency"),
        "local_exchange_rate": data.get("local_exchange_rate"),
        "local_spend": data.get("local_spend"),
    }

@tool
def get_monzo_transaction(months: int = 1) -> list:
    """
    Retrieve Monzo transactions from the past N months.

    Reads credentials from environment variables:
        MONZO_ACCESS_TOKEN — Monzo API access token
        MONZO_ACCOUNT_ID   — Monzo account identifier

    Args:
        months (int): Number of months in the past to include (e.g., 2 means past two months).

    Returns:
        List[dict]: Each dict contains:
            - time (str): ISO8601 timestamp of the transaction
            - amount (float): Transaction amount in GBP
            - counterparty (str): Merchant name or description
            - category (str): Transaction category

    Raises:
        RuntimeError: If environment variables are not set.
        HTTPError: If any HTTP request fails.
    """
    access_token = os.getenv("MONZO_ACCESS_TOKEN")
    account_id = os.getenv("MONZO_ACCOUNT_ID")
    if not access_token or not account_id:
        raise RuntimeError("Environment variables MONZO_ACCESS_TOKEN and MONZO_ACCOUNT_ID must be set")

    def add_months(dt: datetime, months: int) -> datetime:
        """
        Adjust a datetime by a given number of months without external dependencies.
        Handles month overflow and selects the last valid day if needed.
        """
        y, m = dt.year, dt.month + months
        y += (m - 1) // 12
        m = (m - 1) % 12 + 1
        # days in each month, accounting for leap years
        max_day = [31,
                   29 if (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0) else 28,
                   31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
        return dt.replace(year=y, month=m, day=min(dt.day, max_day))

    now = datetime.utcnow()
    start_dt = add_months(now, -months)
    since_ts = start_dt.isoformat() + "Z"
    before_ts = now.isoformat() + "Z"

    url = "https://api.monzo.com/transactions"
    headers = {"Authorization": f"Bearer {access_token}"}
    results = []

    while True:
        resp = requests.get(url, headers=headers, params={
            "account_id": account_id,
            "expand[]": "merchant",
            "limit": 100,
            "since": since_ts,
            "before": before_ts
        })
        resp.raise_for_status()
        transactions = resp.json().get("transactions", [])
        if not transactions:
            break

        for tx in transactions:
            cp = (tx.get("merchant") or {}).get("name") or tx.get("description", "N/A")
            results.append({
                "time": tx.get("created"),
                "amount": tx.get("amount", 0) / 100.0,
                "counterparty": cp,
                "category": tx.get("category", "unknown")
            })

        oldest = min(tx["created"] for tx in transactions)
        if oldest <= since_ts:
            break
        before_ts = oldest

    return results

async def create_monzo_agent(client, tools):
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are `monzo_agent`, responsible for answering banking-related questions based on the user's Monzo account. You must only use the provided tools to fulfill user requests. Follow this workflow strictly:
         

        0. Call `user-input` to create a box and request query from user.
        1. Take 2 seconds to think about the content (instruction) of the message and check the available tools.
        2. Read the user's message and extract what they want:
        - If the user is asking about balance (e.g. current funds, spending today), call `get_monzo_balance()`.
        - If they are asking about transactions (e.g. what they spent, where they spent, how much they spent recently), call `get_monzo_transaction(...)` and extract the correct number of months (default to 1).
        - If the question involves both (e.g. "Why is my balance low?", "How did I spend so much?"), call both tools and answer based on the combined results.
        3. Once tool(s) return, generate a clear, direct reply that answers the user’s question using real data.
        4. If tool response is empty, or there's an error, reply with `"error"` or a helpful fallback message.
        5. Take 3 seconds and think about the content to ensure you have executed the instruction to the best of your ability and the tools. Make this your response as "answer".
        6. Always respond back to the user by calling `user-input` even if you have no answer or error.
        7. Wait for 2 seconds and repeat the process from step 0.

        
        Tools: {get_tools_description(tools)}"""),
        ("placeholder", "{history}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    model = init_chat_model(
        model=os.getenv("MODEL"),
        model_provider=os.getenv("LLM_MODEL_PROVIDER"),
        api_key=os.getenv("API_KEY"),
        temperature=0.3,
        max_tokens=32768
    )

    agent = create_tool_calling_agent(model, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

async def main():
    CORAL_SERVER_URL = f"{base_url}?{query_string}"
    logger.info(f"Connecting to Coral Server: {CORAL_SERVER_URL}")

    client = MultiServerMCPClient(
        connections={
            "coral": {
                "transport": "sse",
                "url": CORAL_SERVER_URL,
                "timeout": 600,
                "sse_read_timeout": 600,
            }
        }
    )
    logger.info("Coral Server Connection Established")

    tools = await client.get_tools()
    coral_tool_names = [
        "list_agents",
        "create_thread",
        "add_participant",
        "remove_participant",
        "close_thread",
        "send_message",
        "wait_for_mentions",
    ]
    tools = [tool for tool in tools if tool.name in coral_tool_names]
    tools += [get_monzo_balance,get_monzo_transaction]

    logger.info(f"Tools Description:\n{get_tools_description(tools)}")

    agent_executor = await create_monzo_agent(client, tools)

    while True:
        try:
            logger.info("Starting new agent invocation")
            await agent_executor.ainvoke({"agent_scratchpad": []})
            logger.info("Completed agent invocation, restarting loop")
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error in agent loop: {str(e)}")
            logger.error(traceback.format_exc())
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
