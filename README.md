conda create -n lang3 python=3.11 -y
conda activate lang3

pip install -r requirements.txt

uvicorn backend:app --reload

streamlit run app.py