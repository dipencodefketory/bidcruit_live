var mapPeers = []//stores 2 items list where the first element is rtc peer connecation and the second is the data channel


// var labelUsername = document.querySelector("#label-username")
var usernameInput = document.querySelector("#username-input")
var btnJoin = document.querySelector("#btn-join")
var btnLeave = document.querySelector(".Leave_video_btn")

var username;

var webSocket;

var active_participants

$('.end_interview').on("click",endInterview)

/*
stun.l.google.com:19302
*/

//var iceConfiguration = {"iceServers":[{"url":"stun:stun.l.google.com:19302"}]};

const iceConfiguration = {
    'iceServers': [{
        urls:["stun:stun.bidcruit.com:3478","turn:turn.bidcruit.com:3478"],
        "username":"admin",
        "credential":"admin"}
    ]
}

/*
const iceConfiguration = {
    'iceServers': [{
    urls:["stun:stun.l.google.com:19302"]
    }]
   }

*/

function webSocketOnMessage(event)
{   
    
    console.log("message received")
    var parseData = JSON.parse(event.data);

    var peerUsername =parseData['peer']
    var action =parseData['action']



    if(action == "end-meeting")
    {

        for(var i=0;i<Object.keys(mapPeers).length;i++)
        {
            console.log(Object.keys(mapPeers)[i])

            var removeUserName = Object.keys(mapPeers)[i]

            var peerConnection = mapPeers[removeUserName][0]

            console.log("perererererer",peerConnection)

            peerConnection.close()
        }

        $('#leave-modal').modal('hide');
        $('#interview-ended').modal({
            backdrop: 'static',
            keyboard: false
        })
        return

    }
    if(username == peerUsername)
    {

        return
    }
    console.log("after if")
    var receiver_channel_name = parseData['message']['receiver_channel_name']

    if(action=='new-peer')
    {
        createOfferer(peerUsername,receiver_channel_name)
        return
    }

    if(action == 'new-offer')
    {
    
    	console.log("new offer was created")
        var offer = parseData['message']['sdp']

        createAnswerer(offer,peerUsername,receiver_channel_name)
        return
    }
    if(action == "new-answer")
    {
        var answer  = parseData['message']['sdp']
        console.log("here is the answer",answer)

        var peer = mapPeers[peerUsername][0]
        console.log("here is the peer",peer)

        peer.setRemoteDescription(answer)
        return
    }

}
btnJoin.addEventListener("click",function(){
    username = usernameInput.value
    if(username =="")
    {
        return;
    }
    else
    {
        btnJoin.disabled = true
        btnJoin.style.display = 'none'

        var labelUsername = document.querySelector("#label-username")
        labelUsername.innerHTML = username

        var loc  = window.location
        var wsstart = 'wss://'

        if(loc.protocol == "https:")
        {
            wsstart = 'wss://'
        }

        var endPoint = wsstart +loc.host +loc.pathname
        
        // endPoint = "wss://freakculture.com:8001/"
        // console.log("loc.host",loc.host)
        // console.log("loc.pathname",loc.pathname)
        console.log("endpoint",endPoint)
        endPoint = "wss://"+location.host+":9000/"+get_room_no()+"/"
//        endPoint = "ws://192.168.1.103:8000/"+get_room_no()+"/"
        webSocket = new WebSocket(endPoint);
        
        webSocket.addEventListener('open',function(){
            console.log("connection opened")
            btnLeave.style.display = 'block';
            send_signal('new-peer',{})
            console.log("donewa")
        })

        webSocket.addEventListener('message',webSocketOnMessage)

        webSocket.addEventListener('close',function(event){
            console.log(event)
        })

        webSocket.addEventListener('error',function(event){
            if (event.code == 1000)
                reason = "Normal closure, meaning that the purpose for which the connection was established has been fulfilled.";
            else if(event.code == 1001)
                reason = "An endpoint is \"going away\", such as a server going down or a browser having navigated away from a page.";
            else if(event.code == 1002)
                reason = "An endpoint is terminating the connection due to a protocol error";
            else if(event.code == 1003)
                reason = "An endpoint is terminating the connection because it has received a type of data it cannot accept (e.g., an endpoint that understands only text data MAY send this if it receives a binary message).";
            else if(event.code == 1004)
                reason = "Reserved. The specific meaning might be defined in the future.";
            else if(event.code == 1005)
                reason = "No status code was actually present.";
            else if(event.code == 1006)
               reason = "The connection was closed abnormally, e.g., without sending or receiving a Close control frame";
            else if(event.code == 1007)
                reason = "An endpoint is terminating the connection because it has received data within a message that was not consistent with the type of the message (e.g., non-UTF-8 [https://www.rfc-editor.org/rfc/rfc3629] data within a text message).";
            else if(event.code == 1008)
                reason = "An endpoint is terminating the connection because it has received a message that \"violates its policy\". This reason is given either if there is no other sutible reason, or if there is a need to hide specific details about the policy.";
            else if(event.code == 1009)
               reason = "An endpoint is terminating the connection because it has received a message that is too big for it to process.";
            else if(event.code == 1010) // Note that this status code is not used by the server, because it can fail the WebSocket handshake instead.
                reason = "An endpoint (client) is terminating the connection because it has expected the server to negotiate one or more extension, but the server didn't return them in the response message of the WebSocket handshake. <br /> Specifically, the extensions that are needed are: " + event.reason;
            else if(event.code == 1011)
                reason = "A server is terminating the connection because it encountered an unexpected condition that prevented it from fulfilling the request.";
            else if(event.code == 1015)
                reason = "The connection was closed due to a failure to perform a TLS handshake (e.g., the server certificate can't be verified).";
            else
                reason = "Unknown reason";
        })
    }
})


var localStream = new MediaStream();

const constraints = {
    'video':true,
    'audio':true
}

const localVideo = document.querySelector("#local-video")
const btnToggleAudio = document.querySelector("#btn-toggle-audio")
const btnToggleVideo = document.querySelector("#btn-toggle-video")

var userMedia = navigator.mediaDevices.getUserMedia(constraints).then(stream =>{
    localStream = stream
    localVideo.srcObject = localStream
    localVideo.muted=true
    
    localVideo.onloadedmetadata = function(e) {
    	localVideo.play();
    };


    var audioTracks = stream.getAudioTracks()
    var videoTracks = stream.getVideoTracks()


    audioTracks[0].enabled = true
    videoTracks[0].enabled = true

    btnToggleAudio.addEventListener("click",()=>{
        audioTracks[0].enabled = !audioTracks[0].enabled

        if(audioTracks[0].enabled)
        {
            btnToggleAudio.innerHTML ="Audio Mute"
            return
        }
        else
        {
            btnToggleAudio.innerHTML ="Audio unMute"
            return
        }
    })

    btnToggleVideo.addEventListener("click",()=>{
        videoTracks[0].enabled = !videoTracks[0].enabled

        if(videoTracks[0].enabled)
        {
            btnToggleVideo.innerHTML ="Video Off"
            return
        }
        else
        {
            btnToggleVideo.innerHTML ="Video On"
            return
        }
    })
}).catch(error =>{
    console.log("error",error)
})

// var jsonStr = JSON.stringify({
//     "peer":username,
//     "action":"new-peer",
//     // "action":"new-offer",
//     // "action":"new-answer", response to new offer 
//     "message":"test message1212"
// })

// webSocket.onopen = function() {
//     webSocket.send('Hello server')
//     webSocket.close()
// }

function endInterview(){
    send_signal('end-meeting',"")
}

function send_signal(action,message)
{
    if(action == 'end-meeting'){
        var jsonStr = JSON.stringify({
            "peer":username,
            "action":action,
            "link":get_room_no(),
            "message":message
        })
    }else{
        var jsonStr = JSON.stringify({
            "peer":username,
            "action":action,
            "message":message
        })
    }
    webSocket.send(jsonStr)
}


function createOfferer(peerUsername,receiver_channel_name)
{
    console.log("create offerer was called")
    // var peer = new RTCPeerConnection(ice);//will work for only same network devices.for different network devieces serach stun and turn servers
    var peer = new RTCPeerConnection(iceConfiguration);
    addLocalTracks(peer);
    console.log("local tracks addeds")
    var dc = peer.createDataChannel('channel');
    dc.addEventListener("open",function(){
        console.log("connection opened")
    })

    dc.addEventListener("close",function(){
        console.log("connection closed")
    })

    dc.addEventListener("message",dcOnMessage)
    var remoteVideo = createVideo(peerUsername)
    setOnTrack(peer,remoteVideo)

    mapPeers[peerUsername] = [peer,dc]

    peer.addEventListener("iceconnectionstatechange",function(){
        var iceConnectionState = peer.iceConnectionState

        if(iceConnectionState === 'failed' || iceConnectionState === 'disconnected' || iceConnectionState==='closed') 
        {
            delete mapPeers[peerUsername]

            if(iceConnectionState !="closed")
            {
                peer.close()
            }
            removeVideo(remoteVideo)
        }
    })

    peer.addEventListener("icecandidate",function(event){
        if(event.candidate)
        {
            console.log("new ice candidate",JSON.stringify(peer.localDescription))
            return 
        }
	console.log("----------------------ICE CANDIDATE !!!!!1----------------------------")
        send_signal('new-offer',{
            'sdp':peer.localDescription,
            'receiver_channel_name':receiver_channel_name
        })
    })


    peer.createOffer().then(o => {peer.setLocalDescription(o)}).then(function(){
        console.log("local description set successfully")
    })
    
    console.log("createofferfer finsied")
}


function addLocalTracks(peer)
{
    localStream.getTracks().forEach(function(track){
        peer.addTrack(track,localStream)
    })
    return 
}


var msg_list = document.querySelector("#message-list")

function dcOnMessage(event)
{
    var message = event.data;
    var li = document.createElement("li")
    li.appendChild(document.createTextNode(message))
    msg_list.appendChild(li)
}


function createVideo(peerUsername)
{
    var videoContainer = document.querySelector(".video_get_section_inner")
    var remoteVideo = document.createElement("video")

    var local_video = $('#local-video')
    local_video.removeClass("main_video")
    local_video.addClass("you_video")

    remoteVideo.id=peerUsername+"-video"
    remoteVideo.autoplay = true
    remoteVideo.playsInline = true
    remoteVideo.classList.add("main_video")

    videoContainer.appendChild(remoteVideo)

    return remoteVideo
}


function setOnTrack(peer,remoteVideo)
{
    var remoteStream = new MediaStream();

    remoteVideo.srcObject = remoteStream
    remoteVideo.onloadedmetadata = function(e) {
	    alert("play")
    	remoteVideo.play();
    };
    
    peer.addEventListener('track',async function(event){
        remoteStream.addTrack(event.track,remoteStream)
    })
}


function removeVideo(Video)
{
    Video.parentNode.removeChild(Video);
}


function createAnswerer(offer,peerUsername,receiver_channel_name)
{
    // var peer = new RTCPeerConnection(null);//will work for only same network devices.for different network devieces serach stun and turn servers
    
    console.log("create answerere was called")
    var peer = new RTCPeerConnection(iceConfiguration);
    addLocalTracks(peer);

    // dc.addEventListener("message",dcOnMessage)
    var remoteVideo = createVideo(peerUsername)
    setOnTrack(peer,remoteVideo)

    peer.addEventListener('datachannel',e =>{
        peer.dc = e.channel
        peer.dc.addEventListener("open",function(){
            console.log("connection opened")
        })

         peer.dc.addEventListener("close",function(){
            console.log("connection closed")
        })
    
        peer.dc.addEventListener("message",dcOnMessage)
        mapPeers[peerUsername] = [peer,peer.dc]
        
    })

    peer.addEventListener("iceconnectionstatechange",function(){
        var iceConnectionState = peer.iceConnectionState

        if(iceConnectionState === 'failed' || iceConnectionState === 'disconnected' || iceConnectionState==='closed') 
        {
            delete mapPeers[peerUsername]

            if(iceConnectionState !="closed")
            {
                peer.close()
            }
            removeVideo(remoteVideo)
        }
    })

    peer.addEventListener("icecandidate",function(event){
        if(event.candidate)
        {
            console.log("new ice candidate",JSON.stringify(peer.localDescription))
            return 
        }

        send_signal('new-answer',{
            'sdp':peer.localDescription,
            'receiver_channel_name':receiver_channel_name
        })
    })

    peer.setRemoteDescription(offer).then(()=> {
        console.log("remote desctiption set succeslfully for %" , peerUsername)
        return peer.createAnswer()
    })
    .then(a =>{
        console.log("answer created")
        peer.setLocalDescription(a);
    }).catch(error =>{
        console.log("error =========" ,error)
    })
    
    console.log("create answerer finished")
    
}
