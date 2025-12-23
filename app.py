import streamlit as st
from agent import get_agent_executor
from langchain_core.messages import HumanMessage

st.set_page_config(page_title="Granite Agent", page_icon="🤖")

st.title("🤖 Granite ReAct Agent")
st.caption("Powered by IBM Granite 4.0 (Text-Only ReAct)")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I can count letters in words. Try me!"}]

# Display history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Input loop
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.write("Thinking...")
        
        try:
            agent = get_agent_executor()
            inputs = {"messages": [HumanMessage(content=prompt)]}
            
            # Run the graph
            response = agent.invoke(inputs)
            last_msg = response["messages"][-1].content
            
            # Extract just the Final Answer if possible for a cleaner look
            if "Final Answer:" in last_msg:
                final_answer = last_msg.split("Final Answer:")[-1].strip()
            else:
                final_answer = last_msg
                
            placeholder.write(final_answer)
            st.session_state.messages.append({"role": "assistant", "content": final_answer})
            
        except Exception as e:
            placeholder.error(f"Error: {e}")