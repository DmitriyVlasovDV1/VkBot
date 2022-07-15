/********
 * Utils
 ********/

// create html block function
export function createDiv()
{
    const res = document.createElement('div');

    for (var i = 0; i < arguments.length; i++) {
        res.classList.add(arguments[i]);
    }

    return res;
}

// set css property
export function setCSS(el, property, value) {
    el.style[property] = value;
}

// for python fans
export function print() {
    for (let i = 0; i < arguments.length; i++)
    console.log(arguments[i]);
}


// creation post request
export function createPost(body, cb={}) {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://127.0.0.1:5000/');
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');

    xhr.addEventListener('load', () => {

        try {
            const response = JSON.parse(xhr.response);
            cb(response);
        } catch(e) {
            print("Cant parse: ", xhr.response);
        }
    })
    xhr.addEventListener('error', () => {
        console.log('ERROR!!!');
    });
    
    xhr.send(JSON.stringify(body));
}


/* end of 'nd_utils.js' file */




