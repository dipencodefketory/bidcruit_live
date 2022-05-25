$(document).ready(function(){
    $("#jobTabView").on('click',function(){
        $('.candidatedetails-list').removeClass('active');
        $('.jobdetails-list').addClass('active');
    })
    $("#candicateTabView").on('click',function(){
        $('.jobdetails-list').removeClass('active');
        $('.candidatedetails-list').addClass('active');
    })

    $(".collps-btn").on('click',function(){
        $(this).toggleClass('active').closest('.toggleTabSection').find('.toggleListContainer').toggleClass('active')
    })
})