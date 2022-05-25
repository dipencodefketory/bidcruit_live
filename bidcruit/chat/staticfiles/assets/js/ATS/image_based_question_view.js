$(function(){
    $('.upload-action').on('click',function(){ //file upload funtion
        //add code
    })

    $('.print-action').on('click',function(){ //print funtion
        //add code
    })

    $('.mini-nav').on('click',function(){ //show navigation funtion
        //add code
    })


    $(document).on('click','.slide-tab-btn',function(){
        currentListEle = $(this);
        if(currentListEle.closest('.slide-list').find('.detail-section').is(":visible")){
            console.log('true')
            $('.short-details').show();
            $('.detail-section').slideUp();
            currentListEle.closest('.title-section').find('.short-details').show('fast');
            currentListEle.closest('.slide-list').find('.detail-section').slideUp();
        }else{
            console.log('false')
            $('.short-details').show();
            $('.detail-section').slideUp();
            currentListEle.closest('.title-section').find('.short-details').hide('fast');
            currentListEle.closest('.slide-list').find('.detail-section').slideDown();
        }
    })

    $(document).on('click','.delete-btn',function(){
        var deletequestion = {'que_id':$(this).closest('.slide-list').find('[name="que_id"]').val()}
        console.log('deletequestion', deletequestion)
        var question_card = $(this).closest('.slide-list')
        swal({
            title: "Are you sure?",
            text: "You will not be able to recover deleted subjects!",
            type: "warning",
            showCancelButton: true,
            confirmButtonClass: "btn-danger",
            confirmButtonText: "Yes, delete it!",
            cancelButtonText: "Cancel",
            closeOnConfirm: false,
            closeOnCancel: false
        },function(isConfirm) { //send ajax request for detele category action
            if (isConfirm){
                $.ajax({
                    url:"/company/delete_image_question/",
                    headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                    type:'POST',
                    contentType: 'application/json; charset=UTF-8',
                    data: JSON.stringify(deletequestion),
                    error: function (request, status, error) {
                          alert(error);
                    }
                }).done(function(response){
                    if(response == 'True'){
                        swal("Deleted!", "Your subject has been deleted.", "success");
                        question_card.remove();
                    }else{
                        swal("Error!", "Something Wrong !!", "error");
                    }
                });
            } else {
                swal("Cancelled", "Your subject is safe :)", "error");
            }
        });
    })

})