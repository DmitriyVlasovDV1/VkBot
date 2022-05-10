const inputMailingName = document.getElementById('input_mailing_name');
const currentMailingName = document.getElementById('current_mailing_name');
const selector = document.getElementById('selector');

const messager = document.getElementById('messager');

const editorMessageName = document.getElementById('editor_message_name');
const editorMessageText = document.getElementById('editor_message_text');
const editorMessageFlag = document.getElementById('editor_message_flag');
const editorMessageTime = document.getElementById('editor_message_time');

const buttonAddMessage = document.getElementById('add_message_button');
const buttonEditorSave = document.getElementById("button_editor_save");
const buttonEditorClose = document.getElementById("button_editor_close");
const editorWindow = document.getElementById("editor_window");


let selectedMailing = null;
let selectedMessage = null;



// create html block function
function createDiv()
{
    const res = document.createElement('div');

    for (var i = 0; i < arguments.length; i++) {
        res.classList.add(arguments[i]);
    }

    return res;
}

// creating post requestion function
function createPost(body, cb=null) {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://127.0.0.1:5000/mailing');
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');

    xhr.addEventListener('load', () => {
        const response = JSON.parse(xhr.response);
        if (cb != null)
            cb(response);
    })
    xhr.addEventListener('error', () => {
        console.log('ERROR!!!');
    });

    xhr.send(JSON.stringify(body));
} // end of createPost function

// button add message
buttonAddMessage.addEventListener('click', () => {
    if (selectedMailing !== null)
        openEditor();
});

// close popup window editing message
buttonEditorClose.addEventListener('click', () => {
    closeEditor();
});

buttonEditorSave.addEventListener('click', () => {
    if (editMessage())
        closeEditor();
});

// Open and close editor
function openEditor() {
    editorWindow.classList.remove("popup_close");

    if (selectedMessage === null) {
        editorMessageName.value = '';
        editorMessageText.value = '';
        editorMessageFlag.value = false;
        editorMessageTime.value = '';
    } else {
        editorMessageName.value = selectedMessage.name;
        editorMessageText.value = selectedMessage.text;
        editorMessageFlag.value = selectedMessage.is_active;
        editorMessageTime.value = new Date(selectedMessage.time).toISOString().substring(0, 19);
    }


}

function closeEditor() {
    editorWindow.classList.add("popup_close");
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
        time = null
        if (editorMessageTime.value !== '')
            time = editorMessageTime.value.slice(0, 19).replace('T', ' ') + ':00'

        message = {
            name: editorMessageName.value,
            text: editorMessageText.value,
            is_active: editorMessageFlag.value,
            time: time
        }

        addMessage(message);
    } else {
        time = null
        if (editorMessageTime.value !== '')
            time = editorMessageTime.value.slice(0, 19).replace('T', ' ') + ':00'
        message = {
            id: selectedMessage.id,
            name: editorMessageName.value,
            text: editorMessageText.value,
            is_active: editorMessageFlag.value,
            time: time
        }
        updateMessage(message);
    }

    return true;
}

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


// send message
function sendMessage(msg) {
    const body = {
        type: 'send_message',
        message: msg
    }
    createPost(body);
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


// delete mailig function
function deleteMailing(mailing) {
    const body = {
        type: 'delete_mailing',
        mailing: mailing
    };
    createPost(body, updateSelector);
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

function updateMessage(msg) {
    const body = {
        type: 'update_message',
        message: msg
    };
    createPost(body, updateMessager);
}


// update selector function
function updateSelector(response) {
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
        const tag = createDiv('tag_mailing');
        
        const nameItem = createDiv("clickable_text", "tag_mailing_item");
        nameItem.innerText = mailing.name;
        nameItem.addEventListener('click', () => {
            selectMailing(mailing);
        });

        const inputItem = document.createElement('input');
        inputItem.classList.add('checkbox', "tag_mailing_item");
        inputItem.type = 'checkbox';
        inputItem.checked = mailing.is_active;
        inputItem.addEventListener("change", () => {
            mailing.is_active = inputItem.checked;
            updateMailing(mailing);
        });

        const buttonItem = createDiv("icon", "icon_delete", "tag_mailing_item");
        buttonItem.addEventListener('click', () => {
            if (confirm(`Delete '${mailing.name}' mailing?`))
                deleteMailing(mailing);
        });

        tag.append(nameItem);
        tag.append(inputItem);
        tag.append(buttonItem);
        item.append(tag);
        fragment.appendChild(item);
    });

    selector.appendChild(fragment);

    selector.scrollTop = selector.scrollHeight;
}

// update selector function
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
        const tagItem = createDiv('tag_mailing', 'tag_mailingmsg');
        const nameItem = createDiv('clickable_text', 'tag_mailingmsg_item');
        nameItem.innerText = msg.name;

        nameItem.addEventListener('click', () => {
            selectedMessage = msg;
            openEditor();
        });

        const inputItem = document.createElement('input');
        inputItem.classList.add('checkbox', "tag_mailingmsg_item");
        inputItem.type = 'checkbox';
        inputItem.checked = msg.is_active;
        inputItem.addEventListener("change", () => {
            msg.is_active = inputItem.checked;
            updateMessage(msg);
        });

        const button1Item = createDiv("icon", "icon_plus", 'tag_mailingmsg_item');
        button1Item.addEventListener('click', () => {
            sendMessage(msg);
        });

        const button2Item = createDiv("icon", "icon_delete", 'tag_mailingmsg_item');
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


function initMessager() {
    messager.innerHTML = '';
    currentMailingName.innerText = 'Not chosen';
}


/* Global update */
document.addEventListener('DOMContentLoaded', () => {
    const body = {
        type: 'update',
    };
    console.log("Loaded");
    createPost(body, (response)=>{
        updateSelector(response);
    });

    initMessager();

    selectedMessage = null;
    selectedMailing = null;

    //checkForSend();
});
