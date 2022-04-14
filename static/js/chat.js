const buttonMessage = document.getElementById('button_message');
const butttonAddUser = document.getElementById('button_add_user')
const butttonDeleteUser = document.getElementById('button_delete_user')
const inputUserName = document.getElementById('input_user_name')
const inputMessage = document.getElementById('textarea_message');
const selector = document.getElementById('selector');
const messager = document.getElementById('messager');
const textCurrentUser = document.getElementById('text_current_user');

function createPost(body, cb={}) {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://127.0.0.1:5000/');
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');

    xhr.addEventListener('load', () => {
        const response = JSON.parse(xhr.response);
        cb(response);
    })
    xhr.addEventListener('error', () => {
        console.log('ERROR!!!');
    });
    
    xhr.send(JSON.stringify(body));
}



/* Selector */

butttonAddUser.addEventListener('click', () => {
    if (inputUserName.value === '')
        return;

    const body = {
        type: 'add_user',
        user_name: inputUserName.value
    };
    inputUserName.value = '';
    createPost(body, updateSelector);
});

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
        const item = document.createElement('div');
        item.classList.add('user');

        const name = document.createElement('div');
        name.classList.add('user__name');
        name.innerHTML = user.name;

        const icon1 = document.createElement('div');
        icon1.classList.add('box__icon');
        icon1.classList.add('icon_plus');
        icon1.addEventListener('click', ()=>{selectUser(user.name)});

        const icon2 = document.createElement('div');
        icon2.classList.add('box__icon');
        icon2.classList.add('icon_delete');
        icon2.addEventListener('click', ()=>{deleteUser(user.name)});

        item.append(name, icon1, icon2);
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

buttonMessage.addEventListener('click', () => {
    sendMessage();
});


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
        const item = document.createElement('div');
        const time = document.createElement('div');
        const date = String(msg.date);
        parsedDate = date.split(" ");
        item.innerText = msg.text;
        time.innerText = parsedDate[4] + " " + parsedDate[1] + " " + parsedDate[2];
        console.log(date.split(" "));
        console.log(typeof date);
        item.classList.add('messager__message');
        time.classList.add('messager__time');
        if (msg.type == 'bot') {
            item.classList.add('messager__message_left');
            time.classList.add('messager__time_left');
        }
        else if (msg.type == 'user') {
            item.classList.add('messager__message_right');
            time.classList.add('messager__time_right');
        }
        fragment.appendChild(item);
        fragment.appendChild(time);
    });

    messager.appendChild(fragment);
    messager.scrollTop = messager.scrollHeight;
    console.dir(messager);
}




/* Global update */

document.addEventListener('DOMContentLoaded', () => {
    const body = {
        type: 'update',
    };
    console.log("Loaded");
    createPost(body, (response)=>{
        updateSelector(response);
        updateMessager(response);
    });

    checkForSend();
});





