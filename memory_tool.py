# /**
#  *
#  * Memory Tools
#  * Created by mychen76 in 2025-03.06
#  * Copyright (c) 2025. All rights reserved.
#  *
#  */
#

import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_core.memory import ListMemory, MemoryContent
from autogen_core.models import ModelFamily
from autogen_ext.models.openai import OpenAIChatCompletionClient
from typing import Any
from agents import function_tool

model_client = OpenAIChatCompletionClient(
    model="qwen2.5:14b",
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": False,
        "family": ModelFamily.ANY,
    },
    # temperature=1.5,
    # max_tokens=256
)

_user_preference=None
_past_experience=None

async def _load_prefrences():
    """
    retrieve user default preference and past experience
    """
    global _user_preference
    global _past_experience    
    
    # Create a list-based memory with some initial content.
    _user_preference = ListMemory("user_preference")
    user_preferences = """ 
    Food Preferences:
    - User likes pizza.
    - User dislikes cheese.
    - User dislikes spicy pepper.
    - food prefrence types: [window, vegetarian or vegan]
    - food allergies: ["peanuts", "shellfish"]

    Seat Preferences:
    - preferred seat types are window, aisle and emergency exit.
    - seat_preferences: ["first_class", "business_class", "economy_class"]
    
    Airline Preferences:
    - preferred airline: "Air Canada"
    - allowed airlines: ["Air Canada", "Qantas", "Delta"]

    Flight Time Preferences:
    - preferred departure time: "08:00 AM"
    - preferred arrival time: "05:00 PM"
    """    
    await _user_preference.add(
        MemoryContent(
            content=user_preferences,
            mime_type="text/markdown",
            metadata={"category": "preferences", "type": "units"},
        )
    )    
    print(_user_preference.content)

    _past_experience = ListMemory("past_experience")
    user_past_experience = """ 
    Recent Flight experiences:
    - Air Canada morning flight from toronto to new york(2025-03-07)
        - Rating: 4/5
        - Liked: window seat, pizza
        - Disliked: tight seat        
        
    - American Airline night flight from new york to toronto(2025-03-08)
        - Rating: 4/5
        - Liked: window seat, coffee
        - Disliked: smaller seat size        
        """
    
    await _past_experience.add(
        MemoryContent(
            content=user_past_experience,
            mime_type="text/markdown",
            metadata={"category": "preferences", "type": "units"},
        )
    )
    print(_past_experience.content)
    return _user_preference, _past_experience

## preload preferences
asyncio.run(_load_prefrences())

## Create an AssistantAgent instance with the model client and memory.
_memory_agent = AssistantAgent(
        name="memory_assistant",
        model_client=model_client,
        memory=[_user_preference, _past_experience],
        system_message="You are a helpful preference and memory assistant.",
        reflect_on_tool_use=True,
    )

### TOOLS
@function_tool(name_override="user_memory_tool", description_override="Lookup user preferences about flight, airline, flight time, foods and past experience")
async def user_memory_tool(query:str) -> str:
    # Create an AssistantAgent instance with the model client and memory.
    response = await _memory_agent.on_messages(
        [TextMessage(content=query, source="user")], CancellationToken()
    )
    #print(response.chat_message.content)  
    return response.chat_message.content

if __name__ == "__main__":    
    print("==="*10)    
    query="What food I dislike?"
    response = asyncio.run(user_memory_tool(query))
    print(response)
    print("==="*10)
    query="What food I am allergic to?"
    response = asyncio.run(user_memory_tool(query))
    print(response)
