# Experimental Seat Booking Agent
Experimental seat booking agent implementation combines OpenAI Agents SDK, Autogen extensions, and MCP tools support.

![seat-booking-workflow-graph](agentic-system-diagram.png?raw=true "seat-booking-agent-workflow")

### Use Case
The self-service airline seat reservation kiosk, also known as a flight seat booking service agent or passenger service agent, is designed to provide comprehensive customer support and assistance. This kiosk ensures a smooth and positive travel experience by handling various tasks, including reservations, through its call center interface.

### Key Features: 
- Triage agent answer user general inquiry with tools 
- Triage agent should route customer question to specialized agents
- Triage agent retrieve user preferences on seating, airlines and food   
- Triage agent use agents as tools on question routing  
- Triage agent use MCP server as tools to perform web fetch content and read files system   
- QA agent has knownledge to handling questions about Plane, Flight and Onboarding 
- Seat booking agent specifilized on plane seat reservation tasks
- Web Chat interface for user self-service

### Lab Technical Stack
- Linux 
- OpenAI Agents SDK
- Autogen 0.4 + extensions (MCP Tools,OpenAI, Ollama)
- Chainlit (UI)
- Ollama (local Qwen2,5)

### Environment 
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
### Running
```
chainlit run app.py
```


