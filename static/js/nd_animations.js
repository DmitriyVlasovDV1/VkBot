//const contentBlock = document.getElementById("content");
//const coverLeftBlock = document.getElementById("cover_left");
//const coverRightBlock = document.getElementById("cover_right");


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


/**********
 * Slider
 **********/

// elements
const slider = document.getElementById("slider");
const slides = document.querySelectorAll(".slider__slide");


// glabal varialbes
const changingDiffY = 250;
const slidesAnimationDuration = 0.5;
let curSlide;
let startY;
let diffY;
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
}

// show current slide
function showCurrentSlide(instant) {

    // is animation instant
    if (!instant) {
        print('animate')

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

    dragSlides();
}

// start dragging
function dragStart(e) {
    if (isSlidesAnimating)
        return;

    isDragging = true;
    diffY = 0;
    startY = e.pageY;
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
}

// change number of current slide
function changeSlide(newSlide) {

    newSlide = Math.min(slides.length - 1, newSlide);
    newSlide = Math.max(0, newSlide);
    newSlide %= slides.length;

    curSlide = newSlide;
}

// drag start
slider.addEventListener("mousedown", dragStart);

// drag end
document.addEventListener("mouseup", dragEnd);



/*************
 * Kuski kala
 *************/

// constants
const stripHeight = 20;

class Point {
    constructor(x, y, z) {
      this.x = x;
      this.y = y;
      this.z = z;
    }


    static distance(a, b) {
      const dx = a.x - b.x;
      const dy = a.y - b.y;

      return Math.hypot(dx, dy);
    }

    static add() {
        let res = new Point(0, 0, 0);
        for (let i = 0; i < arguments.length; i++) {
            res.x += arguments[i].x;
            res.y += arguments[i].y;
            res.z += arguments[i].z;
        }
        return res;
    }

    len() {
        return Math.hypot(x, y, z);
    }

    normalize() {
        let len = len();
        if (len === 0)
            return;
        this.x /= len;
        this.y /= len;
        this.z /= len;
    }

    mul(n) {
        this.x *= n;
        this.y *= n;
        this.z *= n;
        return this;
    }
}


let perlin = new Array();

function generatePerlinNoise(nofNodes, nofOct) {

    for (let oct = 0; oct < nofOct; oct++) {
        let koef = Math.pow(2, oct);

        perlin.push(new Array());
        for (let i = 0; i < nofNodes * koef; i++) {
            perlin[oct].push(Math.random() * 6 - 3);
        }
    }
}
    
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


function print() {
    for (let i = 0; i < arguments.length; i++)
    console.log(arguments[i]);
}


//setInterval(draw, 10);

function step(n) {
    tmp = Math.abs(n);
    tmp = Math.max(tmp, 0);
    tmp = Math.min(tmp, 1);
    return Math.pow(tmp, 1/2);
}

generatePerlinNoise(35, 5);

let cur = 0;
let sum = 0;
let num = 0;

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


function draw() {
    cur += 0.4;

    let start = 4;
    let end = 38;
    for (let i = start; i < end; i++) {
        let k = getPerlinNoise(cur * 0.047 + i * 0.13, 150);
        let k1 = getPerlinNoise(cur * 0.047 + i * 0.13, 200);
        let k2 = getPerlinNoise(cur * 0.047 + i * 0.13 + 43221.646, 200);

        let t = (i - start) / (end - start);
        coverRightBlock.children[i].style.width = (k * 45 + 180) * (-Math.pow(2 * t - 1, 4) + 1);

        let r = 150 + k * 650;
        let g = 200 - k * 200;
        let b = 200 + k * k * 200;


        

        sum += Math.abs(k1);
        num += 1;
        print(sum / num);

        /*c1 = new Point(255, 222, 84);
        c2 = new Point(252, 80, 66);
        c3 = new Point(90, 83, 201);
        c4 = new Point(182, 57, 153);*/
/*
        c1 = new Point(70,130,195);
        c2 = new Point(95,155,220);
        c3 = new Point(255, 255, 255);
        c4 = new Point(45,105,170);
*/

        c1 = new Point(3,155,229);
        c2 = new Point(3,155,229);
        c3 = new Point(3,155,229);
        c4 = new Point(255, 255, 255);


        //RGB (70,130,195)
        //(95,155,220)
        //(255, 255, 255)
        //(45,105,170)


        let tmp1 = 0.37;
        let tmp2 = 1;
        let t1 = Math.sign(k1) * step(k1 / tmp1) * 0.5 + 0.5;
        let t2 = Math.sign(k2) * step(k2 / tmp1) * 0.5 + 0.5;

        let c5 = Point.add(c4.mul(t1), c2.mul(1 - t1));
        let c6 = Point.add(c3.mul(t1), c1.mul(1 - t1));

        let c = Point.add(c5.mul(t2), c6.mul(1 - t2));



        coverRightBlock.children[i].style['background-color'] = `rgb(${c.x}, ${c.y}, ${c.z})`;
    }
}; 



/**************
 * Start point
 **************/

document.addEventListener('DOMContentLoaded', () => {
    initSlider();
});

