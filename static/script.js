document.addEventListener('DOMContentLoaded', function() {
    var socket = io();

    // Function to add a message to the chat window
    function addMessage(data) {
        var chatWindow = document.getElementById('chat-window');
        var messageDiv = document.createElement('div');
        messageDiv.textContent = data.username + ": " + data.message;
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    // Load previous messages from the server
    fetch('/messages')
        .then(response => response.json())
        .then(data => {
            data.forEach(function(msg) {
                addMessage(msg);
            });
        });

    // Listen for incoming chat messages from the server
    socket.on('chat_message', function(data) {
        addMessage(data);
    });

    // Handle sending a new message
    document.getElementById('message-form').addEventListener('submit', function(e) {
        e.preventDefault(); // Prevent the page from refreshing
        var messageInput = document.getElementById('message-input');
        var message = messageInput.value;
        if (message.trim() !== "") {
            socket.emit('chat_message', { username: username, message: message });
            messageInput.value = '';
        }
    });
});
