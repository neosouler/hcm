const pay_container = document.querySelector(".pay_container");
const pay_step = pay_container.querySelector("h2");
const pay_subtitle = pay_container.querySelector(".subtitle")
const pay_explain = pay_container.querySelector(".this_round_explain");
const pay_form = pay_container.querySelector(".pay_form");
const pay_input = pay_container.querySelector("input[type=text]");

const pay_id = pay_form.querySelector("input[id=pay_id]");

const line_break = document.createElement("br");
const blank_pattern = /^\s+|\s+$/g;
const STEP = `1단계`;
const MSG01 = `정산 멤버들을 등록해주세요`;
const MSG02 = `현재 등록 멤버`;
const MSG03 = `멤버 추가`;
const MSG04 = `ex) 쫘니`;
const MSG05 = `등록`;
const ALERT01 = `멤버를 등록해주세요!`;


function drawPayMemberTable(pay_member_list, pay_member_id) {
    const pay_member_tb = document.createElement('table');
    pay_member_tb.classList.add('pay_member_list_table');

    pay_explain.after(pay_member_tb);
    console.log(pay_member_tb);
}

function saveMember(member_name) {
    console.log('saveMember start');

    $.getJSON('/add_pay_member', {
        pay_id: pay_id.value,
        pay_member_nm: member_name
    }, function(data) {
        pay_member_list = data.pay_member_list;
        pay_member_id = data.pay_member_id;
        
        drawPayMemberTable(pay_member_list, pay_member_id);
    });
}

function checkVaildation(member_name) {
    if(member_name.replace(blank_pattern, "") === "") {
        alert(ALERT01);
        pay_input.value = '';
        return false;
    } else {
        return true;
    }
}

function handleSubmit(event) {
    event.preventDefault();
    const member_name = pay_input.value;
    if (checkVaildation(member_name)) {
        saveMember(member_name);
    }
}

function askForMember() {
    pay_form.addEventListener('submit', handleSubmit);
}

function setButton() {
    const regBtn = document.createElement('button');
    regBtn.classList.add('add_pay_member');
    regBtn.innerText = MSG05;
    regBtn.addEventListener('click', handleSubmit);

    pay_input.after(line_break);
    line_break.after(regBtn);
}

function setBasicHtml() {
    pay_step.innerText = STEP;
    pay_subtitle.innerText = MSG01;
    pay_explain.innerText = MSG02;

    pay_input.title = MSG03;
    pay_input.placeholder = MSG04;
    pay_input.maxLength = "5";
}

function initEvent() {
    setBasicHtml();
    setButton();
    askForMember();
}

initEvent();