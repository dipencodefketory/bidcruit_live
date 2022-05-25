$(document).ready(function(){
    stickTopHeight = $('.profile-page').offset().top - 25;
    $(window).scroll(function(){
        var currentScroll = $(window).scrollTop();
        console.log(stickTopHeight+">>>>"+currentScroll)
        if($(this).scrollTop() >= stickTopHeight){
            $('.fx-sticky-right-col').css('top',stickTopHeight+'px')
          }else{
            $('.fx-sticky-right-col').css('top','auto')
          }
        
    });
})
