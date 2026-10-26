"use strict";
const form = document.querySelector('#chat-form');
const input = document.querySelector('#message');
const messages = document.querySelector('#messages');
const status = document.querySelector('#status');
const send = document.querySelector('#send');
const clear = document.querySelector('#clear');
let busy = false;
function addMessage(label, text, kind = '', data = null) {
  const article = document.createElement('article');
  article.className = 'message ' + kind;
  const name = document.createElement('span'); name.className = 'label'; name.textContent = label;
  const body = document.createElement('p'); body.textContent = text;
  article.append(name, body);
  if (data) {
    const notice = document.createElement('p'); notice.className = 'notice'; notice.textContent = data.notice; article.append(notice);
    for (const source of data.sources) {
      const link = document.createElement('a'); link.textContent = source.title; link.href = source.url;
      link.target = '_blank'; link.rel = 'noopener noreferrer'; link.referrerPolicy = 'no-referrer'; article.append(link);
    }
  }
  messages.append(article); messages.scrollTop = messages.scrollHeight;
}
form.addEventListener('submit', async event => {
  event.preventDefault(); const message = input.value.trim();
  if (!message || busy) return;
  busy = true; send.disabled = true; clear.disabled = true; status.textContent = 'Checking the supported information…';
  addMessage('YOU', message, 'user'); input.value = '';
  const controller = new AbortController(); const timer = setTimeout(() => controller.abort(), 12000);
  try {
    const response = await fetch('/api/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message}), signal:controller.signal});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Request failed.');
    addMessage('CAREGUIDE', data.answer, data.kind === 'emergency' ? 'emergency' : 'assistant', data);
    status.textContent = '';
  } catch (error) {
    status.textContent = 'Could not get an answer. ' + (error.name === 'AbortError' ? 'The request timed out.' : error.message) + ' For urgent symptoms, contact emergency services directly.';
    input.value = message;
  } finally {
    clearTimeout(timer); busy = false; send.disabled = false; clear.disabled = false; input.focus();
  }
});
input.addEventListener('keydown', event => {if(event.key === 'Enter' && !event.shiftKey && !event.isComposing){event.preventDefault();form.requestSubmit();}});
document.querySelectorAll('[data-prompt]').forEach(button => button.addEventListener('click', () => {if(!busy){input.value = button.dataset.prompt;form.requestSubmit();}}));
clear.addEventListener('click', () => {if(!busy){messages.replaceChildren();status.textContent = '';input.value = '';input.focus();}});
