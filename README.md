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

### Todos
- save seat history at the end of the booking
- improve FAQ agent to use RAG on actual documents
- improve memory storage
- add MCP tools to invoke actual booking service api 
- more to came...

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

**Important**: Please keep your pull requests small and focused.  This will make it easier to review and merge.

## Feature Requests
If you have a feature request, please open an [issue](https://github.com/minyang-chen/seat-booking-agent/issues) and make sure it is tagged with `enhancement`.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

