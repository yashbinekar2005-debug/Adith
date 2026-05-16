# Local AI News Reporter Agent

This project runs a daily AI/tech news reporter on your Windows laptop. When the laptop is on, the agent gathers news, summarizes it with a local Ollama model, and sends the report to Telegram.

## Setup

1. Install Ollama and pull a model:

```powershell
ollama pull llama3.1
```

2. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Copy the env template and fill in your values:

```powershell
Copy-Item .env.example .env
```

Required values:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `OLLAMA_MODEL`
- `OLLAMA_BASE_URL`
- `REPORT_TIME`

4. Run manually:

```powershell
ollama serve
python main.py
```

## Telegram Commands

- `/report` - Generate or refresh today's report now
- `/last` - Send the latest saved report
- `/feedback <text>` - Save feedback for future reports
- `/status` - Show agent status
- `/help` - Show commands

## Windows Startup

After setup works manually, register startup tasks from PowerShell:

```powershell
.\scripts\register-windows-tasks.ps1
```

This creates two Windows Task Scheduler tasks:

- `AI News Agent - Ollama`
- `AI News Agent - Reporter`

Both run at login. If the laptop was off at `REPORT_TIME`, the agent sends today's report once after startup.

## Notes

- `.env`, `agent.db`, and logs are ignored by git.
- The agent only runs while your laptop is on.
- If the configured Ollama model is missing, run `ollama pull <model-name>`.
