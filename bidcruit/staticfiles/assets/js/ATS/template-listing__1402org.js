


$(document).ready(function(){
    $('.candidate_table').DataTable({
        language: {
            searchPlaceholder: 'Search...',
            sSearch: '',
            lengthMenu: '_MENU_'
        }
    });

    console.log("from js fiiiiiile",$(".tab-pane#basic"))
    $(".tab-pane#basic").addClass("active")
    // $(".nav-link").addClass("active")
    initDomElement(); //init function

    $(document).on('click','.collapse_title',function(){ //collapse toggle event
        
        var getChildList = $(this).next('.categoryListOftab');
        var currentEle = $(this);
        var parentSibling = $(this).closest('.collapse_parent_tab');
        parentSibling.prevAll('.collapse_parent_tab').find('.categoryListOftab').slideUp();
        parentSibling.nextAll('.collapse_parent_tab ').find('.categoryListOftab').slideUp();
        /** siblings list activeClass remove**/
        parentSibling.prevAll('.collapse_parent_tab').find('.collapse_title lable').removeClass('actTab')
        parentSibling.prevAll('.collapse_parent_tab').find('.collapse_title .toggle-arrows').removeClass('active')
        parentSibling.nextAll('.collapse_parent_tab').find('.collapse_title lable').removeClass('actTab')
        parentSibling.nextAll('.collapse_parent_tab').find('.collapse_title .toggle-arrows').removeClass('active')
        parentSibling.prevAll('.collapse_parent_tab').find('.categoryListOftab li a').removeClass('active')
        parentSibling.nextAll('.collapse_parent_tab').find('.categoryListOftab li a').removeClass('active')
        parentSibling.prevAll('.collapse_parent_tab').find('.catActionBtns').removeClass('bg-act')
        parentSibling.nextAll('.collapse_parent_tab').find('.catActionBtns').removeClass('bg-act')

        if(getChildList.is(":visible")){
            currentEle.find('lable').removeClass('actTab')
            getChildList.slideUp();
            currentEle.find('.toggle-arrows').removeClass('active');
        }else{
            currentEle.find('lable').addClass('actTab')
            getChildList.slideDown();
            currentEle.find('.toggle-arrows').addClass('active');
        }
    })

    $(document).on('click','.categoryListOftab li a',function(){ //reset main categories active tab
        $('#header').hide();
        $(document).find('.catActionBtns').removeClass('bg-act')
        $(this).closest('li').find('.catActionBtns').addClass('bg-act');
        /*$(".tab-title__list li").each(function(){
            if($(this).find('a').hasClass('active')){
                $(this).find('a').removeClass('active')
            }
        })*/
    })

    $(".tab-title__list li a").on('click',function(){ //reset child categories active tab
        $(".categoryListOftab li").each(function(){
            if($(this).find('a').hasClass('active')){
                $(this).find('a').removeClass('active')
            }
        })
    })
//    $('.collapes_wrapper .collapse_parent_tab').each(function(){ //append clone of category-list
//        var addMoreBtn = `<li>
//                            <div class="addmore-clone__section">
//                                <button type="button" class="btn btn-sm btn-outline-light rounded-20 text-capitalize addmore-tab">
//                                    <i class="fe fe-plus"></i>add category
//                                </button>
//                            </div>
//                         </li>`
//        $(this).find('.categoryListOftab li:last').after(addMoreBtn);
//    })


    $(document).on('click','.edit-tab',function(){ //edit category event
        $('.es-subtitle').attr('readonly','').removeClass('changeTitle')
        $(this).closest('li').find('.es-subtitle').removeAttr('readonly').addClass('changeTitle');
        

    })
    $(document).on('change','.es-subtitle',function(){ //edit category event
        var updatecategory={'cat_id':$(this).attr('id'),'cat_name':$(this).val(),'stage_id':$(this).closest('ul').find("input[name='stage_id']").val()}
        if($(this).val()!==''){
        $.ajax({
            url:"/company/update_category/",
            headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
            type:'POST',
            contentType: 'application/json; charset=UTF-8',
            data: JSON.stringify(updatecategory),
            error: function (request, status, error) {
                  alert(error);
            }
       }).done(function(response){
           
           if(response=="True"){
            swal("Updated!", "Your category has been updated.", "success");
           }
           else{
            swal("Updated!", "Your category is safe.", "error"); 
           }
       });
    }
    else{
        swal("Enter Category Name!", "Please enter category name.", "error");
        // $(this).attr('readonly','').removeClass('changeTitle')
       
    }
    if($(this).val() == ''){
        setTimeout(function(){
            $(this).removeAttr('readonly')
            console.log('external>>'+$(this).val())
        },2500)
        
    }
    

    })
    $(document).on('click','.delete-tab', function(){ //delete category list
       // $(this).closest('li').remove();
       
       var remvoeEle = $(this).closest('li');
       var deletecategory={'cat_id':$(this).closest('li').find("input[name='cat_id']").val(),'stage_id':$(this).closest('ul').find("input[name='stage_id']").val()}
       swal({
        title: "Are you sure?",
        text: "You will not be able to recover deleted category!",
        type: "warning",
        showCancelButton: true,
        confirmButtonClass: "btn-danger",
        confirmButtonText: "Yes, delete it!",
        cancelButtonText: "Cancel",
        closeOnConfirm: false,
        closeOnCancel: false
      },
      function(isConfirm) { //send ajax request for detele category action
            if (isConfirm) {
                    $.ajax({
                    url:"/company/delete_category/",
                    headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                    type:'POST',
                    contentType: 'application/json; charset=UTF-8',
                    data: JSON.stringify(deletecategory),
                    error: function (request, status, error) {
                          alert(error);
                    }
               }).done(function(response){
                  
                swal("Deleted!", "Your category has been deleted.", "success");
                remvoeEle.remove();
               });
            } else {
                swal("Cancelled", "Your category is safe :)", "error");
            }
       });
    })

    // $(document).on('click','.addmore-tab',async function(){
    //     //ajax request for clone id
    //     var createCatId='';
    //     var add_data={'stage_id':$(this).closest('ul').find("input[name='stage_id']").val(),'add_category':"add new category"};
        
    //     createCatId= JSON.parse(await add_cat(add_data))

    //     console.log('uyfgfhjhgg',createCatId)
    //     if(createCatId['status']==false){
    //         $(this).closest(li).remove()
    //     }
    //     else{
    //         console.log('================',createCatId['cat_id'])
    //     var addCloneList =  `<li>
    //         <a href="#prereq-2" data-toggle="tab"><i class="fe fe-airplay mr-1"></i>
    //             <input type="text" id=`+createCatId['cat_id']+` hidden value=`+createCatId['cat_id']+` name="cat_id" readonly>
    //             <input type="text" id=`+createCatId['cat_id']+` class="es-subtitle" value="add new category" placeholder="add new category" readonly>
    //         </a>
    //         <div class="catActionBtns">
    //             <div class="edit-tab"><i class="fas fa-edit"></i></div>
    //             <div class="delete-tab"><i class="fas fa-trash-alt "></i></div>
    //         </div>
    //     </li>`;
        
    //     $(this).closest('li').before(addCloneList)
    //    }
    // });
    

    $("#saveJobCreateItem").on("click",async function(){
        let tempTitle = $(".jc-tempname").val();
        let tempFormId = $("#jcModel").data('id');
        var add_data = {'stage_id':tempFormId,'add_category':tempTitle};
        var classcreate='.cat-sub-'+tempFormId;
        var createCatId='';

        console.log('uyfgfhjhgg',createCatId)
        if(tempTitle != ""){
            createCatId= JSON.parse(await add_cat(add_data))
            if(createCatId['status']==false){
                $(this).closest(li).remove()
            }
            else{
                console.log('================',createCatId['cat_id'])
            var addCloneList =  `<li>
                <a href="#prereq-2" data-toggle="tab"><i class="fe fe-airplay mr-1"></i>
                    <input type="text" id=`+createCatId['cat_id']+` hidden value=`+createCatId['cat_id']+` name="cat_id" readonly>
                    <input type="text" id=`+createCatId['cat_id']+` class="es-subtitle" value="`+tempTitle+`" readonly>
                </a>
                <div class="catActionBtns">
                    <div class="edit-tab"><i class="fas fa-edit"></i></div>
                    <div class="delete-tab"><i class="fas fa-trash-alt "></i></div>
                </div>
            </li>`;
            
            $(classcreate).closest('li').before(addCloneList)
            $('#jcModel input[type=text]').val('');
            $('#jcModel #closetempModal').trigger('click');
            $('#error').remove();
        }
    }
    else{
        $('#jcModel input[type=text]').after('<div id="error" style="color:red;">Name is Required</div>');
    }
        
    });
    $(".addmore-tab").on('click',function(){
        $('#error').remove();
        var getId = $(this).attr('data-id');
        console.log('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',getId)
        $("#jcModel").attr("data-id",getId);
    })

async function add_cat(add_data){
    var newKeyId = "";
    var return_data = await $.ajax({
        url:"/company/add_category/",
        headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
        type:'POST',
        contentType: 'application/json; charset=UTF-8',
        data: JSON.stringify(add_data),
        error: function (request, status, error) {
                console.log(error);
        }
    }).done(function(response){
    });
    return return_data
};
    $(document).on('click','.delete-row',function(){ //remove template row to the table
        var getCurrentRow = $(this).closest('tr');
        var deletetemplate={'template_id':$(this).attr('data-template'),'cat_id':$(this).attr('data-subcat'),'stage_id':$(this).attr('data-maincat')}
        console.log('========',deletetemplate)
        swal({
            title: "Are you sure?",
            text: "You will not be able to recover deleted template!",
            type: "warning",
            showCancelButton: true,
            confirmButtonClass: "btn-danger",
            confirmButtonText: "Yes, delete it!",
            cancelButtonText: "Cancel",
            closeOnConfirm: false,
            closeOnCancel: false
          },
        function(isConfirm) { 
            
            //send ajax request for detele category action
            if (isConfirm) {
                swal("Deleted!", "Your template has been deleted.", "success");
                $.ajax({
                    url:"/company/delete_template/",
                    headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                    type:'POST',
                    contentType: 'application/json; charset=UTF-8',
                    data: JSON.stringify(deletetemplate),
                    error: function (request, status, error) {
                          alert(error);
                    }
               }).done(function(response){
                if(response.status=='True'){
                    swal("Deleted!", "Your category has been deleted.", "success");
                    remvoeEle.remove();
                    getCurrentRow.remove();
                }
                else if(response.status=='replica'){
                    swal("Replica!", "Your Template dose not delete.", "warning");
                }
                
               });
                
                
            } else {
                swal("Cancelled", "Your template is safe :)", "error");
            }
        });
    })


    
    $(document).mouseup(function(e){ //disable category editing
        var container = $(".es-subtitle");
        // if the target of the click isn't the container nor a descendant of the container
        if (!container.is(e.target) && container.has(e.target).length === 0) 
        {
            
            container.attr('readonly','');
            container.removeClass('changeTitle');
        }
    });

    $(document).on('click','#saveStageItem',function(){ //add main stage
        var getNewStageTitle = $('.stage-title').val();
        //add ajex req. to save new stage
        if(getNewStageTitle !== ''){
            var newStageListView = `<div class="collapse_parent_tab">
                                    <div class="collapse_title">
                                        <lable>`+getNewStageTitle+`</lable>
                                        <span class="toggle-arrows"></span>
                                    </div>
                                    <ul class="nav categoryListOftab panel-tabs">
                                        <li>
                                            <div class="addmore-clone__section">
                                                <button type="button" class="btn btn-sm btn-outline-light rounded-20 text-capitalize addmore-tab">
                                                    <i class="fe fe-plus"></i>add category
                                                </button>
                                            </div>
                                        </li>
                                    </ul>
                                </div>`;
            $(".collapes_wrapper").append(newStageListView);
            $("#closeFormModal").trigger('click');
        }else{
            $('.stage-title').addClass('warning-act');
            setTimeout(function(){
                $('.stage-title').removeClass('warning-act')
            },1500)
        }
    })
//    $("#saveNewTempItem").on('click',function(){//add ajax request and save add new template data
//        var stage_id = $('#newTemplateModal').find('.select-new-stage-list :selected').val();
//        var category_id = $('#newTemplateModal').find('.select-new-category-list :selected').val();
//        var template_name=$('#newTemplateModal').find('.select-new-template-name').val();
//        var template_discriiption=$('#newTemplateModal').find('.select-new-template-description').val();
//        createtemplate={'stage_id':stage_id,'category_id':category_id,'template_name':template_name,'template_discriiption':template_discriiption}
//        if(stage_id==''){
//            $('.select-new-stage-list').after('<p class="msg alert-danger">selected field is required.</p>')
//        }
//        else if(category_id=='')
//        {
//            $('.select-new-category-list').after('<p class="msg alert-danger">selected field is required.</p>')
//        }
//        else if(template_name==''){
//            $('.select-new-template-name').after('<p class="msg alert-danger">template name field is required.</p>')
//        }
//        else if(template_discriiption=='')
//        {
//            $('.select-new-template-description').after('<p class="msg alert-danger">template discription field is required.</p>')
//        }
//        else{
//                $.ajax({
//                        url:"/company/create_template/",
//                        headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
//                        type:'POST',
//                        contentType: 'application/json; charset=UTF-8',
//                        data: JSON.stringify(createtemplate),
//                        error: function (request, status, error) {
//                            alert(error);
//                        }
//                }).done(function(response){
//                    response= JSON.parse(response);
//                    if(response['status']==true){
//                        $("#closetempModal").trigger('click');
//                        window.location.href=response['url']
//                    }
//                    //    else{
//                    //     swal("Updated!", "Your category is safe.", "error");
//                    //    }
//                });
//        }
//
//        setTimeout(function(){
//            $('.msg').remove();
//        },3000)
//
//    })

    $('.print-action').on('click',function(){ //print preview action
        console.log('print preview action') 
    })
    $('.print-action').on('click',function(){ //toggle table nav-list
        console.log('toggle table nav-list') 
    })
    $('.print-action').on('click',function(){ //toggle table nav-list
        console.log('toggle table nav-list') 
    })
  
})

function initDomElement(){
   //add code when render on page load
   defaultActiveTab();
}

function defaultActiveTab(){
    var activeFirstTab = $(".collapes_wrapper .collapse_parent_tab:first-child");
    activeFirstTab.find('.collapse_title').trigger('click');
    activeFirstTab.find('.categoryListOftab li:first-child a').trigger('click')
    activeFirstTab.find('.categoryListOftab li:first-child .catActionBtns').addClass('bg-act');
}
function searchFilterBox(){ //search filter 
   var getListSearchBox =  $(document).find('#example1_filter');
   $(document).find('.fx-search-view').append(getListSearchBox);
}

function siblingTabClose(){
   // if(showFlag){
        $(".categoryListOftab li").each(function(){
            if($(this).find('a').hasClass('active')){
                $(this).find('a').removeClass('active')
            }
        })
  //  }
}



$('.select-new-stage-list').on('change', function () {
    var selectVal =this.selectedOptions[0].value;
    $('.select-new-category-list').children().remove().end().append('<option label="select category" selected disabled></option>') ;
    $.ajax({
        url:"/company/get_category/",
        headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
        type:'POST',
        contentType: 'application/json; charset=UTF-8',
        data: JSON.stringify({'stage_id':selectVal}),
        error: function (request, status, error) {
              alert(error);
        }
   }).done(function(response){
    //    console.log(response)
    response=JSON.parse(response)
       if(response['status']==true){
        category=JSON.parse(response['category_get'])
        category.forEach(element => {
            console.log(element['pk'],element['fields']['name'])
            $('.select-new-category-list').append($("<option></option>").attr("value", element['pk']).text(element['fields']['name'])); 
        });
           
       }
       else{
        swal("Get!", "Your category is safe.", "error"); 
       }
   });




});