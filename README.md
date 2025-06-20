## [Monzo Agent](https://github.com/Coral-Protocol/Coral-Monzo-Agent)

The Monzo Agent allows you to securely access and analyze your Monzo banking data using a local LLM, ensuring privacy and security. By integrating with Monzo’s official API and custom toolkits, the agent enables natural language interactions to check your account balance, view transaction history, and receive personalized financial advice—all without exposing your sensitive information to external servers.

## Responsibility

The Monzo Agent enables privacy-preserving, conversational access to your Monzo account data. Users can check their balance, review recent transactions, and obtain personal finance insights—all powered by a local LLM that processes data securely on your own device.


## Details
- **Framework**: LangChain
- **Tools used**: Customized Monzo Tools, Coral MCP Tools
- **AI model**: Qwen3 via Ollama
- **Date added**: 20/06/25
- **License**: MIT

## Use the Agent

### 1. Install and Run Ollama (for Local LLM)
<details>

Monzo Agent uses Ollama to run local LLM. Please make sure you have Ollama installed and the desired model downloaded before running the agent.

**Step 1: Install Ollama**

- **Linux/macOS:**
  Follow the official instructions: [https://ollama.com/download](https://ollama.com/download)
  Or run:
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```
- **Windows:**
  Download the installer from [Ollama's website](https://ollama.com/download).

**Step 2: Download Local model**

```bash
ollama pull qwen3:latest
```

**Step 3: Start Ollama Service**

Ollama usually starts automatically. If not, start it manually:
```bash
ollama serve
```

**Step 4: Verify the model is running**

```bash
ollama list
```
Make sure no errors occur and Ollama is running at `http://localhost:11434`.

</details>

### 2. Clone & Install Dependencies

<details>  

Ensure that the [Coral Server](https://github.com/Coral-Protocol/coral-server) is running on your system and the [Interface Agent](https://github.com/Coral-Protocol/Coral-Interface-Agent) is running on the Coral Server.  

```bash
# Clone the Monzo Agent repository
git clone https://github.com/Coral-Protocol/Coral-Monzo-Agent.git

# Navigate to the project directory
cd Coral-Monzo-Agent

# Install `uv`:
pip install uv

# Install dependencies from `pyproject.toml` using `uv`:
uv sync
```
This command will read the `pyproject.toml` file and install all specified dependencies in a virtual environment managed by `uv`.

</details>

### 3. Configure Environment Variables
<details>

Get the `MONZO_ACCESS_TOKEN` and `MONZO_ACCOUNT_ID`:
[Monzo Developer Portal](https://developers.monzo.com/)

Create a .env file in the project root:
```bash
cp -r env_sample .env
```

Add your `MONZO_ACCESS_TOKEN` and `MONZO_ACCOUNT_ID` and any other required environment variables to the .env file.

</details>

### 4. Run Agent
<details>

Run the agent using `uv`:
```bash
uv run langchain-monzo-agent.py
```
</details>

### 5. Example
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

## Creator Details
- **Name**: Xinxing
- **Affiliation**: Coral Protocol
- **Contact**: [Discord](https://discord.com/invite/Xjm892dtt3)

