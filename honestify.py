import streamlit as st
import json
import matplotlib.pyplot as plt

# Clear cache to ensure the latest data is loaded (Optional: can be removed if no caching issues arise)
st.cache_data.clear()

# Set up the Streamlit app appearance
st.markdown('<h1 style="text-align: center; font-size: 28px; margin: 0; padding: 0; color: gray;">Honestify</h1>', unsafe_allow_html=True)

logo = '''
<div style="text-align: right;">
    <img src="https://bestofworlds.se/img/BoWlogo.png" width="150px">
</div>
'''
st.markdown(logo, unsafe_allow_html=True)

# Sidebar for UUID input
st.sidebar.title("Honestify Response Viewer")
uuid_input = st.sidebar.text_input("Enter your Question Maker UUID:")

# Load the data from questions.json and responses.json
questions_url = 'https://www.bestofworlds.se/honestify/questions.json'
responses_url = 'https://www.bestofworlds.se/honestify/responses.json'

@st.cache_data
def load_data(url):
    with st.spinner(f"Loading data from {url}..."):
        try:
            import requests
            response = requests.get(url)
            response.raise_for_status()
            return json.loads(response.text)
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return []

questions_data = load_data(questions_url)
responses_data = load_data(responses_url)

# Initialize session state for showing comments or diagram
if "show_comments" not in st.session_state:
    st.session_state["show_comments"] = False

# Buttons to toggle between views
if st.sidebar.button("Show Diagram"):
    st.session_state["show_comments"] = False
if st.sidebar.button("Show Comments"):
    st.session_state["show_comments"] = True

if uuid_input:
    # Find the corresponding question from questions.json
    matching_question_data = [entry for entry in questions_data if entry["question_maker_uuid"] == uuid_input]
    
    if matching_question_data:
        # Extract the question text
        question = matching_question_data[0].get("question", "No question found for this UUID.")
        st.sidebar.subheader(f"Question: {question}")
        
        # Filter responses from responses.json for this UUID
        matching_responses = [entry for entry in responses_data if entry["question_maker_uuid"] == uuid_input]

        if matching_responses:
            # Conditionally render the diagram or the comments based on button clicks
            if not st.session_state["show_comments"]:
                # Show the diagram (Yes/No responses)
                st.subheader("")

                # Count Yes and No responses
                yes_count = sum(1 for entry in matching_responses if entry.get("answer", "").lower() == "yes")
                no_count = sum(1 for entry in matching_responses if entry.get("answer", "").lower() == "no")
                total_responses = yes_count + no_count

                # Plot the Yes/No chart using Matplotlib
                fig, ax = plt.subplots()

                # Remove the frame and y-axis labels
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_color('#DDDDDD')  # Subtle bottom line
                ax.get_yaxis().set_visible(False)

                # Plot bars with earth tone colors
                ax.bar(["Yes", "No"], [yes_count, no_count], color=['#7eadc4', '#47768e'])

                # Add the title and remove axis labels
                ax.set_title("Responses: Yes vs No", fontsize=16)

                # Display the chart
                st.pyplot(fig)

                # Display the total number of responses below the chart
                st.markdown(f"<p style='text-align:center; font-size:18px;'>Total Responses: {total_responses}</p>", unsafe_allow_html=True)
            else:
                # Show the comments
                st.subheader("Comments")
                comments = [entry.get("comment", "") for entry in matching_responses if entry.get("comment")]
                if comments:
                    for i, comment in enumerate(comments, start=1):
                        st.write(f"{i}. {comment}")
                else:
                    st.write("No comments available.")
        else:
            st.sidebar.error("No responses found for this UUID.")
    else:
        st.sidebar.error("No matching question found for this UUID.")
else:
    st.sidebar.info("Please enter your Question Maker UUID to load data.")
