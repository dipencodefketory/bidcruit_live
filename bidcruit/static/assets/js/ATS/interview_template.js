$(document).ready(function(){
    $('#cloneList').on('click',function(){
         var clone = "";
         clone = $('#ratingMiniForm .rating__internalform:last-child').clone();
         clone.find("input").val("");
         $('#ratingMiniForm .rating__internalform:last-child').after(clone)
    })
    $(document).on('click','.delete-btn',function(){
        var listSize = $('#ratingMiniForm .rating__internalform').length;
        if(listSize == '1'){
            $('.rating__internalform').find('input[type=text],input[type=number],textarea').val('')
        }else{
            $(this).closest('.rating__internalform').remove();
        }
    })

    $(document).on('click','.rating-star',function(e){
        e.preventDefault();
        var currentItem = parseInt($(this).closest('.rate-cover').find('#rating-stars-value').val());
        var starList = $(this).closest('.rating-stars-container .rating-star');
       /* $(starList).each(function(i){
            console.log($(this))
            if(count == currentItem){
                $(this).find('.rating-star:eq('+i+')').removeClass('is--active')
            }
        })*/
    })
})

