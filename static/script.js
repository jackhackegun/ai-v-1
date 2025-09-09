document.addEventListener('DOMContentLoaded', () => {
  const form   = document.getElementById('chat-form');
  const input  = document.getElementById('user-input');
  const sendBtn= document.getElementById('send-btn');
  const chat   = document.getElementById('chat-container');

  if (!form || !input || !sendBtn || !chat) {
    console.error('Required elements not found. Check element IDs in HTML.');
    return;
  }

  const append = (who, text) => {
    const row = document.createElement('div');
    row.classList.add('message');
    row.classList.add(who);
    row.textContent = text;
    chat.appendChild(row);
    chat.scrollTop = chat.scrollHeight;
  };

  const send = async () => {
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    append('user', text);

    sendBtn.disabled = true;
    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });

      if (!res.ok) {
        append('bot', `오류: 서버 상태 ${res.status}`);
        return;
      }

      const data = await res.json();
      const reply = data.reply ?? data.response ?? '(응답 없음)';
      append('bot', reply);
    } catch (e) {
      append('bot', `네트워크 오류: ${e.message}`);
    } finally {
      sendBtn.disabled = false;
      input.focus();
    }
  };

  form.addEventListener('submit', (ev) => {
    ev.preventDefault();
    send();
  });

  input.addEventListener('keydown', (ev) => {
    if (ev.key === 'Enter' && !ev.shiftKey) {
      ev.preventDefault();
      form.requestSubmit();
    }
  });
});
