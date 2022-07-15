/**********
 * Imports
 **********/

 import {setCSS, createDiv, createPost, print} from "./nd_utils.js";
 import {longCoverClosingAnimation} from "./nd_animations.js";

 /* end of 'imports.js' block */


 /* end of 'imports.js' block */
 
function checkPasswords(password) {
    var s_letters = "qwertyuiopasdfghjklzxcvbnm"; // Буквы в нижнем регистре
    var b_letters = "QWERTYUIOPLKJHGFDSAZXCVBNM"; // Буквы в верхнем регистре
    var digits = "0123456789"; // Цифры
    var specials = "!@#$%^&*()_-+=\|/.,:;[]{}"; // Спецсимволы
    var is_s = false; // Есть ли в пароле буквы в нижнем регистре
    var is_b = false; // Есть ли в пароле буквы в верхнем регистре
    var is_d = false; // Есть ли в пароле цифры
    var is_sp = false; // Есть ли в пароле спецсимволы
    for (var i = 0; i < password.length; i++) {
      /* Проверяем каждый символ пароля на принадлежность к тому или иному типу */
      if (!is_s && s_letters.indexOf(password[i]) != -1) is_s = true;
      else if (!is_b && b_letters.indexOf(password[i]) != -1) is_b = true;
      else if (!is_d && digits.indexOf(password[i]) != -1) is_d = true;
      else if (!is_sp && specials.indexOf(password[i]) != -1) is_sp = true;
    }
    var rating = 0;
    var text = "";
    if (is_s) rating++; // Если в пароле есть символы в нижнем регистре, то увеличиваем рейтинг сложности
    if (is_b) rating++; // Если в пароле есть символы в верхнем регистре, то увеличиваем рейтинг сложности
    if (is_d) rating++; // Если в пароле есть цифры, то увеличиваем рейтинг сложности
    if (is_sp) rating++; // Если в пароле есть спецсимволы, то увеличиваем рейтинг сложности
    /* Далее идёт анализ длины пароля и полученного рейтинга, и на основании этого готовится текстовое описание сложности пароля */
    if (password.length < 6 && rating < 3) text = "Простой";
    else if (password.length < 6 && rating >= 3) text = "Средний";
    else if (password.length >= 8 && rating < 3) text = "Средний";
    else if (password.length >= 8 && rating >= 3) text = "Сложный";
    else if (password.length >= 6 && rating == 1) text = "Простой";
    else if (password.length >= 6 && rating > 1 && rating < 4) text = "Средний";
    else if (password.length >= 6 && rating == 4) text = "Сложный";
    return false; // Форму не отправляем
  }



/*************
 * Sing in
 *************/

const singInPage = document.getElementById('singin_page');
const singInName = document.getElementById('singin_name');
const singInPassword = document.getElementById('singin_password');

const singInButton = document.getElementById('singin_button');

const gotoSingUpButton = document.getElementById('goto_singup_button');


singInButton.addEventListener('click', () => {

    
    if (singInName.value.trim() === '' ||
        singInPassword.value.trim() === '') {

        alert( "Заполните все поля" );       
        return;
    }

       
    const body = {
        type: 'singin',
        name: singInName.value,
        password: singInPassword.value,
    };

    createPost(body, fillingSingInResponse);

});



function fillingSingInResponse(response) {

    if (!response.is_name_exists) {
        alert('There is no admin with this name');
        return;
    }

    if (!response.is_confirmed_self) {
        alert('Confirm your email, please');
        return;
    }

    if (!response.is_confirmed_boss) {
        alert('BOSS didnt confirm request yet');
        return;
    }

    if (!response.is_correct_password) {
        alert('Incorrect password');
        return;
    }

    longCoverClosingAnimation(() => {
        singInPage.classList.add('close');
        singInName.value = '';
        singInPassword.value = '';
    });

}


gotoSingUpButton.addEventListener('click', () => {
    quickCoverClosingAnimation(() => {
        singInName.value = '';
        singInPassword.value = '';
        singInPage.classList.add('close');
        singUpPage.classList.remove('close');
    })
});




/*************
 * Sing up
 *************/


const singUpPage = document.getElementById('singup_page');

const signUpButton = document.getElementById('singup_button');
const singUpName = document.getElementById('singup_name');
const singUpPassword = document.getElementById('singup_password');
const singUpPassword2 = document.getElementById('singup_password_2');
const singUpEmail = document.getElementById('singup_email');
 
 
signUpButton.addEventListener('click', () => {

    if (singUpName.value.trim() === '' ||
        singUpPassword.value.trim() === '' ||
        singUpPassword2.value.trim() === '' ||
        singUpEmail.value.trim() === '') {

        alert( "Заполните все поля" );       
        return;
    }

   
    if (singUpPassword.value.trim() !== singUpPassword2.value.trim()) {
        alert( "Пароли не совпадают" );       
        return;
    }

    /*
    if (checkPasswords(singUpPassword.value) === false) {
        alert( "Пароль слишком простой" );       
        return;
    }*/

    
    const body = {
        type: 'singup',
        name: singUpName.value,
        password: singUpPassword.value,
        email: singUpEmail.value
    };
    createPost(body, fillingSingUpFormResponse);
});


 function fillingSingUpFormResponse(response) {

    if (!response.is_unique_email) {
        alert('This email is already singed up');
        return;
    }

    if (!response.is_unique_name) {
        alert('This name was already taken');
        return;
    }

    if (!response.is_correct_email) {
        alert('Incorrect email');
        return;
    }

    alert('Check your mailbox. We sent you confirmation email.')

    
    quickCoverClosingAnimation(() => {
        singUpName.value = '';
        singUpEmail.value = '';
        singUpPassword.value = '';
        singUpPassword2.value = '';
        singInPage.classList.remove('close');
        singUpPage.classList.add('close');
    })

}
 


document.addEventListener('DOMContentLoaded', ()=>{
    console.log('myaw');
})