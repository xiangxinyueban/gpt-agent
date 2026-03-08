# GPT Web Automation Agent

An AI agent for automating web interactions, starting with ChatGPT as a proof-of-concept for tax/invoice processing systems.

## Features

- **Automated Login**: Automatically logs into ChatGPT using provided credentials
- **Message Sending**: Sends predefined or custom messages to ChatGPT
- **Response Capture**: Retrieves and parses ChatGPT responses
- **Screenshot Capture**: Takes screenshots at each step for debugging
- **Configurable**: Easy configuration via environment variables
- **Extensible Architecture**: Designed to be extended to other web automation tasks

## Architecture

This project serves as a POC for web automation in tax/invoice processing systems. The architecture can be extended to:

1. **Invoice Portal Automation**: Login to tax portals, download invoices
2. **Data Extraction**: Extract structured data from web pages
3. **Form Submission**: Automate form submissions for tax filing
4. **Multi-step Workflows**: Complex multi-page workflows

## Prerequisites

- Python 3.8+
- Git
- Chrome/Firefox/WebKit browser (for Playwright)

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/xiangxinyueban/gpt-agent.git
cd gpt-agent
```

### 2. Create virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Playwright browsers
```bash
playwright install chromium  # or firefox, webkit
```

### 5. Configure environment
```bash
cp .env.example .env
# Edit .env with your ChatGPT credentials
```

## Configuration

Edit the `.env` file with your settings:

```env
# ChatGPT Credentials (required)
CHATGPT_USERNAME=your_email@example.com
CHATGPT_PASSWORD=your_password

# Browser Configuration
BROWSER_TYPE=chromium  # chromium, firefox, webkit
HEADLESS=false  # Set to true for headless mode

# GPT Interaction
DEFAULT_MESSAGE=你好gpt
WAIT_FOR_RESPONSE_SEC=10
```

## Usage

### Basic Usage
```bash
python gpt_agent.py
```

### CLI Options
```bash
# Install as package
pip install -e .

# Run as command
gpt-agent
```

### Programmatic Usage
```python
import asyncio
from gpt_agent import GPTAgent

async def main():
    async with GPTAgent() as agent:
        results = await agent.run_automation()
        print(f"Response: {results['response']}")

asyncio.run(main())
```

## Project Structure

```
gpt-agent/
├── gpt_agent.py          # Main automation agent
├── config.py             # Configuration management
├── requirements.txt      # Production dependencies
├── requirements-dev.txt  # Development dependencies
├── setup.py             # Package configuration
├── .env.example         # Environment template
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── screenshots/         # Screenshots directory (auto-created)
```

## How It Works

1. **Initialization**: Launches browser using Playwright
2. **Login**: Navigates to ChatGPT, enters credentials, submits form
3. **Message Handling**: Finds chat input, sends message, waits for response
4. **Response Extraction**: Parses response from chat interface
5. **Cleanup**: Closes browser and saves results

## Screenshots

The agent automatically takes screenshots at key steps:
- `login_page.png` - Initial login page
- `login_form.png` - Login form with credentials entered
- `logged_in.png` - Successfully logged in
- `message_entered.png` - Message typed but not sent
- `response_received.png` - Response from ChatGPT

## Extending for Tax/Invoice Automation

This POC can be extended for tax/invoice processing:

### Example: Tax Portal Automation
```python
class TaxPortalAgent(GPTAgent):
    async def login_to_tax_portal(self):
        await self.page.goto("https://tax-portal.example.com")
        await self.page.fill("#username", self.config.tax_username)
        await self.page.fill("#password", self.config.tax_password)
        await self.page.click("#login-button")
    
    async def download_invoices(self, date_range):
        # Navigate to invoice section
        # Filter by date
        # Download PDFs
        pass
```

### Example: Invoice Data Extraction
```python
async def extract_invoice_data(self, invoice_html):
    # Use BeautifulSoup to parse invoice HTML
    # Extract: invoice number, date, amount, tax amount
    # Return structured data
    pass
```

## Development

### Setup Development Environment
```bash
pip install -r requirements-dev.txt
pre-commit install
```

### Running Tests
```bash
pytest tests/ -v
```

### Code Formatting
```bash
black gpt_agent.py config.py
flake8 gpt_agent.py config.py
mypy gpt_agent.py config.py
```

## MCP Server Integration (Future)

This agent can be exposed as an MCP (Model Context Protocol) server:

```python
# mcp_server.py
from mcp.server import Server
from gpt_agent import GPTAgent

server = Server("gpt-agent")

@server.tool()
async def chat_with_gpt(message: str) -> str:
    async with GPTAgent() as agent:
        await agent.login_to_chatgpt()
        return await agent.send_message(message)
```

## Troubleshooting

### Common Issues

1. **Login fails**: Check credentials and ensure account is active
2. **Element not found**: ChatGPT may have updated their UI - update selectors
3. **Timeout errors**: Increase `TIMEOUT_MS` in .env file
4. **Browser issues**: Reinstall Playwright browsers: `playwright install`

### Debug Mode
Set `HEADLESS=false` and `LOG_LEVEL=DEBUG` in `.env` to see detailed logs.

## Security Notes

- Never commit `.env` file with credentials
- Use environment variables in production
- Consider using password managers for credential storage
- This is a POC - production use requires additional security measures

## License

MIT

## Contributing

This is part of a larger tax/invoice processing system. Contact the author for collaboration opportunities.