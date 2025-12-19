document.addEventListener('DOMContentLoaded', () => {
    const chatArea = document.getElementById('chat-area');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const statusIndicator = document.getElementById('status-indicator');

    // Auto-resize textarea
    userInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';

        // Enable/disable button
        if (this.value.trim()) {
            sendBtn.removeAttribute('disabled');
        } else {
            sendBtn.setAttribute('disabled', 'true');
        }
    });

    // Handle enter key to submit
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (userInput.value.trim()) {
                sendMessage();
            }
        }
    });

    sendBtn.addEventListener('click', () => {
        if (userInput.value.trim()) {
            sendMessage();
        }
    });

    function appendMessage(role, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', role);

        const avatar = document.createElement('div');
        avatar.classList.add('avatar');
        avatar.innerHTML = role === 'user' ? '<i class="fa-regular fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';

        const content = document.createElement('div');
        content.classList.add('message-content');

        if (role === 'bot') {
            // For bot, we might start with empty and stream content
            content.innerHTML = marked.parse(text);
        } else {
            content.textContent = text;
        }

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);

        chatArea.appendChild(messageDiv);
        chatArea.scrollTop = chatArea.scrollHeight;

        return content; // Return content div to update it later
    }

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        // Clear input
        userInput.value = '';
        userInput.style.height = 'auto';
        sendBtn.setAttribute('disabled', 'true');

        // User Message
        appendMessage('user', text);

        // Bot Placeholder
        const botMessageContent = appendMessage('bot', '...'); // Show typing or placeholder
        let accumulatedResponse = '';

        // Remove the loading text when streaming starts
        botMessageContent.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });

            if (!response.ok) {
                botMessageContent.innerHTML = `<span style="color: #ef4444">Error: ${response.statusText}</span>`;
                return;
            }

            // Stream reading
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            // Clear typing indicator
            botMessageContent.innerHTML = '';

            let done = false;
            while (!done) {
                const { value, done: doneReading } = await reader.read();
                done = doneReading;
                const chunkValue = decoder.decode(value, { stream: true });

                // The chunk might contain multiple JSON lines (NDJSON)
                const lines = chunkValue.split('\n');

                for (const line of lines) {
                    if (!line.trim()) continue;

                    try {
                        const json = JSON.parse(line);

                        if (json.error) {
                            botMessageContent.innerHTML += `<br/><span style="color: #ef4444">[Error: ${json.error}]</span>`;
                        } else if (json.chunk) {
                            accumulatedResponse += json.chunk;
                            // Re-render markdown
                            botMessageContent.innerHTML = marked.parse(accumulatedResponse);
                            // Scroll to bottom
                            chatArea.scrollTop = chatArea.scrollHeight;
                        }
                    } catch (e) {
                        console.error("Error parsing JSON chunk", e);
                    }
                }
            }

        } catch (err) {
            botMessageContent.innerHTML = `<span style="color: #ef4444">Error: ${err.message}</span>`;
        }
    }
});
