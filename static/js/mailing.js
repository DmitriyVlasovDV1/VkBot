
//#region imports

import { quickCoverClosingAnimation } from "./nd_animations.js";
import {setCSS, createDiv, createPost, print} from "./nd_utils.js";
import { updateChat } from "./chat.js";

//#endregion

//#region global elements

const inputMailingName = document.getElementById('input_mailing_name');
const currentMailingName = document.getElementById('current_mailing_name');
const selector = document.getElementById('selector');

const messager = document.getElementById('messager');

const editorMessageName = document.getElementById('mailing_editor_message_name');
const editorMessageText = document.getElementById('mailing_editor_message_text');
const editorMessageTime = document.getElementById('mailing_editor_message_time');

const buttonAddMessage = document.getElementById('add_mailing_message_button');
const buttonEditorSave = document.getElementById("mailing_editor_save_button");
const buttonEditorClose = document.getElementById("mailing_editor_close_button");
const editorWindow = document.getElementById("mailing_editor_window");


let selectedMailing = null;
let selectedMessage = null;


//#endregion


//#region editor

// button add message
buttonAddMessage.addEventListener('click', () => {
    if (selectedMailing !== null) {
        quickCoverClosingAnimation(() => {
            openEditor();
        });
    }
});

// save message button
buttonEditorSave.addEventListener('click', () => {

    print("saving...");
    if (editMessage()) {
        quickCoverClosingAnimation(() => {
            closeEditor();
        });
    }



});


// button close editor
buttonEditorClose.addEventListener('click', () => {
    quickCoverClosingAnimation(() => {
        closeEditor();
    });
});



// Open and close editor
function openEditor() {
    editorWindow.classList.remove("popup_close");

    if (selectedMessage === null) {
        editorMessageName.value = '';
        editorMessageText.value = '';
        editorMessageTime.value = '';
    } else {
        editorMessageName.value = selectedMessage.name;
        editorMessageText.value = selectedMessage.text;
        editorMessageTime.value = new Date(selectedMessage.time).toISOString().substring(0, 19);
    }

    editorWindow.classList.remove('close');
}

function closeEditor() {
    editorWindow.classList.add("close");
    selectedMessage = null;
}


// add/edit message function
function editMessage() {
    if (editorMessageName.value.trim() === '') {
        alert( "Название должно цеплять" );
        return false;
    }

    if (editorMessageText.value.trim() === '') {
        alert( "Содержание должно умилять" );
        return false;
    }

    console.log(editorMessageTime.value );

    if (selectedMessage === null) {
        let time = null
        if (editorMessageTime.value !== '')
            time = editorMessageTime.value.slice(0, 19).replace('T', ' ') + ':00'

        let message = {
            name: editorMessageName.value,
            text: editorMessageText.value,
            is_active: true,
            time: time
        }

        addMessage(message);
    } else {
        let time = null
        if (editorMessageTime.value !== '')
            time = editorMessageTime.value.slice(0, 19).replace('T', ' ') + ':00'
        let message = {
            id: selectedMessage.id,
            name: editorMessageName.value,
            text: editorMessageText.value,
            is_active: true,
            time: time
        }
        updateMessage(message);
    }

    return true;
}

//#endregion

//#region to backend functions 

// send message
function sendMessage(msg) {
    const body = {
        type: 'send_message',
        message: msg
    }
    createPost(body, updateChat);
}

// add message
function addMessage(msg) {
    const body = {
        type: 'add_message',
        message: msg
    }
    createPost(body, updateMessager);
}

// update message
function updateMessage(msg) {
    const body = {
        type: 'update_message',
        message: msg
    }
    createPost(body, updateMessager);
}

// delete message
function deleteMessage(msg) {
    const body = {
        type: 'delete_message',
        message: msg
    }
    createPost(body, updateMessager);
}

// select mailing function
function selectMailing(mailing) {
    const body = {
        type: 'select_mailing',
        mailing: mailing
    };
    createPost(body, updateMessager);
}

// update mailing function
function updateMailing(mailing) {
    const body = {
        type: 'update_mailing',
        mailing: mailing
    };
    createPost(body, updateSelector);
}

// add message function
function deleteMailing(mailing) {
    const body = {
        type: 'delete_mailing',
        mailing: mailing
    };
    createPost(body, updateSelector);
}

//#endregion

//#region selector


// add mailing button
inputMailingName.addEventListener("keyup", function(event) {
    if (event.key === "Enter") {
        if (inputMailingName.value.trim() === '') {
            alert( "Название должно вдохновлять" );
            return;
        }

        const body = {
            type: 'add_mailing',
            mailing_name: inputMailingName.value.trim()
        };
        createPost(body, updateSelector);

        inputMailingName.value = '';
    }
});


// selector initialization
function initSelector() {
    selector.innerHTML = '';
}


// update selector function
function updateSelector(response) {

    print("selector upadtated", response);
    if (!('mailings' in response && 'exeError' in response)) {
        console.log("Error: wrong response format");
        return;
    }

    if (response.exeError === 'existing name')
        alert("Name is already existed");

    selector.innerHTML = '';

    const fragment = document.createDocumentFragment();
    const mailings = response.mailings;
    mailings.forEach(mailing => {
        const item = createDiv('roller__item');
        const tag = createDiv('tag', 'mailing');
        
        const nameItem = createDiv("clickable_text", "item");
        nameItem.innerText = mailing.name;

        const inputItem = document.createElement('input');
        inputItem.classList.add('checkbox', "item");
        inputItem.type = 'checkbox';
        inputItem.checked = mailing.is_active;
        inputItem.addEventListener("change", () => {
            mailing.is_active = inputItem.checked;
            updateMailing(mailing);
        });

        const buttonSelect = createDiv("button", "arrows", "item");
        buttonSelect.addEventListener('click', () => {
            selectMailing(mailing);
        });

        const buttonDelete = createDiv("button", "cross", "item");
        buttonDelete.addEventListener('click', () => {
            if (confirm(`Delete '${mailing.name}' mailing?`))
                deleteMailing(mailing);
        });

        tag.append(nameItem);
        tag.append(inputItem);
        tag.append(buttonSelect);
        tag.append(buttonDelete);
        item.append(tag);
        fragment.appendChild(item);
    });

    selector.appendChild(fragment);

    selector.scrollTop = selector.scrollHeight;
}


//#endregion

//#region messager



// messager initialization
function initMessager() {
    messager.innerHTML = '';
    currentMailingName.innerText = 'Not chosen';
}


// update messager function
function updateMessager(response) {
    if (!('current_mailing' in response && 'messages' in response &&
    'exeError' in response)) {
        console.log("Error: wrong response format");
        console.log(response);

        return;
    }

    if (response.exeError === 'existing name')
        alert("Name is already existed");


    currentMailingName.innerText = response.current_mailing.name;
    selectedMailing = response.current_mailing;
    messager.innerHTML = '';

    const fragment = document.createDocumentFragment();
    const messages = response.messages;
    messages.forEach(msg => {
        const item = createDiv('roller__item');
        const tagItem = createDiv('tag', 'mailingmsg');
        const nameItem = createDiv('clickable_text', 'item');
        nameItem.innerText = msg.name;

        nameItem.addEventListener('click', () => {
            quickCoverClosingAnimation(() => {
                selectedMessage = msg;
                openEditor();
            });
        });

        const inputItem = document.createElement('input');
        inputItem.classList.add('checkbox', "item");
        inputItem.type = 'checkbox';
        inputItem.checked = msg.is_active;
        inputItem.addEventListener("change", () => {
            msg.is_active = inputItem.checked;
            updateMessage(msg);
        });

        const button1Item = createDiv("button", "arrows", 'item');
        button1Item.addEventListener('click', () => {
            sendMessage(msg);
        });

        const button2Item = createDiv("button", "cross", 'item');
        button2Item.addEventListener('click', () => {
            deleteMessage(msg);
        })

        tagItem.append(nameItem);
        tagItem.append(inputItem);
        tagItem.append(button1Item);
        tagItem.append(button2Item);
        item.append(tagItem);
        fragment.appendChild(item);
    });

    messager.appendChild(fragment);
}



//#endregion

//#region start point

/* Global update */
document.addEventListener('DOMContentLoaded', () => {
    const body = {
        type: 'mailing_update',
    };
    console.log("Loaded1");
    initSelector();
    initMessager();

    createPost(body, (response)=>{
        updateSelector(response);
    });


    selectedMessage = null;
    selectedMailing = null;

    //checkForSend();
});

//#endregion
