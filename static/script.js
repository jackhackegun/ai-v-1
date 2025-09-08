/*
 * Front‑end script for the ai‑v‑1 chatbot.
 *
 * This script listens for click events on the send button and the Enter key
 * within the input box, appends the user's message to the chat, makes a
 * POST request to the `/chat` endpoint, and appends the AI's response.
 */

document.addEventListener('DOMContentLoaded', () => {
  const chatContainer = document.getElementById('chat-container');
  const messageInput = document.getElementById('message-input');
  const sendBtn = document.getElementById('send-btn');

  function appendMessage(text, className) {
    const msgElem = document.createElement('div');
    msgElem.classList.add('message', className);
    msgElem.textContent = text;
    chatContainer.appendChild(msgElem);
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }

  async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;
    appendMessage(text, 'user');
    messageInput.value = '';
    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      appendMessage(data.response, 'bot');
    } catch (err) {
      appendMessage('Error: ' + err.message, 'bot');
    }
  }

  sendBtn.addEventListener('click', sendMessage);
  messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  });
});
