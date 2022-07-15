/**********
 * Imports
 **********/

 import {setCSS, createDiv, createPost, print} from "./nd_utils.js";

 /* end of 'imports.js' block */

//const buttonMessage = document.getElementById('button_message');
//const butttonAddUser = document.getElementById('button_add_user')
//const butttonDeleteUser = document.getElementById('button_delete_user')
const inputUserName = document.getElementById('input_user_name')
const inputMessage = document.getElementById('textarea_message');
const selector = document.getElementById('chat_selector');
const messager = document.getElementById('chat_messager');
const textCurrentUser = document.getElementById('text_current_user');

// user name input reponse
inputUserName.addEventListener("keyup", function(event) {
    if (event.key === "Enter") {
        if (inputUserName.value.trim() === '') {
            alert( "Название должно вдохновлять" );
            return;
        }

        addUser(inputUserName.value);

        inputUserName.value = '';
    }
});


function addUser(name) {
    const body = {
        type: 'add_user',
        user_name: name
    }

    createPost(body, updateSelector);
}

function deleteUser(name) {
    const body = {
        type: 'delete_user',
        user_name: name
    };
    createPost(body, updateSelector);
}

function selectUser(name) {
    const body = {
        type: 'select_user',
        user_name: name
    };
    createPost(body, updateMessager);
}


function updateSelector(response) {
    if (!response.debug_users) {
        console.log("Error: wrong response format");
        return;
    }

    selector.innerHTML = ''

    const fragment = document.createDocumentFragment();
    const debug_users = response.debug_users;
    debug_users.forEach(user => {
        const item = createDiv('roller__item');
        const tag = createDiv('tag', 'bot_name');
        
        const nameItem = createDiv("item");
        nameItem.innerText = user.name;

        const buttonSelect = createDiv("button", "arrows", "item");
        buttonSelect.addEventListener('click', () => {
            selectUser(user.name);
        });

        const buttonDelete = createDiv("button", "cross", "item");
        buttonDelete.addEventListener('click', () => {
            deleteUser(user.name);
        });


        tag.append(nameItem);
        tag.append(buttonSelect);
        tag.append(buttonDelete);
        item.append(tag);
        fragment.appendChild(item);
    });

    selector.appendChild(fragment);

    selector.scrollTop = selector.scrollHeight;
}

/* Chat */

function sendMessage() {
    const body = {
        'type' : 'message_new',
        'text' : inputMessage.value,
    };

    let timerId = setTimeout(()=>{inputMessage.value = ''}, 100);

    createPost(body, updateMessager);
}


function checkForSend() {
    let pressed = new Set();

    inputMessage.addEventListener('keydown', function(event) {
        pressed.add(event.code);

        if (event.code == "Enter" && !pressed.has("ShiftLeft") && !pressed.has("ShiftRight"))
            sendMessage();
    });

    inputMessage.addEventListener('keyup', function(event) {
        pressed.delete(event.code);
    });
}

// update messager
function updateMessager(response) {
    if (!response.current_user && response.current_user !== '') {
        console.log("Error: wrong response format");
        return;
    }

    messager.innerHTML = '';

    if (response.current_user === '') {
        textCurrentUser.innerHTML = 'Select user';
        return;
    }

    textCurrentUser.innerHTML = response.current_user;

    const fragment = document.createDocumentFragment();
    const messages = response.messages;
    messages.forEach(msg => {
        const item = createDiv('roller__item');
        const tag = createDiv('tag', 'chat_msg');

        if (msg.type === 'bot') {
            item.classList.add('left');
            tag.classList.add('left');
        } else {
            item.classList.add('right');
            tag.classList.add('right');
        }

        tag.innerText = msg.text;

        item.append(tag);
        fragment.appendChild(item);
    });

    messager.appendChild(fragment);
    messager.scrollTop = messager.scrollHeight;
    console.dir(messager);
}




/* Global update */


export function updateChat() {
    const body = {
        type: 'chat_update',
    };

    createPost(body, (response)=>{
        updateSelector(response);
        updateMessager(response);
    });
}

document.addEventListener('DOMContentLoaded', () => {

    updateChat();
    console.log("Loaded2");


    checkForSend();
});





