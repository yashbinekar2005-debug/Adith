# Local AI News Reporter Agent

This project runs a daily AI/tech news reporter on your Windows laptop. When the laptop is on, the agent gathers news, summarizes it with a local Ollama model, and sends the report to Telegram.

Current startup workflow:

```text
Laptop opens
Ollama starts
Agent starts in the background
Report is generated and sent if today's report is not already sent
Ollama stops automatically to free RAM
Telegram bot stays available for commands
```

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

Useful optional values:

- `STOP_OLLAMA_AFTER_REPORT=true` - stop Ollama after reports to save RAM
- `OLLAMA_STARTUP_WAIT_SECONDS=45` - wait time for Ollama to become ready
- `TELEGRAM_SEND_RETRIES=6` - how many times to retry Telegram sending
- `TELEGRAM_RETRY_DELAY_SECONDS=60` - seconds to wait between Telegram retries

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

After setup works manually, install automatic startup from PowerShell:

```powershell
.\scripts\install-startup-folder.ps1
```

This creates a startup launcher here:

- `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\AI News Agent.cmd`

It runs at login, starts Ollama, then starts the reporter in the background. If today's report has not been sent yet, the agent sends it once after startup. After the report is sent, the agent stops Ollama automatically to free RAM.

If Telegram is not reachable immediately after laptop startup, the sender retries using:

- `TELEGRAM_SEND_RETRIES`
- `TELEGRAM_RETRY_DELAY_SECONDS`

If your Windows account allows Task Scheduler registration, you can also use:

```powershell
.\scripts\register-windows-tasks.ps1
```

## Notes

- `.env`, `agent.db`, and logs are ignored by git.
- The agent only runs while your laptop is on.
- If the configured Ollama model is missing, run `ollama pull <model-name>`.
- If no Telegram report arrives, check `logs/agent.log` first. DNS or Wi-Fi startup delays usually show as `api.telegram.org` connection errors.
