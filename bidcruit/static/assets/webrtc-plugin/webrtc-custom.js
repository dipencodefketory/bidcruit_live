/*-----------------------------------------------------------------------*/

var showWebStatus = "";
var showMicStatus = "";
$(document).ready(function(){
    navigator.getMedia = ( navigator.getUserMedia || // use the proper vendor prefix
        navigator.webkitGetUserMedia ||
        navigator.mozGetUserMedia ||
        navigator.msGetUserMedia);
        plugedWebCamStatus();
        plugedMicroPhoneStatus();
        autoConnectActivity();

    $("#playStream").on('click', function(){
        var btnText = $(this).find('label').text();
        if(btnText == 'Start Test'){
            $(this).find('label').text('Stop Test');
            equpModalHandle(true);
        }else{
            $(this).find('label').text('Start Test');
            equpModalHandle(false);
        }
    });

    $("#playStream2").on('click', function(){
        var btnText = $(this).find('label').text();
        if(btnText == 'Start Test'){
            $(this).find('label').text('Stop Test');
            equpModalHandle(true);
        }else{
            $(this).find('label').text('Start Test');
            equpModalHandle(false);
        }
    })

    $(".dismiss-msg").on('click',function(){
        $(this).parent('.toastSet').hide('slow');
        $(this).prev('div').html('');
    })

    $("#nextPageButton").on('click',function(){
       var micConnection = plugedMicroPhoneStatus();
       var webCamConnection =  plugedWebCamStatus();
       var autoConvalidkey = autoConnectActivity();
       if(micConnection.status == false){
            $(".micValidMsg").html("");
            $(".micValidMsg").html("<p>"+micConnection.msg+"</p>");
            $(".micMsgPromt").show('slow').css("background","#fc3268");
        }
        if(webCamConnection.status == false){
            $(".webCamValidMsg").html("");
            $(".webCamValidMsg").html("<p>"+webCamConnection.msg+"</p>");
            $(".webCamMsgPromt").show('slow').css("background","#fc3268");
        }
       if(webCamConnection.status == true && micConnection.status == true || autoConvalidkey == true){
        console.log(autoConvalidkey)
        alert('Go to next Page....');
        $(".webCamWithMic").hide();
        $(".micTestLayout").show();
       }
    })

    $("#nextPageButton2").on('click',function(){
        var micConnection = plugedMicroPhoneStatus();
        //var autoConvalidkey = autoConnectActivity();
        if(micConnection.status == false){
             $(".micValidMsg").html("");
             $(".micValidMsg").html("<p>"+micConnection.msg+"</p>");
             $(".micMsgPromt").show('slow').css("background","#fc3268");
         }
        if(micConnection.status == true){
         console.log(autoConvalidkey)
         alert('Go to next Page....');
        }
    })

});

function equpModalHandle(checkKey){ // start - stop (webcam and mic)
    var vid = document.getElementById("gum-video");
    var aud = document.getElementById("gum-audio");
    var webCamCheck = plugedWebCamStatus();
    var micCheck = plugedMicroPhoneStatus();
    console.log("webCamCheck>>>",webCamCheck);
    console.log("micCheck>>>>",micCheck)
    if(webCamCheck.status == true && micCheck.status == true){
        if(checkKey == true){
            vid.play();
            aud.play();
        }else{
            vid.pause();
            aud.pause();
        }
    }else{
        if(micCheck.status == false){
            $(".micValidMsg").html("");
            $(".micValidMsg").html("<p>"+micCheck.msg+"</p>");
            $(".micMsgPromt").show('slow').css("background","#fc3268");
        }
        if(webCamCheck.status == false){
            $(".webCamValidMsg").html("");
            $(".webCamValidMsg").html("<p>"+webCamCheck.msg+"</p>");
            $(".webCamMsgPromt").show('slow').css("background","#fc3268");
        }
    }
}

function equpModalHandle2(checkKey){ // start - stop (only mic)
    var aud = document.getElementById("gum-audio2");
    var micCheck = plugedMicroPhoneStatus();
    console.log("micCheck>>>>",micCheck)
    if(micCheck.status == true){
        if(checkKey == true){
            vid.play();
            aud.play();
        }else{
            vid.pause();
            aud.pause();
        }
    }else{
        if(micCheck.status == false){
            $(".micValidMsg").html("");
            $(".micValidMsg").html("<p>"+micCheck.msg+"</p>");
            $(".micMsgPromt").show('slow').css("background","#fc3268");
        }
    }
}

function plugedWebCamStatus(){ //WebCam Connection Check
    navigator.getMedia({audio: true}, function() {
        showWebStatus = {status:true,msg:'WebCam Connection Successful.'};
    }, function() {
        showWebStatus = {status:false,msg:'WebCam Connection Not Found, Please check WebCam connection.'};
    });
    return showWebStatus;
}
function plugedMicroPhoneStatus(){ //MicroPhone  Connection Check
    navigator.getMedia({video: true}, function() {
        showMicStatus = {status:true,msg:'MicroPhone Connection Successful.'};
    }, function() {
        showMicStatus = {status:false,msg:'MicroPhone Connection Not Found, Please check MicroPhone connection.'};
    });
    return showMicStatus;
}
function autoConnectActivity(){ //autoConnection Handler
    setInterval(function(){
      let autoConWebCam = plugedWebCamStatus();
      let autoConMicro =  plugedMicroPhoneStatus();
      var avtivateKey = "";
      if(autoConWebCam.status == true && autoConMicro.status == true){
        avtivateKey = true;
        return avtivateKey;
      }else{
        avtivateKey = false;
        return avtivateKey;
      }
    }, 900)
}
