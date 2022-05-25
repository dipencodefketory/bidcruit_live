$(document).ready(function(){
    $('.info-btn').on('click',function(){
        $('.slideClose').removeClass('inside');
        $('.sidebar-preview').css({'width':'100%','visibility':'visible'});
    })
    $('.slideClose').on('click',function(){
        $('.sidebar-preview').css({'width':'0%','visibility':'hidden'});
        $('.slideClose').addClass('inside');
    })
    
})