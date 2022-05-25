let currentRecipient = '';
let chatInput = $('#msg-input');
let chatButton = $('#btn-send');
let userList = $('#user-list');
let messageList = $('#messages');

var unread_messages_for_users=[];

console.log("current yuserrrrrrrrrrrrrrrrrrrrrrrr",currentUser)
//function remove_unread_message_count(id)
//{
//    console.log(id)
//    document.getElementById(id).innerHTML = ''
//    target_url = '/chat/update_unread_messages/'+id
//    console.log(target_url)
//    $.ajax({
//        type:'GET',
//        url:target_url,
//    }).done(function(response){
//        console.log('DONE')
//    });
//}

async function get_user_image(id){
    target_url = '/chat/get_user_image/'+id
    var return_value = await $.ajax({
        type:'GET',
        url:target_url,
    }).done(function(response){
         return response
    });
    return return_value
}

function updateUserList() {
    $.ajax({
        type:'GET',
        url:'/chat/get_unread_messages/',
    }).done(function(response){
        unread_messages_for_users = JSON.parse(response);
        console.log("response",response);
        console.log("unread_messages_for",unread_messages_for_users);
    });

     $.getJSON('/chat/api/v1/user/',async function (data) {
        userList.children('.user').remove();
        console.log("/dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",data)
        for (let i = 0; i < data.length; i++) {
            var id = data[i]['id'];
            console.log('id',id);
            console.log('id typoe',typeof(id));
            unread_message_count = unread_messages_for_users[id];
            if(unread_message_count == 0){
                unread_message_count =''
            }else{
                unread_message_count = unread_message_count + 'unread'
            }
            var user_image = await get_user_image(data[i]['email'])
            if(data[i]['is_candidate']){
                var name  = data[i]['first_name'];
            }else{
                var name  = data[i]['company_name'];
            }
            const userItem = `<a class="media new user" id="" onclick="remove_unread_message_count(${id})">
														<div class="main-img-user online">
															<img alt="" src="${user_image}">
														</div>
														<div class="media-body">
															<div class="media-contact-name">
															    <input type="hidden" id="email" value="${data[i]['email']}">
																<span id="user-name">${name}</span>
																<span id=${id}>${unread_message_count}</span>
															</div>
														</div>
													</a>`;

            $(userItem).appendTo('#user-list');
        }
        $('.user').click(function () {
            userList.children('.active').removeClass('active');
            let email = $(this).find('#email').val()
            let name = $('.user').find('#user-name').text()
            $('#selected-user').text(name);
            console.log('email>>>>>>>>>>>>>>>', name);
            $(event.target).addClass('active');
            setCurrentRecipient(email);
        });
    });
}

async function drawMessage(message) {
    let position = 'left';
    console.log('messsss',message)
    const date = new Date(message.timestamp);
    var user_image = await get_user_image(message.user)
    if (message.user === currentUser) position = 'flex-row-reverse';
    const messageItem = `<div class="message media ${position}">
                            <div class="main-img-user online"><img alt="image" src="${user_image}"></div>
                            <div class="media-body">
                                <div class="main-msg-wrapper">
                                    ${message.body}
                                </div>
                                <div>
                                    <span>${date}</span> <a href=""><i class="icon ion-android-more-horizontal"></i></a>
                                </div>
                            </div>
                        </div>`;
    $(messageItem).appendTo('#messages');
}

function getConversation(recipient) {
    $.getJSON(`/chat/api/v1/message/?target=${recipient}`, function (data) {
        console.log('data<<<<<<<<<<<<<<', data)
        messageList.children('.message').remove();
        for (let i = data['results'].length - 1; i >= 0; i--) {
            drawMessage(data['results'][i]);
        }
        messageList.animate({scrollTop: messageList.prop('scrollHeight')});
    });

}

function getMessageById(message) {
    id = JSON.parse(message).message
    $.getJSON(`/chat/api/v1/message/${id}/`, function (data) {
        if (data.user === currentRecipient ||
            (data.recipient === currentRecipient && data.user == currentUser)) {
            drawMessage(data);
        }
        messageList.animate({scrollTop: messageList.prop('scrollHeight')});
    });
}

function sendMessage(recipient, body) {
    $.post('/chat/api/v1/message/', {
        recipient: recipient,
        body: body
    }).fail(function () {
        alert('Error! Check console!');
    });
}

function setCurrentRecipient(username) {
    currentRecipient = username;
    getConversation(currentRecipient);
    enableInput();
    console.log("recipientttttttttttt",username)
}

//
//function enableInput() {
//    chatInput.prop('disabled', false);
//    chatButton.prop('disabled', false);
//    chatInput.focus();
//}
//
//function disableInput() {
//    chatInput.prop('disabled', true);
//    chatButton.prop('disabled', true);
//}

$(document).ready(function () {
    updateUserList();
    disableInput();
    var socket = ''

    socket.onopen = e =>{console.log("connection successfull")}

    // var endPoint = "ws://127.0.0.1:8000"
    // // var webSocket = new WebSocket(endPoint);
    // console.log(socket)

    chatInput.keypress(function (e) {
        if (e.keyCode == 13)
            chatButton.click();
    });

    chatButton.click(function () {
        if (chatInput.val().length > 0) {
        socket = new WebSocket('ws://' + window.location.host + 'privatechat')
            sendMessage(currentRecipient, chatInput.val(),currentUser);
            chatInput.val('');
        }
    });

    socket.onmessage = function (e) {
        getMessageById(e.data);
        // updateUserList();
        alert("received a message")
        console.log("eeeeee",e)
    };
});



