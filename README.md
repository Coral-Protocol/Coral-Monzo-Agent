## [Monzo Agent](https://github.com/Coral-Protocol/Coral-Monzo-Agent)

The Monzo Agent allows you to securely access and analyze your Monzo banking data using a local LLM/LLM provided by Groq, ensuring privacy and security. By integrating with Monzo’s official API and custom toolkits, the agent enables natural language interactions to check your account balance, view transaction history, and receive personalized financial advice—all without exposing your sensitive information to external servers.

## Responsibility

The Monzo Agent enables privacy-preserving, conversational access to your Monzo account data. Users can check their balance, review recent transactions, and obtain personal finance insights—all powered by a local LLM/LLM provided by Groq that processes data securely on your own device.


## Details
- **Framework**: LangChain
- **Tools used**: Customized Monzo Tools, Coral MCP Tools
- **AI model**: Qwen3 via Ollama
- **Date added**: 20/06/25
- **License**: MIT

## Setup the Agent

### 1. Clone & Install Dependencies

<details>  

```bash
# In a new terminal clone the repository:
git clone https://github.com/Coral-Protocol/Coral-Monzo-Agent.git

# Navigate to the project directory:
cd Coral-Monzo-Agent

# Download and run the UV installer, setting the installation directory to the current one
curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=$(pwd) sh

# Create a virtual environment named `.venv` using UV
uv venv .venv

# Activate the virtual environment
source .venv/bin/activate

# install uv
pip install uv

# Install dependencies from `pyproject.toml` using `uv`:
uv sync
```

</details>

### 2. Configure Environment Variables

Get the API Key:
[OpenAI](https://platform.openai.com/api-keys) or [GROQ](https://console.groq.com/keys) 

`MONZO_ACCESS_TOKEN` and `MONZO_ACCOUNT_ID`:
[Monzo Developer Portal](https://developers.monzo.com/)

<details>

Create a .env file in the project root:
```bash
cp -r env_sample .env
```

Add your `API_KEY`, `MONZO_ACCESS_TOKEN`, and `MONZO_ACCOUNT_ID` and any other required environment variables to the .env file.

</details>

## Run the Agent

You can run in either of the below modes to get your system running.  

- The Executable Model is part of the Coral Protocol Orchestrator which works with [Coral Studio UI](https://github.com/Coral-Protocol/coral-studio).  
- The Dev Mode allows the Coral Server and all agents to be seaprately running on each terminal without UI support.  

### 1. Executable Mode

Checkout: [How to Build a Multi-Agent System with Awesome Open Source Agents using Coral Protocol](https://github.com/Coral-Protocol/existing-agent-sessions-tutorial-private-temp) and update the file: `coral-server/src/main/resources/application.yaml` with the details below, then run the [Coral Server](https://github.com/Coral-Protocol/coral-server) and [Coral Studio UI](https://github.com/Coral-Protocol/coral-studio). You do not need to set up the `.env` in the project directory for running in this mode; it will be captured through the variables below.

<details>

For Linux or MAC:

```bash
# PROJECT_DIR="/PATH/TO/YOUR/PROJECT"

applications:
  - id: "app"
    name: "Default Application"
    description: "Default application for testing"
    privacyKeys:
      - "default-key"
      - "public"
      - "priv"

registry:
  monzo:
    options:
      - name: "API_KEY"
        type: "string"
        description: "API key for the service"
      - name: "MONZO_ACCESS_TOKEN"
        type: "string"
        description: "MONZO_ACCESS_TOKEN"
      - name: "MONZO_ACCOUNT_ID"
        type: "string"
        description: "MONZO_ACCOUNT_ID"
    runtime:
      type: "executable"
      command: ["bash", "-c", "/home/xinxing/coral/coral-orchestrator/Coral-Monzo-Agent/run_agent.sh main.py"]
      
      environment:
        - name: "API_KEY"
          from: "API_KEY"
        - name: "MODEL"
          value: "llama-3.3-70b-versatile"
        - name: "LLM_MODEL_PROVIDER"
          value: "groq"
        - name: "MONZO_ACCESS_TOKEN"
          from: "MONZO_ACCESS_TOKEN"
        - name: "MONZO_ACCOUNT_ID"
          from: "MONZO_ACCOUNT_ID"

```

For Windows, create a powershell command (run_agent.ps1) and run:

```bash
command: ["powershell","-ExecutionPolicy", "Bypass", "-File", "${PROJECT_DIR}/run_agent.ps1","main.py"]
```

</details>

### 2. Dev Mode

Ensure that the [Coral Server](https://github.com/Coral-Protocol/coral-server) and [Interface Agent](https://github.com/Coral-Protocol/Coral-Interface-Agent/tree/main) is running on your system and run below command in a separate terminal.

<details>

```bash
# Run the agent using `uv`:
uv run python main.py
```
</details>

## Example
<details>

```bash
# Input:
Question: Help me check my transections of monzo for the last 2 months and give me some personal finance advice.

# Output:
Answer: Here is a summary of your Monzo transactions for the past 2 months:
- May 1: -£22.00 (University, bills)
- May 14: -£120.00 (Person A, general)
- May 14: -£20.81 (Mobile Provider, bills)
- May 18: -£16.00 (Person A, general)
- May 19: +£9.00 (Person B, income)
- June 2: -£22.00 (University, bills)
- June 6: +£6.66 (From Person C, income)
- June 12: -£20.81 (Mobile Provider, bills)
- June 17: +£100.00 (From Person C, income)

Notable spending patterns:
- Regular bills to University and Mobile Provider.
- Significant general spending to "Person A."
- Income from Person B and Person C.

Personalized financial advice:
1. **Track Recurring Bills:** Your regular payments to University and Mobile Provider are predictable. Consider setting up automated budgeting for these to ensure you always have funds allocated.
2. **Review Large Expenses:** The £120 payment to "Person A" stands out. Review such large transactions to ensure they are necessary and look for ways to reduce or avoid them if possible.
3. **Increase Savings:** Try to set aside a portion of your income (even small amounts) right after you receive it. Automating savings can help build a financial cushion.
4. **Monitor Cash Flow:** Your income is irregular. Consider ways to stabilize your income or reduce discretionary spending during lower-income months.
5. **Analyze General Spending:** Categorize your general expenses to identify areas where you can cut back.

Would you like more detailed budgeting tips or help setting up a savings plan?

Is there anything else I can help you with?
```
</details>

## Creator Details
- **Name**: Xinxing
- **Affiliation**: Coral Protocol
- **Contact**: [Discord](https://discord.com/invite/Xjm892dtt3)

