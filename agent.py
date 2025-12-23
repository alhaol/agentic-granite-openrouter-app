import os
import re
from dotenv import load_dotenv
from typing import Annotated, TypedDict, Union, List

# Core imports
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

load_dotenv()

# --- 1. Define Tools ---
def get_word_length(word: str) -> str:
    """Returns the length of a word."""
    # Stripping quotes in case the model adds them (e.g., "word")
    clean_word = word.strip('"\'')
    return str(len(clean_word))

# Map tool names to functions
TOOL_MAP = {
    "WordLength": get_word_length
}

# --- 2. Define the ReAct Prompt ---
# Since the model doesn't support native tools, we teach it the format via this prompt.
REACT_SYSTEM_PROMPT = """Answer the following questions as best you can. You have access to the following tools:

WordLength: Useful for when you need to count the characters in a specific word. Input should be a single word.

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [WordLength]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!
"""

# --- 3. Define Graph State ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

# --- 4. Node: The Reasoner (The Model) ---
def run_model(state: AgentState):
    messages = state["messages"]
    
    # Setup the model
    llm = ChatOpenAI(
        model=os.getenv("MODEL_NAME", "ibm-granite/granite-4.0-h-micro"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "http://localhost:7777",
            "X-Title": "Granite Streamlit Agent",
        },
        temperature=0.01 # Extremely low temperature for strict formatting
    )

    # If this is the first turn, prepend the system prompt instructions
    if len(messages) == 1 and isinstance(messages[0], HumanMessage):
        # We wrap the user query with the ReAct prompt structure
        user_input = messages[0].content
        prompt_content = f"{REACT_SYSTEM_PROMPT}\nQuestion: {user_input}"
        # Replace the first message with the formatted prompt
        messages = [HumanMessage(content=prompt_content)]
    
    response = llm.invoke(messages)
    return {"messages": [response]}

# --- 5. Node: The Tool Executor ---
def run_tool(state: AgentState):
    last_message = state["messages"][-1]
    content = last_message.content
    
    # Regex to find "Action:" and "Action Input:"
    # We look for the last occurrence to handle potential chain-of-thought blocks
    action_match = re.search(r"Action:\s*(.*?)\n", content, re.IGNORECASE)
    input_match = re.search(r"Action Input:\s*(.*)", content, re.IGNORECASE)
    
    if action_match and input_match:
        action_name = action_match.group(1).strip()
        action_input = input_match.group(1).strip()
        
        # Execute Tool
        if action_name in TOOL_MAP:
            print(f"🛠️ Executing {action_name} with input: {action_input}")
            result = TOOL_MAP[action_name](action_input)
            observation = f"Observation: {result}"
        else:
            observation = f"Observation: Error: Tool '{action_name}' not found."
            
        return {"messages": [HumanMessage(content=observation)]}
    
    # Fallback if parsing fails but loop triggered (should generally not happen due to edge logic)
    return {"messages": [HumanMessage(content="Observation: Could not parse Action/Action Input. Please try again.")]}

# --- 6. Edge Logic ---
def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    content = last_message.content
    
    # If the model says "Final Answer:", we are done.
    if "Final Answer:" in content:
        return "end"
    # If the model produced an "Action:", we need to run a tool.
    elif "Action:" in content:
        return "continue"
    # If it didn't follow format, we might assume it's done or stuck. 
    # For this simple agent, we'll end to prevent loops.
    else:
        return "end"

# --- 7. Build the Graph ---
def get_agent_executor():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", run_model)
    workflow.add_node("action", run_tool)
    
    workflow.set_entry_point("agent")
    
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "action",
            "end": END
        }
    )
    
    workflow.add_edge("action", "agent")
    
    app = workflow.compile()
    return app