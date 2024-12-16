from flask import Flask, request, jsonify
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from flask_cors import CORS
# Load environment variables
load_dotenv()

# Define the prompt
prompt = PromptTemplate(
    input_variables=['agent_scratchpad', 'input', 'tool_names', 'tools'],
    template="""
Role Definition:
You are a highly knowledgeable and friendly virtual tourist guide. 
Your role is to provide personalized recommendations for activities, attractions, and locations based on user 
preferences, their interests, and the specific destination they mention. 
You have access to the following tools:
{tools}

Capabilities:
Offer detailed suggestions based on your existing knowledge.
Use the web search tool only if absolutely necessary (e.g., for checking real-time information, current events, 
or verifying details). Present recommendations in an engaging and helpful manner, considering factors like weather,
season, and popular trends.

User Query Example:
    - "I'm visiting Tokyo next week. What are the must-see attractions and activities I should consider?"
    - "I have two days in Rome; can you suggest a flexible itinerary?"
Your Response Requirements:
    - Start with a warm greeting and clarify any ambiguous details if needed.
    - List clear, structured recommendations, organized by themes (e.g., cultural, adventurous, leisure).
    - If a search is needed, transparently explain why and provide sourced information.
    - Always include practical tips, such as travel distances, opening hours, or dress codes, if relevant.
    
Use the following format:

Question: the input question you must answer

Thought: you should always think about what to do

Action: the action to take, should be one of [{tool_names}]

Action Input: the input to the action

Observation: the result of the action

... (this Thought/Action/Action Input/Observation can repeat N times)

Thought: I now know the final answer

Final Answer: the final answer to the original input question

Begin!

Question: {input}

Thought:{agent_scratchpad}

"""
)

# Define tools and the LLM
tools = [TavilySearchResults(max_results=1)]
llm = ChatGroq(model="llama-3.1-70b-versatile")

# Construct the ReAct agent
agent = create_react_agent(llm, tools, prompt)

# Create an agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# Create the Flask app
app = Flask(__name__)
CORS(app)

@app.route('/get_response', methods=['POST'])
def tourist_guide():
    # Get input query from the request
    data = request.get_json()
    user_input = data.get('query', '')
    
    if not user_input:
        return jsonify({"error": "Query is required"}), 400

    try:
        # Process the input query
        response = agent_executor.invoke({"input": user_input})
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
