#we used llama3.1 for extracting and qwen-math for answering them
#we used ngrok to run  the server

python backend.py
ngrok http 8000

#for the site in setting put "https://collative-tanika-uncriticisable.ngrok-free.dev" or the link ngrok give you if it doesn't want to work