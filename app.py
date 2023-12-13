import streamlit as st
import spacy
import xgboost as xgb
import pandas as pd
import plotly.express as px
import time

# List of stages
stages = ["Stage 1 - Loading NLP Model",
		  "Stage 2 - Loading XGBoost Model",
		  "Stage 3 - Reading Data"
		 ]

# Function to load NLP model
def load_nlp_model(sub_header, place_holder):
	# sub_header.subheader(stages[0])
	try:
		# Load SpaCy model
		nlp = spacy.load("en_core_web_md")
		# place_holder.success("NLP Model Loaded Successfully!")
		# time.sleep(1)
		return nlp
	except Exception as e:
		place_holder.error(f"Error loading NLP model: {e}")
		return None

# Function to load XGBoost model
def load_xgboost_model(sub_header, place_holder):
	# sub_header.subheader(stages[1])
	try:
		# Load XGBoost model
		xgboost_model = xgb.XGBClassifier()
		xgboost_model.load_model('xgboost_model_11122023.json')
		# place_holder.success("XGBoost Model Loaded Successfully!")
		# time.sleep(1)
		return xgboost_model
	except Exception as e:
		raise("Can't load model")
		place_holder.error(f"Error loading XGBoost model: {e}")
		return None

# Function to read labeled data
def read_labeled_data(sub_header, place_holder):
	# sub_header.subheader(stages[2])
	try:
		# Read the labeled data
		labeled_data = pd.read_excel('Labelled_Windows_Cmd.xlsx')
		# place_holder.success("Data Read Successfully!")
		time.sleep(1)
		return labeled_data
	except Exception as e:
		raise("Failed to load file")
		place_holder.error(f"Error reading labeled data: {e}")
		return None

sub_header = st.empty()
place_holder = st.empty()

# Sidebar for navigation
menu = ["Prediction", "Insights"]
choice = st.sidebar.selectbox("Select Page", menu)

# Main app logic
if choice == "Prediction":	
	if 'nlp' not in globals():
		nlp = load_nlp_model(sub_header, place_holder)
		sub_header.empty()
		place_holder.empty()
	if 'xgboost_model' not in globals():
		xgboost_model = load_xgboost_model(sub_header, place_holder)
		sub_header.empty()
		place_holder.empty()
	
	st.markdown("<h1 style='text-align: center;'>Prediction for malicious Windows commands</h1>", unsafe_allow_html=True)
	st.markdown("<h5>Note: Model Accuracy - up to 88%</h5>", unsafe_allow_html=True)

	# User input prompt
	user_input = st.text_input("Enter a prompt:")

	if user_input:
		# Convert user input to SpaCy vector
		user_input_vector = nlp(user_input).vector.tolist()

		# Make prediction with the loaded XGBoost model
		prediction = xgboost_model.predict([user_input_vector])[0]
		probability = xgboost_model.predict_proba([user_input_vector])[0][1]

		# Display the result
		st.subheader("Prediction Result")
		st.write(f"Is it malicious : {bool(prediction)}")
		st.write(f"Probability of being malicious: {probability*100:.4f}")

elif choice == "Insights":
	if 'labeled_data' not in globals():
		labeled_data = read_labeled_data(sub_header, place_holder)
		sub_header.empty()
		place_holder.empty()

	# Subheading for insights
	st.markdown("<h1 style='text-align: center;'>Model Insights</h1>", unsafe_allow_html=True)

	# Check if 'prompt' column exists in labeled_data
	if 'prompt' not in labeled_data.columns:
		st.error("Error: 'prompt' column not found in labeled_data. Please check your column names.")
	else:
		# Insights 1: Common words for Malicious Label
		malicious_words = labeled_data[labeled_data['is_malicious'] == 1]['prompt'].str.split().explode().value_counts()
		malicious_words = pd.DataFrame(malicious_words).reset_index()
		st.subheader("1. Most common words in prompts for Malicious Label:")

		# Progress bar for Insights 1
		progress_bar_1 = st.progress(0)
		for percent_complete in range(0, 101, 10):
			progress_bar_1.progress(percent_complete)

		# Check if the DataFrame is not empty before creating the plot
		if not malicious_words.empty:
			sorted_malicious_words = malicious_words.head(10).sort_values(by='count', ascending=False)
			fig1 = px.bar(sorted_malicious_words.head(10), x='prompt',y='count', title="Word Frequency for Malicious Label")
			st.plotly_chart(fig1)
			st.success("Insight 1 Generated !")
		else:
			st.warning("No data available for generating insights.")


		# Insights 2: Common words for non-Malicious Label
		non_malicious_words = labeled_data[labeled_data['is_malicious'] == 0]['prompt'].str.split().explode().value_counts()
		non_malicious_words = pd.DataFrame(non_malicious_words).reset_index()
		st.subheader("2. Most common words in prompts for Non-Malicious Label:")

		# Progress bar for Insights 2
		progress_bar_2 = st.progress(0)
		for percent_complete in range(0, 101, 10):
			progress_bar_2.progress(percent_complete)

		# Check if the DataFrame is not empty before creating the plot
		if not non_malicious_words.empty:
			sorted_non_malicious_words = non_malicious_words.head(10).sort_values(by='count', ascending=False)
			fig2 = px.bar(sorted_non_malicious_words, x='prompt', y='count', title="Word Frequency for Non-Malicious Label")

			st.plotly_chart(fig2)
			st.success("Insight 2 Generated !")
		else:
			st.warning("No data available for generating insights.")