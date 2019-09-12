const index_container = document.querySelector(".index_container");
const index_header = index_container.querySelector("h1");
const index_subtitle = index_container.querySelector(".subtitle")
const index_form = index_container.querySelector(".index_form");
const index_input = index_container.querySelector("input");

const line_break = document.createElement("br");
const blank_pattern = /^\s+|\s+$/g;
const APP = `황총무`;
const MSG01 = `걱정하지 마세요. 다 받아드립니다.`;
const MSG02 = `돈 받으러 가기`;
const MSG03 = `정산명을 입력해주세요`;
const ALERT01 = `정산명을 입력해주세요!`;


function savePayment(pay_name) {
    $.post('/pay_register'
        , {'pay_name': pay_name}
        , function(data) {
            window.location.href = '/pay/' + data.pay_id; 
        }
    );
}

function checkVaildation(pay_name) {
    if(pay_name.replace(blank_pattern, "") === "") {
        alert(ALERT01);
        index_input.value = '';
        return false;
    } else {
        return true;
    }
}

function handleSubmit(event) {
    event.preventDefault();
    const pay_name = index_input.value;
    if (checkVaildation(pay_name)) {
        savePayment(pay_name);
    }
}

function askForPayment() {
    index_form.addEventListener('submit', handleSubmit);
}

function setAddButton() {
    const regBtn = document.createElement('button');
    regBtn.innerText = MSG02;
    regBtn.addEventListener('click', handleSubmit);

    index_input.after(line_break);
    line_break.after(regBtn);
}

function setBasicHtml() {
    index_header.innerText = APP;
    index_subtitle.innerText = MSG01;

    index_input.title = MSG03;
    index_input.placeholder = MSG03;
    index_input.maxLength = "15";
}

function initEvent() {
    setBasicHtml();
    setAddButton();
    askForPayment();
}

initEvent();