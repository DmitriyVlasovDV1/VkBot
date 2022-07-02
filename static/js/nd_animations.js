/*********
 * Utils
 *********/

// create html block function
function createDiv()
{
    const res = document.createElement('div');

    for (var i = 0; i < arguments.length; i++) {
        res.classList.add(arguments[i]);
    }

    return res;
}

// set css property
function setCSS(el, property, value) {
    el.style[property] = value;
}

// for python fans
function print() {
    for (let i = 0; i < arguments.length; i++)
    console.log(arguments[i]);
}


/**********
 * Slider
 **********/

// elements
const slider = document.getElementById("slider");
const slides = document.querySelectorAll(".slider__slide");
const progressBar = document.getElementById("progress_bar");


// glabal varialbes
const changingDiffY = 250;
const slidesAnimationDuration = 0.5;
let curSlide;
let startY;
let startX;
let diffY = 0;
let diffX = 0;
let isSlidesAnimating = false;
let isDragging = false;



// initialization
function initSlider() {
    curSlide = 0;

    // set slides position
    let h = slider.offsetHeight;
    for (let i = 0; i < slides.length; i++) {
        setCSS(slides[i], 'top', `${i * h}px`);
    }

    showCurrentSlide(true);

    for (let i = 0; i < slides.length; i++) {
        progressBar.children[i].addEventListener('click', () => {
            changeSlide(i);
            showCurrentSlide();
        })
    }
}

// show current slide
function showCurrentSlide(instant) {

    // is animation instant
    if (!instant) {

        isSlidesAnimating = true;

        slides.forEach((el) => {
            el.classList.add('animate');
        });

        setTimeout(() => {
            isSlidesAnimating = false;

            slides.forEach((el) => {
                el.classList.remove('animate');
            });

            }, slidesAnimationDuration * 1000);

    }

    // set positions
    let h = slider.offsetHeight;
    for (let i = 0; i < slides.length; i++) {
        setCSS(slides[i], 'transform', `translate(0px, ${-curSlide * h}px)`);
    }

}


// drag slides
function dragSlides() {
    let h = slider.offsetHeight;
    for (let i = 0; i < slides.length; i++) {
        setCSS(slides[i], 'transform', `translate(0px, ${-curSlide * h + diffY * 0.5}px)`);
    }
}

// drag response
function dragResponse(e) {
    if (isSlidesAnimating)
        return;

    diffY = e.pageY - startY;
    diffX = e.pageX - startX;

    dragSlides();
    dragBalls();
}

// start dragging
function dragStart(e) {
    if (isSlidesAnimating)
        return;

    isDragging = true;
    diffY = 0;
    diffX = 0;
    startY = e.pageY;
    startX = e.pageX;
    document.addEventListener("mousemove", dragResponse);
}

// end dragging
function dragEnd(e) {
    if (isDragging === false) {
        return;
    }

    document.removeEventListener("mousemove", dragResponse);

    if (diffY < -changingDiffY) {
        changeSlide(curSlide + 1);
    } else if (diffY > changingDiffY) {
        changeSlide(curSlide - 1);
    }

    showCurrentSlide(diffY === 0);
    isDragging = false;
    diffY = 0;
    diffX = 0;

    returnBalls();
}

// change number of current slide
function changeSlide(newSlide) {

    newSlide = Math.min(slides.length - 1, newSlide);
    newSlide = Math.max(0, newSlide);
    newSlide %= slides.length;

    curSlide = newSlide;
    for (let i = 0; i < slides.length; i++) {
        if (i == curSlide)
            progressBar.children[i].classList.add('active');
        else
            progressBar.children[i].classList.remove('active');
    }
}

// drag start
slider.addEventListener("mousedown", dragStart);

// drag end
document.addEventListener("mouseup", dragEnd);

function zoom(event) {
    event.preventDefault();
  
    scale += event.deltaY * -0.01;
  
    // Restrict scale
    scale = Math.min(Math.max(.125, scale), 4);
  
    // Apply scale transform
    el.style.transform = `scale(${scale})`;
  }


function wheelResponse(event) {
    return
    if (event.target !== slider) {
        print(event.target);
        return;
    }

    if (isSlidesAnimating)
        return;

    event.preventDefault();

    if (event.deltaY > 0) {
        changeSlide(curSlide + 1);
        showCurrentSlide();
    }
    else if (event.deltaY < -0) {
        changeSlide(curSlide - 1);
        showCurrentSlide();
    }
}

slider.addEventListener("wheel", wheelResponse);

/***************
 * Perlin noise
 ***************/

// constants
const maxTg = 3;
const nofNodes = 100;
const nofOct = 1;
let perlin = new Array();


// generate noise
function generatePerlinNoise(nofNodes, nofOct) {
    for (let oct = 0; oct < nofOct; oct++) {
        let koef = Math.pow(2, oct);

        perlin.push(new Array());
        for (let i = 0; i < nofNodes * koef; i++) {
            perlin[oct].push(Math.random() * maxTg * 2 - maxTg);
        }
    }
}

// get value from perlin noise
function getPerlinNoise(units, unitsInCycle)
{
    let res = 0;

    let cycleUnits = units % unitsInCycle;
    for (let oct = 0; oct < perlin.length; oct++) {
        let koef = Math.pow(2, oct);
        let ind1 = Math.floor(cycleUnits / unitsInCycle * perlin[oct].length);
        let ind2 = (ind1 + 1) % perlin[oct].length;
        
        let unitsInSeg = unitsInCycle / perlin[oct].length;
        
        
        let t = cycleUnits / unitsInSeg - ind1;
        
        let a = perlin[oct][ind1];
        let b = perlin[oct][ind2];
        
        let y = 2 * (a - b) * Math.pow(t, 4) - (3 * a - 5 * b) * Math.pow(t, 3) - 3 * b * Math.pow(t, 2) + a * t;
        res += y / koef;
    }
    return res;
}

/********************
 * Perlin animation
 ********************/

/*********
 * Balls
 *********/

const ballsDist = [2, 1, 1.5, 3];
const ballSize = 200;
const ballAnimationTime = 0.6;

const balls = document.querySelectorAll(".ball");

function initBalls() {
    for (let i = 0; i < balls.length; i++)  {
        setCSS(balls[i], 'height', `${ballSize / ballsDist[i]}px`);
        setCSS(balls[i], 'width', `${ballSize / ballsDist[i]}px`);
    }
}

function dragBalls() {
    for (let i = 0; i < balls.length; i++)  {
        setCSS(balls[i], 'transform', `translate(${diffX * 0.08 / ballsDist[i]}px, ${diffY * 0.08 / ballsDist[i]}px)`);
    }
}

function returnBalls() {
    for (let i = 0; i < balls.length; i++)  {
        balls[i].classList.add("animate");
        setCSS(balls[i], 'transform', `translate(${0}px, ${0}px)`);

        setTimeout(() => {
            isSlidesAnimating = false;

            balls.forEach((el) => {
                el.classList.remove('animate');
            });

            }, ballAnimationTime * 1000);
    }
}


/**********
 * Stripes
 **********/

const unitsPerSec = 0.1;

const coverRight = document.getElementById("cover_right");
const coverLeft = document.getElementById("cover_left");
const cover = document.getElementById("cover");

const account = document.getElementById("account");
const closePopup = document.getElementById("button_editor_close");
const popup = document.getElementById("editor_window");


account.addEventListener("click", () => {
    quickCoverClosingAnimation();
});
/*

closePopup.addEventListener("click", () => {
    closeCover(() => {popup.classList.add("close")});
});*/


const closingCloseTime = 0.5;
const closingOpenTime = 0.3;
const closingWaitTime = 0.5;
const dltClose = 0.2;

const numOfStripes = 20;
const stride = 0.05;
const unitsInCycle = 100;

const baseW = 60;
const dltW = 20;

let stripesRight = [];
let stripesLeft = [];
let isCoverClosed = false;

// initializatioin
function initStripes() {
    let h = cover.offsetHeight / numOfStripes;

    for (let i = 0; i < numOfStripes; i++) {
        let strip = createDiv('cover__strip');
        setCSS(strip, 'height', `${h}px`);
        strip.classList.add('open');
        strip.classList.add('left');

        //setCSS(strip, 'width', `0px`);

        coverLeft.appendChild(strip);

        stripesLeft.push(strip);
    }

    for (let i = 0; i < numOfStripes; i++) {
        let strip = createDiv('cover__strip');
        setCSS(strip, 'height', `${h}px`);
        strip.classList.add('open');
        strip.classList.add('right');

        coverRight.appendChild(strip);

        stripesRight.push(strip);
    }

}


function closeCover() {

    for (let i = 0; i < numOfStripes; i++) {
        coverRight.children[i].classList.remove('open');
        coverLeft.children[i].classList.remove('open');
        coverRight.children[i].classList.add('open_to_close');
        coverLeft.children[i].classList.add('open_to_close');
        coverRight.children[i].classList.add('close');
        coverLeft.children[i].classList.add('close');

        setCSS(coverRight.children[i], 'transition-delay', `${Math.random() * dltClose}s`);
        setCSS(coverLeft.children[i], 'transition-delay', `${Math.random() * dltClose}s`);
    }

}

function openCover() {

    for (let i = 0; i < numOfStripes; i++) {
        coverRight.children[i].classList.remove('close');
        coverLeft.children[i].classList.remove('close');
        coverRight.children[i].classList.add('close_to_open');
        coverLeft.children[i].classList.add('close_to_open');
        coverRight.children[i].classList.add('open');
        coverLeft.children[i].classList.add('open');
    }
}


function fixateCover() {
    for (let i = 0; i < numOfStripes; i++) {
        coverRight.children[i].classList.remove('close_to_open');
        coverLeft.children[i].classList.remove('close_to_open');
        coverRight.children[i].classList.remove('open_to_close');
        coverLeft.children[i].classList.remove('open_to_close');
    }
}



/**************
 * Start point
 **************/

 document.addEventListener('DOMContentLoaded', () => {
    initSlider();
    generatePerlinNoise(nofNodes, nofOct);
    initStripes()
    initBalls();
});




/**************
 * Animations
 **************/

function quickCoverClosingAnimation () {
    closeCover();
    isCoverClosed = true;
    print('p1:', isCoverClosed);
    setTimeout(fixateCover, (closingCloseTime + dltClose) * 1000);
    setTimeout(openCover, (closingCloseTime + closingWaitTime + dltClose) * 1000);
    setTimeout(fixateCover, (closingCloseTime + closingWaitTime + dltClose + closingOpenTime) * 1000);
    isCoverClosed = false;
}


/*****************
 * A pure kal
 *****************/


//  function step(n) {
//     tmp = Math.abs(n);
//     tmp = Math.max(tmp, 0);
//     tmp = Math.min(tmp, 1);
//     return Math.pow(tmp, 1/2);
// }
/*
    let numStripes = window.innerHeight / stripHeight;
    console.log(numStripes);
    for (let i = 0; i < numStripes; i++) {
        let strip = createDiv('cover__strip');
        strip.style.height = `${stripHeight}px`;
        coverLeftBlock.appendChild(strip);
    }

    for (let i = 0; i < numStripes; i++) {
        let strip = createDiv('cover__strip');
        strip.style.height = `${stripHeight}px`;
        coverRightBlock.appendChild(strip);
    }
*/

        // let k1 = getPerlinNoise(cur * 0.047 + i * 0.13, 200);
        // let k2 = getPerlinNoise(cur * 0.047 + i * 0.13 + 43221.646, 200);
        // // let r = 150 + k * 650;
        // let g = 200 - k * 200;
        // let b = 200 + k * k * 200;


        

        // sum += Math.abs(k1);
        // num += 1;
        // print(sum / num);

        /*c1 = new Point(255, 222, 84);
        c2 = new Point(252, 80, 66);
        c3 = new Point(90, 83, 201);
        c4 = new Point(182, 57, 153);*/

        // c1 = new Point(70,130,195);
        // c2 = new Point(95,155,220);
        // c3 = new Point(255, 255, 255);
        // c4 = new Point(45,105,170);


        // c1 = new Point(3,155,229);
        // c2 = new Point(3,155,229);
        // c3 = new Point(3,155,229);
        // c4 = new Point(255, 255, 255);


        //RGB (70,130,195)
        //(95,155,220)
        //(255, 255, 255)
        //(45,105,170)


        // let tmp1 = 0.37;
        // let tmp2 = 1;
        // let t1 = Math.sign(k1) * step(k1 / tmp1) * 0.5 + 0.5;
        // let t2 = Math.sign(k2) * step(k2 / tmp1) * 0.5 + 0.5;

        // let c5 = Point.add(c4.mul(t1), c2.mul(1 - t1));
        // let c6 = Point.add(c3.mul(t1), c1.mul(1 - t1));

        // let c = Point.add(c5.mul(t2), c6.mul(1 - t2));



        // coverRight.children[i].style['background-color'] = `rgb(${c.x}, ${c.y}, ${c.z})`;
//     }
// }; 







// class Point {
//     constructor(x, y, z) {
//       this.x = x;
//       this.y = y;
//       this.z = z;
//     }


//     static distance(a, b) {
//       const dx = a.x - b.x;
//       const dy = a.y - b.y;

//       return Math.hypot(dx, dy);
//     }

//     static add() {
//         let res = new Point(0, 0, 0);
//         for (let i = 0; i < arguments.length; i++) {
//             res.x += arguments[i].x;
//             res.y += arguments[i].y;
//             res.z += arguments[i].z;
//         }
//         return res;
//     }

//     len() {
//         return Math.hypot(x, y, z);
//     }

//     normalize() {
//         let len = len();
//         if (len === 0)
//             return;
//         this.x /= len;
//         this.y /= len;
//         this.z /= len;
//     }

//     mul(n) {
//         this.x *= n;
//         this.y *= n;
//         this.z *= n;
//         return this;
//     }
// }
