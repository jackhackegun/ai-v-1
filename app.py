"""
Simple conversational AI server.

This script exposes a minimal web server using Flask.  The server provides two
routes: a root route that serves a basic HTML front en‑end and a `/chat` route
that accepts JSON payloads containing a user message.  The AI responds to
messages by performing a handful of reasoning tasks including arithmetic
evaluation, date/time queries and conversational memory.  Conversation history
is persisted in a SQLite database (`conversation.db`) so that the model can
refer back to past exchanges.

This project intentionally avoids relying on any large external models or
internet access – it uses only the Python standard library and Flask.

Running locally
--------------
1. Install Flask if it's not already installed:

   ```bash
   pip install Flask
   ```

2. Start the server:

   ```bash
   python app.py
   ```

3. Open `http://127.0.0.1:5000` in your browser.

The AI will remember your conversation across page reloads thanks to the
SQLite database.
"""

from __future__ import annotations

import ast
import datetime as _dt
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

from flask import Flask, jsonify, render_template, request
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "conversation.db"

# ---------------------------------------------------------------------------
# Database helpers
#
# The following functions wrap SQLite operations.  A single table named
# `messages` stores each conversation turn.  The table has the following
# columns:
#   id          INTEGER PRIMARY KEY AUTOINCREMENT
#   timestamp   TEXT    – ISO 8601 timestamp of when the message/response was stored
#   user_msg    TEXT    – original user message
#   ai_msg      TEXT    – AI's response to the user message

def init_db() -> None:
    """Ensure the SQLite database and messages table exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user_msg TEXT NOT NULL,
            ai_msg TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def log_message(user_msg: str, ai_msg: str) -> None:
    """Insert a new conversation turn into the database."""
    timestamp = _dt.datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (timestamp, user_msg, ai_msg) VALUES (?, ?, ?)",
        (timestamp, user_msg, ai_msg),
    )
    conn.commit()
    conn.close()


def fetch_history(limit: int = 20) -> List[Tuple[str, str]]:
    """Fetch the most recent conversation turns from the database.

    Returns a list of tuples (user_msg, ai_msg).  The oldest of the requested
    turns appears first.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT user_msg, ai_msg FROM messages ORDER BY id DESC LIMIT ?", (limit,)
    )
    rows = c.fetchall()
    conn.close()
    # Reverse to chronological order
    return rows[::-1]


# ---------------------------------------------------------------------------
# AI logic
#
# The `generate_response` function encapsulates the reasoning ability of
# this AI.  It attempts to parse arithmetic expressions safely, answer
# date/time queries, recall prior conversation and provide a unique identity.

class ExpressionEvaluator(ast.NodeVisitor):
    """Safely evaluate arithmetic expressions using the ast module.

    Only supports numeric literals and the operators +, -, *, /, **, //, %.
    Does not allow variables or function calls.  Raises ValueError on
    unsupported nodes or division by zero.
    """

    def visit(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Expression):
            return self.visit(node.body)
        elif isinstance(node, ast.BinOp):
            left = self.visit(node.left)
            right = self.visit(node.right)
            op = node.op
            if isinstance(op, ast.Add):
                return left + right
            if isinstance(op, ast.Sub):
                return left - right
            if isinstance(op, ast.Mult):
                return left * right
            if isinstance(op, ast.Div):
                return left / right
            if isinstance(op, ast.FloorDiv):
                return left // right
            if isinstance(op, ast.Mod):
                return left % right
            if isinstance(op, ast.Pow):
                return left ** right
            raise ValueError("Unsupported operator")
        elif isinstance(node, ast.UnaryOp):
            operand = self.visit(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            if isinstance(node.op, ast.USub):
                return -operand
            raise ValueError("Unsupported unary operator")
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            else:
                raise ValueError("Only numeric constants are allowed")
        else:
            raise ValueError("Invalid expression")


def safe_eval(expr: str) -> float:
    """Evaluate a simple arithmetic expression safely."""
    try:
        tree = ast.parse(expr, mode="eval")
        evaluator = ExpressionEvaluator()
        return evaluator.visit(tree)
    except Exception as e:
        raise ValueError(f"Invalid arithmetic expression: {e}")


def generate_response(message: str) -> str:
    """Generate a response to the user's message.

    The AI can:
      * Evaluate basic arithmetic expressions (e.g. "2 + 2").
      * Tell the current date or time.
      * Recall recent conversation history when asked.
      * Describe itself and how it differs from other AI assistants.
      * Provide a fallback response when it cannot help.

    Parameters
    ----------
    message: str
        The user's input string.

    Returns
    -------
    str
        The AI's response.
    """
    msg = message.strip().lower()
    # 1. Arithmetic detection: if the message contains digits and arithmetic symbols
    has_digit = any(ch.isdigit() for ch in msg)
    has_arith_op = any(op in msg for op in ['+', '-', '*', '/', '%'])
    if has_digit and has_arith_op:
        try:
            result = safe_eval(msg)
            # Format result to avoid long floating point tails
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return f"The result is {result}."
        except ValueError:
            pass  # fall through to other handling

    # 2. Date/time queries
    now = _dt.datetime.now()
    if any(word in msg for word in ["date", "day", "today", "날짜", "요일"]):
        # Return the local date in YYYY-MM-DD format
        return f"Today's date is {now.strftime('%Y-%m-%d')} (local time)."
    if any(word in msg for word in ["time", "현재 시간", "시각", "hour", "minute"]):
        return f"The current time is {now.strftime('%H:%M:%S')} (local time)."

    # 3. Conversation history recall
    if any(word in msg for word in ["history", "memory", "log", "대화", "내역", "지난", "remember"]):
        history = fetch_history(limit=10)
        if not history:
            return "There is no previous conversation yet."
        formatted = []
        for i, (user_msg, ai_msg) in enumerate(history, 1):
            formatted.append(f"{i}. You said: '{user_msg}' | I responded: '{ai_msg}'")
        return "Here is our recent conversation history:\n" + "\n".join(formatted)

    # 4. Self‑identification
    if any(phrase in msg for phrase in ["who are you", "what are you", "이름", "정체", "your difference"]):
        return (
            "I am a small open‑source AI assistant. Unlike large models such as ChatGPT "
            "or Gemini, I run entirely on simple logic without access to external APIs "
            "or massive datasets. I can perform arithmetic, tell the date and time, and "
            "remember our conversation, but I don't pretend to know everything."
        )

    # 5. Generic fallback
    return (
        "I'm sorry, I don't have enough information to answer that. "
        "I'm still learning and rely on simple reasoning rather than vast knowledge."
    )


# ---------------------------------------------------------------------------
# Flask application

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"), static_folder=str(BASE_DIR / "static"))


@app.route("/")
def index() -> Any:
    """Serve the chat UI."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat() -> Any:
    """Handle a chat message from the client.

    Expects JSON like `{\"message\": \"hello\"}` and returns JSON
    `{\"response\": \"...\"}`.
    """
    data: Dict[str, Any] = request.get_json(force=True)
    user_msg = data.get("message", "").strip()
    if not user_msg:
        return jsonify({"response": "Please provide a message."})
    ai_response = generate_response(user_msg)
    log_message(user_msg, ai_response)
    return jsonify({"response": ai_response})


if __name__ == "__main__":
    init_db()
    # Use port 5000 by default; host='0.0.0.0' for remote access
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
