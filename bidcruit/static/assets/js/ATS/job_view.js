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
    $('.btn_users-cog').on('click',function(){
        $('.slideClose').removeClass('inside');
        $('.sidebar-preview').css({'width':'100%','visibility':'visible'});
    })
    $('.slideClose').on('click',function(){
        $('.sidebar-preview').css({'width':'0%','visibility':'hidden'});
        $('.slideClose').addClass('inside');
    })
})



