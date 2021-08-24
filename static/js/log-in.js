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
