$(document).ready(function(){
var getListSize =  $('.tbls-inline li').length;
console.log('size',getListSize)
 $(document).on('click','.t-btn',function(e){
    e.preventDefault();
    $('.tab-title_name').removeClass('tab-act')
    $('.tab-preview-list .tab-model').removeClass('active');
    var getTabId = $(this).attr('data-id');
    $(this).find('.tab-title_name').addClass('tab-act')
    $('#'+getTabId).addClass('active');
 })
$('.next-btn').on('click',function(){
    var tabWidth = $('.sl-tab-list').width() + 15;
    console.log(tabWidth)
    var slidePoz = $('.tbls-inline').attr('data-poz')
    if(slidePoz !== '0'){
        var addPoz = parseInt(slidePoz) + tabWidth;
        $('.tbls-inline').css("transform","translate3d("+addPoz+"px, 0px, 0px)")
        $('.tbls-inline').attr('data-poz',addPoz)
    }
})
$('.prev-btn').on('click',function(){
    var tabWidth = $('.sl-tab-list').width() + 15;
    //console.log(tabWidth)
    var getTotalSize = (getListSize * tabWidth) - 720;
    getTotalSize = '-'+getTotalSize;
    var slidePoz = $('.tbls-inline').attr('data-poz')
    console.log(getTotalSize+'....'+slidePoz)
   if(slidePoz == '0'){
        var removePoz = slidePoz - tabWidth;
        $('.tbls-inline').css("transform","translate3d("+removePoz+"px, 0px, 0px)")
        $('.tbls-inline').attr('data-poz',removePoz)
    }else if(slidePoz <= getTotalSize && slidePoz !== '0'){
        var removePoz = slidePoz - tabWidth;
        $('.tbls-inline').css("transform","translate3d("+removePoz+"px, 0px, 0px)")
        $('.tbls-inline').attr('data-poz',removePoz)
    }else{
        $('.tbls-inline').css("transform","translate3d(0px, 0px, 0px)")
        $('.tbls-inline').attr('data-poz','0')  
    }
})
})
