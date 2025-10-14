const chatButton = document.getElementById("chatbot-button");
const chatbox = document.getElementById("chatbox");
const chatClose = document.getElementById("chat-close");
const chatSend = document.getElementById("chat-send");
const chatInput = document.getElementById("chat-input");
const chatMessages = document.getElementById("chat-messages");

chatButton.addEventListener("click", () => {
    chatbox.style.display = "flex";
});
chatClose.addEventListener("click", () => {
    chatbox.style.display = "none";
});
chatSend.addEventListener("click", sendMessage);
chatInput.addEventListener("keypress", function(e){
    if(e.key === "Enter") sendMessage();
});
function sendMessage() {
    const message = chatInput.value.trim();
    if(!message) return;
    const userP = document.createElement("p");
    userP.className = "user-msg";
    userP.innerText = message;
    chatMessages.appendChild(userP);
    chatInput.value = "";
    chatMessages.scrollTop = chatMessages.scrollHeight;
    fetch("/chat_ai", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message})
    })
    .then(res => res.json())
    .then(data => {
        const botP = document.createElement("p");
        botP.className = "bot-msg";
        botP.innerText = data.response || data.error;
        chatMessages.appendChild(botP);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });
}