// Function to scroll the chat box to the bottom
function scrollToBottom() {
    const chatBox = document.getElementById('chat-box');
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Event Listener on 'send' button click
document.getElementById('send-button').addEventListener('click', async () => {

    // Retrieve user's input text
    const userInput = document.getElementById('user-input').value;
    if (!userInput) return;

    // Delete user input from text bar
    document.getElementById('user-input').value = '';

    // Write User message in the chat window
    const chatBox = document.getElementById('chat-box');
    const userMessage = document.createElement('p');
    userMessage.className = 'user-message';
    userMessage.textContent = userInput;
    chatBox.appendChild(userMessage);
    scrollToBottom(); // Scroll to bottom after adding the user message

    // Write temporary "thinking" message in the chat window
    const thinkingMessage = document.createElement('p');
    thinkingMessage.className = "bot-thinking";
    thinkingMessage.innerHTML = "I am thinking...";
    chatBox.appendChild(thinkingMessage);
    scrollToBottom();

    try {

        // Make query to endpoint
        const response = await fetch('/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: userInput })
        });

        // Retrieve response from query endpoint
        const data = await response.json();
        const { answer, sources } = data;

        // Remove the "thinking" message
        chatBox.removeChild(thinkingMessage);

        // Create a container for the chatbot's response + sources
        const botResponseContainer = document.createElement('div');
        botResponseContainer.className = 'bot-message';

        // Add chatbot response text to the response container
        const botMessageText = document.createElement('p');
        botMessageText.textContent = answer;
        botResponseContainer.appendChild(botMessageText);

        // Deal with the list of sources, if they exist
        if (sources && sources.length > 0) {

            const collapsibleRow = document.createElement('div');
            collapsibleRow.className = 'collapsible-row';

            const sourcesButton = document.createElement('button');
            sourcesButton.className = 'sources-button';
            sourcesButton.innerHTML = 'Show sources <span class="collapsible-icon">+</span>';

            const sourcesContent = document.createElement('div');
            sourcesContent.className = 'sources-content';
            sourcesContent.style.display = 'none';

            // Retrieve list of sources
            const sourcesList = document.createElement('ul');
            sources.forEach(source => {
                const listItem = document.createElement('li');
                listItem.textContent = source;
                sourcesList.appendChild(listItem);
            });
            sourcesContent.appendChild(sourcesList);

            // Attach click event to collapsible
            sourcesButton.addEventListener('click', function () {
                const contentVisible = sourcesContent.style.display === 'block';
                sourcesContent.style.display = contentVisible ? 'none' : 'block';
                this.innerHTML = `Show sources <span class="collapsible-icon">${contentVisible ? '+' : '-'}</span>`;
            });

            // Add collapsible button to the response container
            collapsibleRow.appendChild(sourcesButton);
            botResponseContainer.appendChild(collapsibleRow);
            botResponseContainer.appendChild(sourcesContent);
        }

        // Show chatbot response container in the chat window
        chatBox.appendChild(botResponseContainer);
        scrollToBottom();

        // Add a divider after each question-answer pair
        const divider = document.createElement('div');
        divider.className = 'message-divider';
        chatBox.appendChild(divider);

        scrollToBottom();

    } catch (error) {

        // Remove the "thinking" message
        chatBox.removeChild(thinkingMessage);

        // Show error message
        const errorMessage = document.createElement('p');
        errorMessage.className = 'bot-message';
        errorMessage.textContent = 'Error communicating with the server.';
        chatBox.appendChild(errorMessage);

        scrollToBottom();
    }
});
