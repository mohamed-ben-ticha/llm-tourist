import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import requests
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu

# Load the data
@st.cache_data
def load_data():
    # Replace with the path to your dataset
    data = pd.read_csv("data/tourists_flows_per_country.csv")  
    return data

def main():
    selected = option_menu(menu_title=None, 
                           options=["Tourists Flow", "LLM-Assistant"], 
                           icons=["globe-europe-africa", "robot"],
                           orientation="horizontal", default_index=0)
    
    if selected=="Tourists Flow":
        st.title("Tourist Flow Visualization")
        # Load data
        data = load_data()

        # Load GeoJSON from manually downloaded file
        world = gpd.read_file("data/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp")  # Replace with the correct path

        # Merge dataset with GeoJSON
        world = world.merge(data, how='left', left_on='NAME', right_on='Country')

        # Create the map
        m = folium.Map(location=[30, 30], zoom_start=3, tiles="cartodbpositron")  # Adjust zoom level and tile style if needed

        # Add choropleth layer
        choropleth = folium.Choropleth(
            geo_data=world,
            name="choropleth",
            data=world,
            columns=["NAME", "Visitors"],
            key_on="feature.properties.NAME",
            fill_color="YlGnBu",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Number of Visitors",
            control=False  # Disabling default legend
        )
        choropleth.add_to(m)

        # Add tooltips
        folium.GeoJsonTooltip(
            fields=["NAME", "Visitors"],
            aliases=["Country", "Number of Visitors"],
            localize=True,
        ).add_to(choropleth.geojson)

        # Display map with larger size
        st_folium(m, width=800, height=650) 

    elif selected=="LLM-Assistant":
        # Initialize chat history in session state if not already present
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        # Sidebar: Display previous chat history
        
        for message in st.session_state.chat_history:
            with st.chat_message(message['role']):
                st.write(message['text'])

        query = st.chat_input(placeholder="Hello!")
        if query:
            # Display the user query in the sidebar
            with st.chat_message("user"):
                st.write(query)
            
            # Store the user query in the chat history
            st.session_state.chat_history.append({"role": "user", "text": query})

            # Send query to the Flask API (Dockerized agent)
            try:
                # URL for Flask API
                flask_api_url = "http://localhost:5000/get_response"  # Adjust if necessary
                response = requests.post(flask_api_url, json={"query": query})

                if response.status_code == 200:
                    response_data = response.json()

                    # Extract response output from Flask
                    agent_response = response_data.get("response", {}).get("output", "No response from agent.")
                    
                    # Display the agent's response in the sidebar
                    with st.chat_message("agent", avatar="assistant"):
                        st.write(agent_response)

                    # Store the agent's response in the chat history
                    st.session_state.chat_history.append({"role": "agent", "text": agent_response})

                else:
                    st.error(f"Error from Flask API: {response.status_code}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")




# Run the app
if __name__ == "__main__":
    main()
