'use strict';

/***
 * WebCam + Microphone Functionality
 */


 var video = document.querySelector('video');
 var audio = document.querySelector('audio');

 var mediaDomEle = window.constraints = {
  audio: true,
  video: true
};

function mediaHandler(stream){
  var mediaObjectData = {};
  var videoTracks = stream.getVideoTracks();
  var audioTracks = stream.getAudioTracks();
  stream.oninactive = function() {
    console.log('Stream inactive');
  };
  window.stream = stream; // make variable available to browser console
  video.srcObject = stream;
  audio.srcObject = stream;
  mediaObjectData = {vidSrcObj:video.srcObject, audSrcObj:audio.srcObject};
 // console.log('mediaObjectData>>>>',audio.srcObject);
  //console.log('mediaObjectData>>>>',video.srcObject)
  return mediaObjectData;
}

function mediaErrorHandler(error) {
  //console.log('Media Connetion Error', error);
  return error;
}

navigator.mediaDevices.getUserMedia(mediaDomEle).
    then(mediaHandler).catch(mediaErrorHandler);
