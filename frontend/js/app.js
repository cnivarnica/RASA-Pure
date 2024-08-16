const userInput = document.getElementById('user-input');
const chatBox = document.getElementById('chat-box');
const settingsBtn = document.getElementById('settings-btn');
const settingsModal = document.getElementById('settings-modal');
const closeSettings = document.getElementById('close-settings');
const themeSelect = document.getElementById('theme-select');
const fontSizeSelect = document.getElementById('font-size-select');

let lastMessageTime = 0;
const MESSAGE_RATE_LIMIT = 1000;

userInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
    }
});

settingsBtn.addEventListener('click', () => {
    settingsModal.style.display = 'block';
});

closeSettings.addEventListener('click', () => {
    settingsModal.style.display = 'none';
});

themeSelect.addEventListener('change', (e) => {
    document.body.className = `theme-${e.target.value}`;
    localStorage.setItem('theme', e.target.value);
});

fontSizeSelect.addEventListener('change', (e) => {
    document.body.classList.remove('font-size-small', 'font-size-medium', 'font-size-large');
    document.body.classList.add(`font-size-${e.target.value}`);
    localStorage.setItem('fontSize', e.target.value);
});

async function sendMessage() {
    const currentTime = Date.now();
    if (currentTime - lastMessageTime < MESSAGE_RATE_LIMIT) {
        alert('Please wait a moment before sending another message.');
        return;
    }
    lastMessageTime = currentTime;

    const message = userInput.value.trim();
    if (!message) return;
    addMessageToChatBox(message, 'user');
    userInput.value = '';
    showTypingIndicator();
    try {
        await fetchBotResponse(message);
    } catch (error) {
        console.error('Error:', error);
        addMessageToChatBox('Sorry, I encountered an error. Please try again later.', 'bot');
    } finally {
        hideTypingIndicator();
    }
}


async function fetchBotResponse(message) {
    try {
        const response = await fetch('http://localhost:5005/webhooks/rest/webhook', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        if (!response.ok) throw new Error('Network response was not ok');

        const messages = await response.json();

        for (const msg of messages) {
            // Check if the message contains text or buttons
            if (msg.text && msg.buttons) {
                addMessageWithButtons(msg.text, msg.buttons, 'bot');
            } else if (msg.text) {
                addMessageToChatBox(msg.text, 'bot');
            } else if (msg.buttons) {
                addMessageWithButtons("", msg.buttons, 'bot');
            }
        }
    } catch (error) {
        console.error('Error fetching bot response:', error);
        addMessageToChatBox('Sorry, I encountered an error. Please try again later.', 'bot');
    }
}


function addMessageWithButtons(text, buttons, sender) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);

    // Add the message text
    const textElement = document.createElement('div');
    textElement.innerHTML = `${sanitizeHTML(text).replace(/\n/g, '<br>')}`;
    messageElement.appendChild(textElement);

    // Add the buttons
    const buttonContainer = document.createElement('div');
    buttonContainer.classList.add('button-container');

    buttons.forEach(button => {
        const btn = document.createElement('button');
        btn.classList.add('chat-button');
        btn.textContent = button.title;
        btn.onclick = () => handleButtonClick(btn, button.payload);
        buttonContainer.appendChild(btn);
    });

    messageElement.appendChild(buttonContainer);

    // Add the timestamp
    const timestampElement = document.createElement('div');
    timestampElement.classList.add('message-timestamp');
    timestampElement.textContent = getCurrentTimestamp();
    messageElement.appendChild(timestampElement);

    chatBox.appendChild(messageElement);
    scrollToBottom();
}

function handleButtonClick(button, payload) {
    // Change button appearance to show it has been visited
    button.classList.add('visited');

    // Disable all buttons in the same container
    const buttonContainer = button.closest('.button-container');
    const buttons = buttonContainer.querySelectorAll('.chat-button');
    buttons.forEach(btn => {
        btn.disabled = true;
        btn.classList.add('disabled');
    });

    // Send the payload to the Rasa server
    fetchBotResponse(payload);
}


function showTypingIndicator() {
    const typingMessage = document.createElement('div');
    typingMessage.classList.add('message', 'bot', 'typing-indicator');
    typingMessage.id = 'typing-indicator';
    typingMessage.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
    chatBox.appendChild(typingMessage);
    scrollToBottom();
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) typingIndicator.remove();
}

function addMessageToChatBox(message, sender) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);
    messageElement.innerHTML = `
        ${sanitizeHTML(message).replace(/\n/g, '<br>')}
        <div class="message-timestamp">${getCurrentTimestamp()}</div>
    `;
    chatBox.appendChild(messageElement);
    scrollToBottom();
}

function sanitizeHTML(text) {
    const temp = document.createElement('div');
    temp.textContent = text;
    return temp.innerHTML;
}

function getCurrentTimestamp() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

themeSelect.addEventListener('change', (e) => {
    document.body.className = `theme-${e.target.value} font-size-${fontSizeSelect.value}`;
    localStorage.setItem('theme', e.target.value);
});

fontSizeSelect.addEventListener('change', (e) => {
    document.body.classList.remove('font-size-small', 'font-size-medium', 'font-size-large');
    document.body.classList.add(`font-size-${e.target.value.toLowerCase()}`);
    localStorage.setItem('fontSize', e.target.value.toLowerCase());
});

function loadSettings() {
    const theme = localStorage.getItem('theme') || 'light';
    const fontSize = localStorage.getItem('fontSize') || 'medium';
    document.body.className = `theme-${theme} font-size-${fontSize}`;
    themeSelect.value = theme;
    fontSizeSelect.value = fontSize.charAt(0).toUpperCase() + fontSize.slice(1);
}

function initChat() {
    loadSettings();
    addMessageToChatBox('Welcome to the Rasa Game Bot! I can play Chess and Story RPG :)', 'bot');
}

initChat();

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => {
                console.log('ServiceWorker registration successful with scope: ', registration.scope);
            }, err => {
                console.log('ServiceWorker registration failed: ', err);
            });
    });
}
