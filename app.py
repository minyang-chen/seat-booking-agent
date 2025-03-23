# /**
#  *
#  * App UI
#  * Created by mychen76 in 2025-03.06
#  * Copyright (c) 2025. All rights reserved.
#  *
#  */
#
import chainlit as cl
import uuid
from typing import cast
from agents import Agent, Runner, ItemHelpers,ModelSettings, TResponseInputItem
from agents import set_default_openai_client,set_default_openai_api,set_tracing_disabled
from agents import (Agent,HandoffOutputItem,ItemHelpers,MessageOutputItem,Runner,ToolCallItem,ToolCallOutputItem,TResponseInputItem,function_tool,handoff,trace)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from openai import AsyncOpenAI
from flight_tools import AirlineAgentContext,faq_lookup_tool,update_seat_tool,on_seat_booking_handoff
from memory_tool import user_memory_tool
from mcp_tools import webfetch_mcp_tool, files_mcp_tool

## GLOBAL SETTINGS
BASE_URL="http://localhost:11434/v1"
MODEL_NAME="qwen2.5:14b"
API_KEY="ollama"

client = AsyncOpenAI(api_key=API_KEY,base_url=BASE_URL)
set_default_openai_client(client=client, use_for_tracing=False)
set_default_openai_api("chat_completions")
set_tracing_disabled(disabled=True)

model_settings = ModelSettings(temperature=1.5,max_tokens=256)

@cl.set_chat_profiles
async def chat_profile(current_user: cl.User):
    return [
        cl.ChatProfile(
            name="Ollama Airline Agent",
            icon="https://picsum.photos/250",
            markdown_description="Ollama Airline Agent",
            starters = [
                cl.Starter(
                    label="Greetings",
                    message="Hello! What can you help me with today?",
                ),
                cl.Starter(
                    label="Carry Bags",
                    message="how many bags I am allow to bring on the plane for flight #1113.",
                ),
                cl.Starter(
                    label="Seat Booking boarding",
                    message="I am boarding Flight #1113 with Airbus Airlines. Could you please book a seat for me?",
                ),         
                cl.Starter(
                    label="Fetch Web Content",
                    message="summarize the content of https://www.cntraveler.com/galleries/best-airlines-in-us and give me a recommend airline.",
                ),         
                cl.Starter(
                    label="Cost",
                    message="is there are any cost on checked-in 2 luggages?",
                ),                                                     
            ]            
            
        )
    ]

@cl.on_chat_start  # type: ignore
async def start_chat() -> None:        
    # Create the TaskList
    task_list = cl.TaskList(name="Agent Tasks")
    task_list.status = "Running..."
    await task_list.send()
    
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful Airline assistant"}],
    )    
    ### AGENTS
    faq_agent = Agent[AirlineAgentContext](
        name="FAQ Agent",
        handoff_description="A helpful agent that can answer questions about the airline.",
        instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
        You are an FAQ agent. If you are speaking to a customer, you probably were transferred to from the triage agent.
        Use the following routine to support the customer.
        # Routine
        1. Identify the last question asked by the customer.
        2. Use the faq lookup tool to answer the question. Do not rely on your own knowledge.
        If you cannot answer the question, transfer back to the triage agent.""",
        tools=[faq_lookup_tool],
        model=MODEL_NAME,       
        model_settings=model_settings,                     
    )

    seat_booking_agent = Agent[AirlineAgentContext](
        name="Seat Booking Agent",
        handoff_description="A helpful agent that can update a seat on a flight.",
        instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
        You are a seat booking agent. If you are speaking to a customer, you probably were transferred to from the triage agent.
        Use the following routine to support the customer.
        # Routine
        1. Ask for their confirmation number.
        2. Ask the customer what their desired seat number is.
        3. Use the update seat tool to update the seat on the flight.
        If the customer asks a question that is not related to the routine, transfer back to the triage agent. """,
        tools=[update_seat_tool],
        model=MODEL_NAME,        
        model_settings=model_settings,                                         
    )

    triage_agent = Agent[AirlineAgentContext](
        name="Triage Agent",
        handoff_description="A triage agent that can delegate a customer's request to the appropriate agent.",
        instructions=(
            f"{RECOMMENDED_PROMPT_PREFIX} "
            "You are a helpful triaging agent. You can use your tools to delegate questions to other appropriate agents."
        ),
        handoffs=[
            faq_agent,
            handoff(agent=seat_booking_agent, on_handoff=on_seat_booking_handoff),
        ],
        tools=[user_memory_tool,webfetch_mcp_tool,files_mcp_tool],
        model=MODEL_NAME, 
        model_settings=model_settings,                                                
    )

    faq_agent.handoffs.append(triage_agent)
    seat_booking_agent.handoffs.append(triage_agent)

    # Set the assistant agent in the user session.
    cl.user_session.set("prompt_history", "")  
    cl.user_session.set("faq_agent", faq_agent)  
    cl.user_session.set("seat_booking_agent", seat_booking_agent)  
    cl.user_session.set("triage_agent", triage_agent)  
    cl.user_session.set("current_agent", triage_agent)      
    cl.user_session.set("input_items", [])  
    cl.user_session.set("task_list", task_list)  

@cl.on_message  # type: ignore
async def chat(message: cl.Message) -> None:
    # Get the assistant agent from the user session.
    task_list = cast(cl.TaskList, cl.user_session.get("task_list"))     
    current_agent = cast(Agent[AirlineAgentContext], cl.user_session.get("current_agent")) 
    # inputs
    input_items = cl.user_session.get("input_items")
    if len(input_items)==0:
        input_items: list[TResponseInputItem] = []
    context = AirlineAgentContext()
    conversation_id = uuid.uuid4().hex[:16]
    
    # Construct the response message.
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})    
    # Run Agent
    input_items.append({"content": message.content, "role": "user"})    
    response = cl.Message(content="")
    
    # Update status    
    await cl.Message(content="working... please wait!").send()    
    task1 = cl.Task(title=f"{current_agent.name} call {current_agent.model}.", status=cl.TaskStatus.RUNNING)
    await task_list.add_task(task1)    
    
    result = await Runner.run(current_agent, input_items, context=context)

    task1.status = cl.TaskStatus.DONE
    await task_list.send()

    # update agent inputs
    input_items = result.to_input_list()
    cl.user_session.set("input_items", input_items)     
    current_agent = result.last_agent
    # update session    
    cl.user_session.set("message_history", message_history)
    cl.user_session.set("current_agent", current_agent)    

    task2 = cl.Task(title=f"{current_agent.name} call {current_agent.model}", status=cl.TaskStatus.RUNNING)
    await task_list.add_task(task2)        
    
    # update ui  
    for new_item in result.new_items:
        agent_name = new_item.agent.name
        if isinstance(new_item, MessageOutputItem):
            msg=f"{agent_name}: {ItemHelpers.text_message_output(new_item)}"             
        elif isinstance(new_item, HandoffOutputItem):
            msg=f"Handed off from {new_item.source_agent.name} to {new_item.target_agent.name}"
        elif isinstance(new_item, ToolCallItem):
            msg=f"{agent_name}: Calling a tool"
        elif isinstance(new_item, ToolCallOutputItem):
            msg=f"{agent_name}: Tool call output: {new_item.output}"
        else:
            msg=f"{agent_name}: Skipping item: {new_item.__class__.__name__}"    
        await cl.Message(content=msg).send()   

    task2.status = cl.TaskStatus.DONE
    await task_list.send()              

@cl.on_stop
def on_stop():
    print("The user wants to stop the task!")