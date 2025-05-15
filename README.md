# Project Setup and Agent Interaction

### 🚀 Follow the commands to run the project

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install google-adk
```

### Start the agent

```bash
adk api_server
```

### Create a session

Call the below route to create a session.
```bash
/apps/tool_agent/users/example_user/sessions/{session_id}
```

note: session_id could be anything. better pass a UUID.

#### Interact with the agent

route: 
```bash
/run_sse
```

body:
```bash
{
  "app_name": "tool_agent",
  "user_id": "example_user",
  "session_id": {session_id},
  "new_message": {
    "role": "user",
    "parts": [
      {
        "text": {text}
      }
    ]
  },
  "streaming": false
}
```
