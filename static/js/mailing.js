const inputMailingName = document.getElementById('input_mailing_name');
const buttonAddMailing = document.getElementById('button_add_mailing');
const selector = document.getElementById('selector');
const messanger = document.getElementById('messager')
const textCurrentMailing = document.getElementById('text_current_mailing')
const buttonAddMessage = document.getElementById('add_message_button')

const textareas =  Array.from(document.getElementsByTagName('textarea'));

textareas.forEach(txt => {
    txt.addEventListener('keydown', resize);
    });

function resize() {
  var el = this;
  setTimeout(function() {
    el.style.height = 'auto';
    el.style.height = el.scrollHeight;
  }, 1);
}


function createPost(body, cb={}) {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://127.0.0.1:5000/mailing');
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
buttonAddMailing.addEventListener('click', () => {
    console.log('hello');
    if (inputMailingName.value === '')
        return;

    const body = {
        type: 'add_mailing',
        mailing_name: inputMailingName.value
    };
    inputMailingName.value = '';
    createPost(body, updateSelector);
});

buttonAddMessage.addEventListener('click', () => {
    const body = {
        type: 'add_message'
    };
    createPost(body, updateMessager);
})

function deleteMailing(mailing) {
    const body = {
        type: 'delete_mailing',
        mailing: mailing
    };
    createPost(body, updateSelector);
}

function selectMailing(mailing) {
    const body = {
        type: 'select_mailing',
        mailing: mailing
    };
    createPost(body, updateMessager);
}

function updateMailing(mailing) {
    const body = {
        type: 'update_mailing',
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


function updateSelector(response) {
    if (!response.mailings) {
        console.log("Error: wrong response format");
        return;
    }

    selector.innerHTML = ''

    const fragment = document.createDocumentFragment();
    const mailings = response.mailings;
    mailings.forEach(mailing => {
        const item = document.createElement('div');
        item.classList.add('mailing');

        const name = document.createElement('div');
        name.classList.add('mailing__name');
        name.innerHTML = mailing.name;

        const checkbox = document.createElement('input');
        checkbox.classList.add('checkbox');
        checkbox.type = 'checkbox';
        checkbox.checked = mailing.is_active;
        checkbox.addEventListener('click', ()=>{
            mailing.is_active = checkbox.checked;
            updateMailing(mailing);
        });

        const icon1 = document.createElement('div');
        icon1.classList.add('box__icon');
        icon1.classList.add('icon_plus');
        icon1.addEventListener('click', ()=>{selectMailing(mailing)});

        const icon2 = document.createElement('div');
        icon2.classList.add('box__icon');
        icon2.classList.add('icon_delete');
        icon2.addEventListener('click', ()=>{deleteMailing(mailing)});

        item.append(name, checkbox, icon1, icon2);
        fragment.appendChild(item);
    });

    selector.appendChild(fragment);

    selector.scrollTop = selector.scrollHeight;
}


function updateMessager(response) {
    if (!response.current_mailing) {
        console.log("Error: wrong response format");
        return;
    }

    messager.innerHTML = '';

    if (Object.keys(response.current_mailing).length === 0) {
        textCurrentMailing.innerHTML = 'Select mailing';
        return;
    }

    textCurrentMailing.innerHTML = response.current_mailing.name;

    const fragment = document.createDocumentFragment();
    const messages = response.messages;
    messages.forEach(msg => {
        const item = document.createElement('textarea');
        item.value = msg.text;

        setTimeout(function() {
            item.style.height = 'auto';
            item.style.height = item.scrollHeight;
          }, 0.5);

        item.style.height = 'auto';
        item.style.height = item.scrollHeight;

        item.classList.add('messager__message', 'messager__message_delayed');
        if (msg.is_active)
            item.style['border-color'] = '#0087DD';
        else
            item.style['border-color'] = 'rgb(94, 205, 50)'

        const item2 = document.createElement('div');
        item2.classList.add('messager__setting');
        const inputTime = document.createElement('input');
        inputTime.type ='datetime-local';
        const inputActivity = document.createElement('input');
        inputActivity.type ='checkbox';
        inputActivity.classList.add('checkbox');
        inputActivity.checked = msg.is_active;

        const plusButton = document.createElement('div');
        plusButton.classList.add('box__icon', 'icon_plus');
        const deleteButton = document.createElement('div');
        deleteButton.classList.add('box__icon', 'icon_delete');
        
        item2.append(inputTime, inputActivity, plusButton, deleteButton);

        fragment.appendChild(item);
        fragment.appendChild(item2);

        item.addEventListener('keydown', resize);
        item.addEventListener('keydown', ()=>{
            inputActivity.disabled = true;

            msg.is_active = false;
            inputActivity.checked = false;
            item.style['border-color'] = 'red';
        });
        inputActivity.addEventListener('click', ()=>{
            msg.is_active = inputActivity.checked;
            updateMessage(msg);
        })
        plusButton.addEventListener('click', ()=>{
            msg.text = item.value;
            console.log(item.value);
            updateMessage(msg);
        })
    });
    messager.appendChild(fragment);

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

    checkForSend();
});
