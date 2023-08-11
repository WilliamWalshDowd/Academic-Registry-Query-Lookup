const inputField = document.getElementById("input");
inputField.addEventListener("keydown", (e) => {
    if (e.code === "Enter") {
        let input = inputField.value;
        inputField.value = "";
        output(input);
    }
});

function output(input) {
    let product;
    product = 'test';
    var output;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "AllQueries.py?text=" + text, true);
    xhr.responseType = "JSON";
    xhr.onload = function(e) {
        var arrOfStrings = JSON.parse(xhr.response);
    }
    xhr.send();

    addChatEntry(input, JSON.stringify(output));
}

function addChatEntry(input, product) {
    const messagesContainer = document.getElementById("messages");
    let userDiv = document.createElement("div");
    userDiv.id = "user";
    userDiv.className = "user response";
    userDiv.innerHTML = `<span>${input}</span>`;
    messagesContainer.appendChild(userDiv);

    let botDiv = document.createElement("div");
    let botText = document.createElement("span");
    botDiv.id = "bot";
    botDiv.className = "bot response";
    botText.innerText = "Typing...";
    botDiv.appendChild(botText);
    messagesContainer.appendChild(botDiv);

    messagesContainer.scrollTop =
        messagesContainer.scrollHeight - messagesContainer.clientHeight;

    setTimeout(() => {
        botText.innerText = `${product}`;
    }, 2000);
}