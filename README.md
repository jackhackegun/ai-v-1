# ai v‑1

`ai‑v‑1` is a minimalistic, self‑hosted chatbot that demonstrates how a
conversational agent can be built without relying on massive language models
or proprietary APIs.  The goal of this project is **not** to rival systems
like ChatGPT, Claude or Gemini, but rather to explore how far simple
reasoning and local memory can take an assistant.

## Features

* **Reasoning over arithmetic:**
  The bot can safely evaluate arithmetic expressions (addition, subtraction,
  multiplication, division, modulo, exponentiation and floor division).

* **Temporal awareness:**
  Ask for the date or time and the bot will reply using the server’s local
  clock.

* **Conversation memory:**
  Interactions are stored in a SQLite database (`conversation.db`).  You can
  ask the bot to recall previous messages from your chat history.

* **Self‑description:**
  The bot can explain what it is and how it differs from other AI
  assistants.  It is designed to minimise hallucination by only answering
  questions it can reason about.

## Getting Started

These instructions will get a copy of the project up and running on your
local machine for development and testing purposes.  See deployment notes for
how to host it publicly.

### Prerequisites

* Python 3.9 or higher
* `pip` to install dependencies

### Installation

1. Clone this repository

   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-v-1.git
   cd ai-v-1
   ```

2. Install Flask (the only external dependency)

   ```bash
   pip install Flask
   ```

3. Start the server

   ```bash
   python app.py
   ```

4. Open your browser and navigate to `http://127.0.0.1:5000` to start
   chatting with `ai‑v‑1`.

### Deployment

`ai‑v‑1` can be deployed to any platform that can run a Python web
application, such as Heroku, Render or your own server.  When deployingp
`ai-v-1` can be deployed to any platform that can run a Python web application, including free hosting services like [Render](https://render.com), [Replit](https://replit.com) or [Railway](https://railway.app). A typical deployment workflow on Render is:

1. Fork this repository to your own GitHub account.
2. Create a free account on Render.com and choose "New Web Service".
3. Connect your GitHub repository when prompted.
4. Set the build command to `pip install -r requirements.txt` and the start command to `python app.py`.
5. Select a Python environment (e.g. Python 3) and deploy. Render will build the container and provide a public URL once ready.

On Heroku, you can deploy using the included **Procfile**:

1. Ensure the Heroku CLI is installed and you are logged in.
2. Run `heroku create` in the project root to create a new app.
3. Run `git push heroku main` to push your code to Heroku.
4. Open the URL provided by Heroku to access the chatbot.

When deploying publicly, remember to set `debug=False` in `app.py` and ensure the SQLite database file is stored in a persistent location.
cation.

## Limitations and Future Work

This project deliberately avoids external knowledge bases, network access or
large pretrained models.  As a result its capabilities are limited.  Future
improvements could include:

* Using word embeddings or small open‑source language models to improve
  response diversity.
* Adding more reasoning modules (e.g. unit conversion, simple search over
  built‑in documents).
* Enhancing the front‑end with markdown rendering and styling.

## License

This project is released under the MIT License.  See the [LICENSE](LICENSE)
file for details.
