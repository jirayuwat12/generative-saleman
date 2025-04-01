format-all:
	isort .
	black .

test:
	pytest

run-streamlit:
	uv run streamlit run ./scripts/chatbot_streamlit.py