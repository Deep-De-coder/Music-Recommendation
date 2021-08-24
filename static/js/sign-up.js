const input1 = document.getElementById('ghost-input1');
const bubble1 = document.getElementById('ghost-bubble1');

const mouth1 = document.querySelector('.ghost__mouth');

input1.onkeydown = e => {
  if (e.keyCode == 13) {
    bubble1.innerText = e.target.value;
    e.target.value = '';

    // mouth chatter
    let i = 0;
    //if (mouthChatter1) clearInterval(mouthChatter1);

    const mouthChatter1 = setInterval(() => {
      mouth1.classList.toggle('ghost__mouth--open');
      if (i === 6) clearInterval(mouthChatter1);
      i++;
    }, 300);
  }
};
const input2 = document.getElementById('ghost-input2');
const bubble2 = document.getElementById('ghost-bubble2');

const mouth2 = document.querySelector('.ghost__mouth');

input2.onkeydown = e => {
  if (e.keyCode == 13) {
    bubble2.innerText = e.target.value;
    e.target.value = '';

    // mouth chatter
    let j = 0;
    //if (mouthChatter2) clearInterval(mouthChatter2);

    const mouthChatter2 = setInterval(() => {
      mouth2.classList.toggle('ghost__mouth--open');
      if (j === 6) clearInterval(mouthChatter2);
      j++;
    }, 300);
  }
};
const input3 = document.getElementById('ghost-input3');
const bubble3 = document.getElementById('ghost-bubble3');

const mouth3 = document.querySelector('.ghost__mouth');

input3.onkeydown = e => {
  if (e.keyCode == 13) {
    bubble3.innerText = e.target.value;
    e.target.value = '';

    // mouth chatter
    let k = 0;
    //if (mouthChatter3) clearInterval(mouthChatter3);

    const mouthChatter3 = setInterval(() => {
      mouth3.classList.toggle('ghost__mouth--open');
      if (k === 6) clearInterval(mouthChatter3);
      k++;
    }, 300);
  }
};
const input4 = document.getElementById('ghost-input4');
const bubble4 = document.getElementById('ghost-bubble4');

const mouth4 = document.querySelector('.ghost__mouth');

input4.onkeydown = e => {
  if (e.keyCode == 13) {
    bubble4.innerText = e.target.value;
    e.target.value = '';

    // mouth chatter
    let l = 0;
    //if (mouthChatter4) clearInterval(mouthChatter4);

    const mouthChatter4 = setInterval(() => {
      mouth4.classList.toggle('ghost__mouth--open');
      if (l === 6) clearInterval(mouthChatter4);
      l++;
    }, 300);
  }
};
