var currentElement = ""
var currentElementParent = ""
$(document).ready(function(){

    var matchingKey = 'single';

    phaseOneData = false;

    var iniListCount = 1;

    /** check localDB and Category List**/
    setInterval(function(){ //sync within 700ms
        storageVisible();
    }, 700);

    checkJrcCatList = get_jcrData()

    console.log('checkJrcCatList in document ready',checkJrcCatList)

    jcrTemplateUpdate();

 $(".colaps-tab").click(function(){ //colapse-active

        console.log("before click ",currentElementParent)
        $(document.getElementById(currentElementParent)).trigger("dblclick")
        currentElement =""
        currentElementParent = ""
        var showSavedListTotal = 0;
        var getGTC = $(this).find('.badge').data('poc');
        subCatClone = `<div class="sub-que__wrapper">
                    <p class="rt-remove-form rounded-10"><i class="typcn typcn-delete"></i></p>
                    <div class="sample__form bd bd-10 rounded-20">
                    <div class="upper__section">
                        <form action="" class="upper-top__text-feilds" id="addFeild">
                            <div class="add-quest-textarea">
                                <input type="number" value="" hidden readOnly name="q_add_id" class="q_add_id">
                                <input type="text" placeholder="write something" value="" name="input_text_one" class="upper-ls_full_text bd bd-0 rounded-10">
                                <div class="sfx-input quest-percent-tab" data-suffix="%">
                                <input type="number" value="" name="que-percent" class="sl-feild2 bd-0 sub-cat-num" oninput="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength);" maxlength="3">
                                </div>
                            </div>
                            <div class="xs-col-2">
                                <input name="form-category" type="radio" value="single" checked><span>single</span>
                                <input name="form-category" type="radio" value="multi"><span>multiple</span>
                            </div>
                        </form>
                    </div>
                    <ul class="lower_section"></ul>
                    <div class="split_btn-bottom badge badge-outline-light">
                        <span class="add-clone">
                        <i class="si si si-plus"></i> Add More
                        </span>
                    </div>
                    <ul class="clone-listing" style="display:none;">
                        <li class="show_list bd bd-2 rounded-20">
                            <input type="number" value="" hidden readOnly name="detail_id" class="detail_id">
                            <input type="text" value="" name="lang-1" class="sl-feild1 bd-0 rounded-10 sub-cat-title">
                            <div class="sfx-input" data-suffix="%">
                                <input type="number" value="" name="lang" class="sl-feild2 bd-0 sub-cat-num" oninput="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength);" maxlength = "3">
                            </div>
                            <button class="btn btn-outline-danger btn-icon sl-action-btn btn-icon bd-0">
                            <i class="typcn typcn-trash"></i>
                            </button>
                        </li>
                    </ul>
                    </div>
                        <span class="split__half-circle"><img src="../../assets/img/circle-edge.png"></span>
                    </div>`;

        var all_que_wrappers = $(".sub-que__wrapper").remove()
        // all_que_wrappers.each(function(index){
        //     all_que_wrappers[index].remove()
        // })
        $(".jcr-child3__categorry-form").prepend(subCatClone)

        $(".lower_section").html("");
        if(getGTC > '0'){
            var createFirstCloneList = $(".clone-listing li").clone().attr('class', 'show_list bd bd-2 rounded-20 xs-clone clone-1');
            $(".inner_form-container, .saveActionBtn").show();
            $(".notfound__layout").hide();
            var getTabId = $(this).attr('id');
            $(this).closest('.left-col__list').addClass('lls-active');
            $(".lavel-2 li").removeClass('colapse-active');
            $('.colaps-head-1').removeClass('active_batch'); 
            $(this).nextAll('li').find(".lavel-3 li").hide();
            $(this).prevAll('li').find(".lavel-3 li").hide();
            $(this).nextAll('li').find("i").attr('class','si si-plus');
            $(this).prevAll('li').find("i").attr('class','si si-plus');
            $(this).find('.colaps-head-1').addClass('active_batch');
            
            if($(this).find("i").hasClass('si-plus')){
                $(this).addClass('colapse-active');
                $(this).find(".lavel-3 li").show();
                $(this).find("i").attr('class','si si-minus');
            }else{
                $(this).removeClass('colapse-active');
                $(this).find(".lavel-3 li").hide();
                $(this).find("i").attr('class','si si-plus');
            }
            
            
            $('.left_section').each(function(){$(this).find('input').val('');});
            resetChildClonelist({'reset':true,'delete':true});
            $('.inner_form-container,.bottom_gbli').addClass('act-rightList');
            $('.form_model').attr('data-item',getTabId);
            $(".lower_section").append(createFirstCloneList);
        }else{
           $(".lower_section").html("");
           $(".inner_form-container, .saveActionBtn").hide();
           $(".lavel-2 li").removeClass('colapse-active');
           $('.colaps-head-1').removeClass('active_batch');
           $(".lavel-2 li").find("i").attr('class','si si-plus'); 
           $(".lavel-3 li").hide();
           $(this).addClass('colapse-active');
           $(this).find('.colaps-head-1').addClass('active_batch empty-list');
           $(".notfound__layout").show(function(){
               $(this).html('');
               html = '';
               html += '<div class="alert alert-danger mg-b-0" role="alert"><button aria-label="Close" class="close" data-dismiss="alert" type="button"><span aria-hidden="true">&times;</span></button><strong>Sorry!</strong> </div>';
               $(".notfound__layout").append(html);
           });
        }
    })

    $(document).on('click','.add-clone', function(){ //create new colne of right col child-List
        var subCatInputPercentValidationKey = true;
        var sumOfmultiOptionValues = 0;
        var checkMetchingOfSelector = $(this).closest('.sample__form').find(".upper__section .xs-col-2 input[name='form-category']:checked").val();
        
        //addCloneOfList(showCurrentList);
        getSubListTotal = 0;
        var countNum;
        var createFirstCloneList = "";
        var cloneListView = `<li class="show_list bd bd-2 rounded-20 xs-clone">
                            <input type="number" value="" hidden readOnly name="detail_id" class="detail_id">
                            <input type="text" value="" name="lang-1" class="sl-feild1 bd-0 rounded-10 sub-cat-title">
                            <div class="sfx-input" data-suffix="%">
                                <input type="number" value="" name="lang" class="sl-feild2 bd-0 sub-cat-num" oninput="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength);" maxlength = "3">
                            </div>
                            <button class="btn btn-outline-danger btn-icon sl-action-btn btn-icon bd-0">
                                <i class="typcn typcn-trash"></i>
                            </button>
                        </li>`;
   //getListLength = $('.lower_section li').length;
   var getCurrentListItem = $(this).parent().prev('.lower_section');
   var getListLength = getCurrentListItem.find('li').length;
   
   if(getListLength == '0'){
        getCurrentListItem.append(cloneListView);
   }else{
        getCurrentListItem.find('li').each(function(indxOfCount){
            var self = $(this);
            var checkPrevLiVal = getCurrentListItem.find('li').eq(indxOfCount).find(".sub-cat-num").val();
            getSubListTotal += Number(self.find(".sub-cat-num").val())
            console.log(checkPrevLiVal)
            if( checkPrevLiVal !== '0' && checkPrevLiVal !== '' && typeof(checkPrevLiVal) !== 'undefined'){
                subCatInputPercentValidationKey = true;
                sumOfmultiOptionValues += parseInt(checkPrevLiVal);
                self.find(".sub-cat-num").addClass('validShadow');
                setTimeout(function(){self.find(".sub-cat-num").removeClass('validShadow'); },2500);
            }else{
                subCatInputPercentValidationKey = false;
                self.find(".sub-cat-num").addClass('ntValidShadow');
                setTimeout(function(){self.find(".sub-cat-num").removeClass('ntValidShadow'); },2500);
                return false
            }

            })
            console.log("the subCatInputPercentValidationKey is ",subCatInputPercentValidationKey);
            console.log("the sumOfmultiOptionValues is ",sumOfmultiOptionValues);
            if(checkMetchingOfSelector == 'single'){
                if(subCatInputPercentValidationKey){
                    var single_value_list=[];
                    $(getCurrentListItem.find(".show_list input[name='lang']")).each(function(){
                        single_value_list.push(this.value); 
                    });
                    
                    if(jQuery.inArray("100", single_value_list)!== -1) {
                        console.log(single_value_list)
                        var showMsg = "The grand total must not exceed 100%";
                        snakBarShow(showMsg);
                    } else {
                        getCurrentListItem.append(cloneListView);
                    }
                   
                }
            }
            
            console.log("subCatInputPercentValidationKey",subCatInputPercentValidationKey)
            console.log("sumOfmultiOptionValues",sumOfmultiOptionValues)
            console.log(" type sumOfmultiOptionValues",typeof(sumOfmultiOptionValues))
            console.log("is less than 100",sumOfmultiOptionValues < 100)
            if(checkMetchingOfSelector == 'multi'){
                if(subCatInputPercentValidationKey){                   
                    if(sumOfmultiOptionValues < "100")
                    {
                        console.log('in')
                        getCurrentListItem.append(cloneListView);
                    }
                    else
                    {
                        // console.log("please fill out the remaining fields first!!!!")
                        var showMsg = "The grand total must not exceed 100%";
                        snakBarShow(showMsg);
                    } 
                }
                else{
                    // console.log('complete multi ')
                    // console.log("please fill out the multi fields first")
                    console.log('else false')
                    var showMsg = "Please fill out the remaining fields first!!!!";
                    snakBarShow(showMsg);
                    
                }
                console.log('else exit')
            }
         
        }

    });

    $("#rmChildList").on('click',function(){ //JCR Parent From-Tab Close button event
        var flag = {'reset':true,'delete':true};
        resetChildClonelist(flag);
        $.ajax({
            url:"/company/remove_jcr/",
            headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
            type:'POST',
            contentType: 'application/json; charset=UTF-8',
            data: JSON.stringify({'deleteid':$("input[name='add_id']").val()}),
            error: function (request, status, error) {
                  alert(error);
            }
       }).done(function(response){
//                        console.log('response >>>>>>>>>',response);
           form1_response_data = response;
//            $(".percent-box").val('');
           formSwitch(true);
           ajaxLoader(false);
           checkJrcCatList=JSON.parse(response['getStoreData'])
           listSync()
       });
        $('.left_section').each(function(){
            $(this).find('input').val('');
        });
        $('.upper__section').each(function(){
            $(this).find('input').val('');
        });
        
    });

    $(document).on('click','.rt-remove-form',function(){ //JCR Child From-Tab Close button event
        var numOfsubList = $(this).closest('.jcr-child3__categorry-form').find('.sub-que__wrapper').length;
        var hiddenInputVal = $(this).next('.sample__form').find('.q_add_id').val()
       
        if(numOfsubList > '1'){
            $(this).closest('.sub-que__wrapper').remove()
        }
    
        $.ajax({
            url:"/company/remove_sub_jcr/",
            headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
            type:'POST',
            contentType: 'application/json; charset=UTF-8',
            data: JSON.stringify({'deleteid':hiddenInputVal }),
            error: function (request, status, error) {
                  alert(error);
            }
       }).done(function(response){
//                        console.log('response >>>>>>>>>',response);
           form1_response_data = response;
//            $(".percent-box").val('');
           formSwitch(true);
           checkJrcCatList=JSON.parse(response['getStoreData'])
           listSync()
           ajaxLoader(false);



       });
    });

    $(".remove-form").on('click',function(){ //JCR Details Main Form Layout Close button Event
        var flag = {'reset':true,'delete':true};
        resetChildClonelist(flag);
        $('.inner_form-container,.bottom_gbli').removeClass('act-rightList');
        $(".left-col__list").removeClass("lls-active");
        if($(".colaps-head-1").is(".active_batch")){
            $(".colaps-head-1").removeClass('active_batch');
        }
        $.ajax({
            url:"/company/remove_jcr/",
            headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
            type:'POST',
            contentType: 'application/json; charset=UTF-8',
            data: JSON.stringify({'deleteid':$("input[name='add_id']").val()}),
            error: function (request, status, error) {
                  alert(error);
            }
       }).done(function(response){
//                        console.log('response >>>>>>>>>',response);
           form1_response_data = response;
//            $(".percent-box").val('');
           formSwitch(true);
           checkJrcCatList=JSON.parse(response['getStoreData'])
           listSync()
           ajaxLoader(false);



       });
    });
   
    $(document).on('click','.sl-action-btn',function(){
        var delete_item= '';
        var getListLength = $(this).closest('.lower_section').find('li.show_list').length-1;
        var add=$(this).closest('.lower_section');
        if($(this).parent('li').hasClass('xs-clone')){
         delete_item=$(this).parent('li').find('[name=detail_id]').val()
         $(this).parent('li').remove();
        }
        if($(this).parent('li').length < 5){
            
            $(".sample__form .split_btn-bottom").show();
        }
        $.ajax({
            url:"/company/remove_jcr/",
            headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
            type:'POST',
            contentType: 'application/json; charset=UTF-8',
            data: JSON.stringify({'deleteid':delete_item }),
            error: function (request, status, error) {
                  alert(error);
            }
       }).done(function(response){
//                        console.log('response >>>>>>>>>',response);
           form1_response_data = response;
           formSwitch(true);
           checkJrcCatList=JSON.parse(response['getStoreData'])
           listSync()
           ajaxLoader(false);
          
           if(getListLength==0){
            var cloneListView = `<li class="show_list bd bd-2 rounded-20 xs-clone">
                                    <input type="number" value="" hidden readOnly name="detail_id" class="detail_id">
                                    <input type="text" value="" name="lang-1" class="sl-feild1 bd-0 rounded-10 sub-cat-title">
                                    <div class="sfx-input" data-suffix="%">
                                        <input type="number" value="" name="lang" class="sl-feild2 bd-0 sub-cat-num" oninput="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength);" maxlength = "3">
                                    </div>
                                    <button class="btn btn-outline-danger btn-icon sl-action-btn btn-icon bd-0">
                                        <i class="typcn typcn-trash"></i>
                                    </button>
                                </li>`;
            add.append(cloneListView)
                                
           }

       });
     })

    $('.next-tab').on('click',function(){ //JCR right form Next Button click event
        showEvent = 'next';
        iniListCount
        paginateTabs(showEvent);
    })

    $('.prev-tab').on('click',function(){ //JCR right form Previous Button click event
        showEvent = 'prev';
        paginateTabs(showEvent);
    });

    $("#nextFormActionBtn").on('click', function(){
        phaseOneFormValidation();
    })
    $(".percent-box").on('keyup change',function(){ //change and keyup action of phase 1 form
        flagOfActiveButton = false;
         var totalCountOfPercents = 0;
         //var getCurrentEle = $(this);
         var getValOfEle = $(this).val();
         if(getValOfEle){
             $(".psf_row").each(function(){
                if($(this).find(".percent-box").val())
                {
                    totalCountOfPercents +=  Number($(this).find(".percent-box").val());
                }
                else
                {
                    totalCountOfPercents =  0
                    return false
                }
                
             })
            if(totalCountOfPercents == '100'){
                flagOfActiveButton = true;
                phaseOneData = true;
                console.log(totalCountOfPercents)
                enableNextButton(flagOfActiveButton);
            }else{
                flagOfActiveButton = false;
                console.log('not eqal'+totalCountOfPercents)
                enableNextButton(flagOfActiveButton);
            }
         }else{
            flagOfActiveButton = false;
            enableNextButton(flagOfActiveButton);
            console.log(getValOfEle); 
         }
    })
  
    $(document).on("click",".lavel-3 li",function(){ //JCR left-subCategoty slide-toggle 
        self = $(this);
        // console.log("the sidebar ele is",self.attr("data-item"))
        currentElement = self.attr("data-item").toLowerCase()
        currentElementParent = self.closest(".colaps-tab").attr("id")
        console.log("the current element is",currentElement)
        console.log("the current elements parent is",currentElementParent)

        $(".lavel-3 li").show();
        self.closest('.colaps-tab').prevAll('li .lavel-3 li').hide();
        self.closest('.colaps-tab').nextAll('li .lavel-3 li').hide();
        $(this).closest('.colaps-tab').find('i').attr('class','si si-minus');
        getIdOfSubCat = $(this).data('item');
        getMainCatId = $(this).closest(".colaps-tab").attr("id");
        populateSubCatItems({"parentKey":getMainCatId,"subCatKey":getIdOfSubCat});
    })

    $("#sub_clone").on('click',function(){
      var sampleItemCount = 0;
      var inputNotNull = true;
       var subCatClone = '';
       var checkTotalSubcatTotalcval = $(this).closest('.jcr-child3__categorry-form').find('.sub-que__wrapper');
       var checkSubCatListSize = $(this).closest('.jcr-child3__categorry-form').find('.sub-que__wrapper').length;
       $.each(checkTotalSubcatTotalcval, function(i){
        if(checkTotalSubcatTotalcval.eq(i).hasClass('sub-que__wrapper')){
            console.log("Get percent of subcate>>",checkTotalSubcatTotalcval.eq(i).find('.add-quest-textarea .sl-feild2 ').val() )
           if(checkTotalSubcatTotalcval.eq(i).find('.add-quest-textarea .sl-feild2 ').val() !== ""){
                sampleItemCount += parseInt(checkTotalSubcatTotalcval.eq(i).find('.add-quest-textarea .sl-feild2').val());
                inputNotNull = false;
            }else{
                inputNotNull = true;
                console.log("check before value>>"+checkTotalSubcatTotalcval.eq(i).find('.add-quest-textarea .sl-feild2').val())
                if(!checkTotalSubcatTotalcval.eq(i).find('.add-quest-textarea .sl-feild2').val()){
                    // alert('blank')
                    checkTotalSubcatTotalcval.eq(i).find('.add-quest-textarea .sl-feild2').addClass('ntValidShadow')
                    setTimeout(function(){
                        checkTotalSubcatTotalcval.eq(i).find('.add-quest-textarea .sl-feild2 ').removeClass('ntValidShadow');
                    },2500)
                }
                return false;
            }
        }
          //console.log("check question percent->>",sampleItemCount)
       })
       console.log(inputNotNull);
       console.log('check input value of box',sampleItemCount)
       if(sampleItemCount < 100 && !sampleItemCount == 0 && !inputNotNull){
                if(checkSubCatListSize <= 3){
                    subCatClone = `<div class="sub-que__wrapper">
                    <p class="rt-remove-form rounded-10"><i class="typcn typcn-delete"></i></p>
                    <div class="sample__form bd bd-10 rounded-20">
                    <div class="upper__section">
                        <form action="" class="upper-top__text-feilds" id="addFeild">
                            <div class="add-quest-textarea">
                                <input type="number" value="" hidden readOnly name="q_add_id" class="q_add_id">
                                <input type="text" placeholder="write something" value="" name="input_text_one" class="upper-ls_full_text bd bd-0 rounded-10">
                                <div class="sfx-input quest-percent-tab" data-suffix="%">
                                <input type="number" value="" name="que-percent" class="sl-feild2 bd-0 sub-cat-num" oninput="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength);" maxlength="3">
                                </div>
                            </div>
                            <div class="xs-col-2">
                                <input name="form-category" type="radio" value="single" checked><span>single</span>
                                <input name="form-category" type="radio" value="multi"><span>multiple</span>
                            </div>
                        </form>
                    </div>
                    <ul class="lower_section"></ul>
                    <div class="split_btn-bottom badge badge-outline-light">
                        <span class="add-clone">
                        <i class="si si si-plus"></i> Add More
                        </span>
                    </div>
                    <ul class="clone-listing" style="display:none;">
                        <li class="show_list bd bd-2 rounded-20">
                            <input type="number" value="" hidden readOnly name="detail_id" class="detail_id">
                            <input type="text" value="" name="lang-1" class="sl-feild1 bd-0 rounded-10 sub-cat-title">
                            <div class="sfx-input" data-suffix="%">
                                <input type="number" value="" name="lang" class="sl-feild2 bd-0 sub-cat-num" oninput="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength);" maxlength = "3">
                            </div>
                            <button class="btn btn-outline-danger btn-icon sl-action-btn btn-icon bd-0">
                            <i class="typcn typcn-trash"></i>
                            </button>
                        </li>
                    </ul>
                    </div>
                        <span class="split__half-circle"><img src="../../assets/img/circle-edge.png"></span>
                    </div>`;
                $(this).closest('.jcr-child3__categorry-form').find('.sub-que__wrapper').last().after(subCatClone);
            }else{
                
               var msg = "You have already done of question fields"
               snakBarShow(msg)
            }
       }else{
                
        var msg = "You have already done of question fields"
        setTimeout(function(){ $(this).closest('.jcr-child3__categorry-form').find('.sub-que__wrapper sl-feild2').addClass('ntValidShadow'); },0);
                    
        snakBarShow(msg)
        setTimeout(function(){ $(this).closest('.jcr-child3__categorry-form').find('.sub-que__wrapper sl-feild2').removeClass('ntValidShadow'); },2500);

       }
    })

    $(".add_parcent").on("change", function(){ //JCR RightSide form-item (Parent Category)
        self = $(this);
        var colPercent = 0;
        var catTotal = 0;
        var formType = $(this).closest('.form_model').attr('data-item');
        $(".lavel-2 li").each(function(){
            if($(this).attr('id') == formType){
                $(this).find('.lavel-3 li').each(function(){
                 colPercent += Number($(this).attr('data-percent'));
                })
            }
        })
        currentValue = $(this).val();
        setTimeout(function(){
         catTotal = parseInt(currentValue) + colPercent;
         if(catTotal <= 100){
            console.log('complete'+ catTotal);
            self.addClass('validShadow');
            setTimeout(function(){self.removeClass('validShadow'); },2500);
         }else{
             console.log('overflow'+ catTotal)
             self.addClass('ntValidShadow');
             setTimeout(function(){self.removeClass('ntValidShadow'); },2500);
         }
        },700)
    })

    listSync();//page load to update sub-category-list

    //ADDED ON 12/9/2021

    $(document).on("change","input[name='form-category']",function(){
        var all_options = $(this).closest(".sample__form").find('.show_list')

        console.log("the closest form box is ",$(this).closest(".sample__form").find('.show_list'))
        $.each(all_options,function(i){
            all_options.eq(i).remove()
        })
        $(this).closest(".sub-que__wrapper").find(".add-clone").trigger("click")
    })
})




/**functions**/
var dbConnection = false;
var newId = (function() {
    var id = 1;
    return function() {
        return id++;
    };
}());


function addCloneOfList(getCurrentListItem){ //Generate clone of Child Category list.
   getSubListTotal = 0;
   var countNum;
   var createFirstCloneList ="";
   var cloneListView = `<ul class="show_list bd bd-2 rounded-20 xs-clone clone-1">
                        <li class="show_list bd bd-2 rounded-20">
                            <input type="number" value="" hidden readOnly name="detail_id" class="detail_id">
                            <input type="text" value="" name="lang-1" class="sl-feild1 bd-0 rounded-10 sub-cat-title">
                            <div class="sfx-input" data-suffix="%">
                                <input type="number" value="" name="lang" class="sl-feild2 bd-0 sub-cat-num" oninput="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength);" maxlength = "3">
                            </div>
                            <button class="btn btn-outline-danger btn-icon sl-action-btn btn-icon bd-0">
                                <i class="typcn typcn-trash"></i>
                            </button>
                        </li>
                        </ul>`;
   //getListLength = $('.lower_section li').length;
   getListLength = getCurrentListItem.length;
   if(getListLength == '0'){
        initCloneList = $(".clone-listing li").clone().attr("class", "show_list bd bd-2 rounded-20 xs-clone clone-1");
        $(".lower_section").append(initCloneList);
   }else{
    getCurrentListItem.each(function(indxOfCount){
        var self = $(this);
        checkPrevLiVal =  getCurrentListItem.eq(indxOfCount).find(".sub-cat-num").val();
        getSubListTotal += Number(self.find(".sub-cat-num").val())
        if( checkPrevLiVal !== "0" && checkPrevLiVal !== ""){
            countNum = Number(indxOfCount + 1)
            if(getListLength == countNum){
                if(getSubListTotal <= 100){
                    updateLsCount = parseInt(countNum + 1);
                    classItemList = 'show_list bd bd-2 rounded-20 xs-clone clone-'+updateLsCount;
                    createFirstCloneList = self.last().clone().attr("class", classItemList)
                    createFirstCloneList.find('[type=text]').val('');
                    createFirstCloneList.find('[type=number]').val('');
                    $(".lower_section").append(createFirstCloneList);
                    self.find(".sub-cat-num").addClass('validShadow');
                    setTimeout(function(){self.find(".sub-cat-num").removeClass('validShadow'); },2500);
                }else{
                    showMsg = "Grand total should be 100 in your selected all inputs."
                    snakBarShow(showMsg);
                }
            }
        }else{
            self.find(".sub-cat-num").addClass('ntValidShadow');
            setTimeout(function(){self.find(".sub-cat-num").removeClass('ntValidShadow'); },2500);
        }
       })
   }
}

function resetChildClonelist(data){ //SubCategoty form clean and delete
    if(data.reset){
        $('.sample__form').each(function(){
            if(!$(this).find('input').attr('type') == 'radio'){
                $(this).find('input').val('');
            }
        });
    }
    if(data.delete){
        $('.lower_section li').each(function(){
            if($(this).hasClass('xs-clone')){
                console.log("in delete ,the value of this is",$(this))
                $(this).remove()
            }
        });
    }
}
function paginateTabs(actionType){ //switch form/page activity on next/prev. button
    if(actionType == 'next'){
      getCurrentActTab =  $('.lavel-2').find('.active_batch');
      checkCurrentPos = getCurrentActTab.closest('li').data('lscat');
      if(checkCurrentPos == "list-2"){
          console.log('finish')
      }
      getCurrentActTab = getCurrentActTab.closest('li').next().find('a').trigger('click');
      //console.log(getCurrentActTab);
    }
    if(actionType == 'prev'){
        getCurrentActTab =  $('.lavel-2').find('.active_batch');
        checkCurrentPos = getCurrentActTab.closest('li').data('lscat');
        if(checkCurrentPos == "list-0"){
            console.log('Go to Phase -1 Page');
            formSwitch(false);
        }
        getCurrentActTab = getCurrentActTab.closest('li').prev().find('a').trigger('click');
        //console.log(getCurrentActTab);
    }
}

function getParentItemData(setCatData){ //Collect Main-Category item
    var data = {};
    var cateType = $('.mc-title').val();
    var catePercent  = $('.mc-num').val();
    var cateId  = $('.mc-num-id').val();
    if(cateType != '' ||  catePercent != ''){
        data.title = cateType;
        data.id=cateId;
        data.percent = catePercent;
        setCatData.push(data);
    }
    return setCatData;
}

function getChildItemData(queObjItems){
  //var queObjItems = [];
  var mainList = $(document).find('.jcr-child3__categorry-form .sub-que__wrapper');
  
  $.each(mainList, function(key){
    var childList = mainList.eq(key).find('.lower_section li')
    var queryText =  mainList.eq(key).find('.upper-top__text-feilds .upper-ls_full_text').val();
    var queryId =  mainList.eq(key).find('.upper-top__text-feilds .q_add_id').val();
    console.log(mainList.eq(key).find('.upper-top__text-feilds .sub-cat-num').val())
    var queryPercent = mainList.eq(key).find('.upper-top__text-feilds .sub-cat-num').val()
    var querySelector = mainList.eq(key).find('.upper-top__text-feilds .xs-col-2 input[type="radio"]:checked').val()
    queObjItems.push({"question":queryText,"id":queryId,"q_percent":queryPercent,"matching":querySelector,"details":[]})
    $.each(childList,function(index){
        var subData = {};
        var subCatTitle = $(this).find('input:text').val();
        var subCatPercent = $(this).find('.sl-feild2').val();
        var subCatId = $(this).find('.detail_id').val();
        if(subCatTitle !== '' || subCatPercent !== ''){
            subData.title = subCatTitle;
            subData.percent = subCatPercent;
            subData.id=subCatId;
            queObjItems[key]['details'].push(subData)
            //setSubData.push(subData);
        }
    });
  })
  return queObjItems;
}

function saveFormItems(){
    // ajaxLoader(true);
    var checkEmptyFlag = checkFormDataCalucations()
    console.log(checkEmptyFlag)
    if(checkEmptyFlag == false)
    {
        console.log("innnnn")
        return false
    }
    
    setSubCatItems = []
    let getFormId = '';
    setMainCatItem = [];
    setSubCatItems = [];
    var addDetailsItem = []; 
    getFormId = $('.colaps-head-1.active_batch').closest('li').attr('id');
    getParentItemData(setMainCatItem);
    getChildItemData(setSubCatItems);
    console.log(getParentItemData)
    if(getFormId){
        if(!setMainCatItem.length == "0" && !setMainCatItem.length == "0"){
           switch(getFormId) {
                case "primary-list":
                    addDetailsItem.push({"keyId":getFormId},{"cat_type":setMainCatItem[0].title,"id":setMainCatItem[0].id,"cate_percent":setMainCatItem[0].percent,"cat_subtype":setSubCatItems});
                    console.log("==============================================")
                    console.log(addDetailsItem)
                    console.log(setMainCatItem[0].id)
                    AddJcrData(addDetailsItem);
                break;
                case "secondary-list":
                    addDetailsItem.push({"keyId":getFormId},{"cat_type":setMainCatItem[0].title,"id":setMainCatItem[0].id,"cate_percent":setMainCatItem[0].percent,"cat_subtype":setSubCatItems});
                    AddJcrData(addDetailsItem);
                break;
                case "objective-list":
                    addDetailsItem.push({"keyId":getFormId},{"cat_type":setMainCatItem[0].title,"id":setMainCatItem[0].id,"cate_percent":setMainCatItem[0].percent,"cat_subtype":setSubCatItems});
                    AddJcrData(addDetailsItem);
                break;
                default:
                    AddJcrData(addDetailsItem);
                console.log('key does not match to list');
            }
        }else{  
            console.log(setMainCatItem.length)
        }   
    }else{
        textMsg = "All input field is require.."
    }
    // ajaxLoader(false);

    subCatClone = `<div class="sub-que__wrapper">
    <p class="rt-remove-form rounded-10"><i class="typcn typcn-delete"></i></p>
    <div class="sample__form bd bd-10 rounded-20">
    <div class="upper__section">
        <form action="" class="upper-top__text-feilds" id="addFeild">
            <div class="add-quest-textarea">
                <input type="number" value="" hidden readOnly name="q_add_id" class="q_add_id">
                <input type="text" placeholder="write something" value="" name="input_text_one" class="upper-ls_full_text bd bd-0 rounded-10">
                <div class="sfx-input quest-percent-tab" data-suffix="%">
                <input type="number" value="" name="que-percent" class="sl-feild2 bd-0 sub-cat-num" oninput="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength);" maxlength="3">
                </div>
            </div>
            <div class="xs-col-2">
                <input name="form-category" type="radio" value="single" checked><span>single</span>
                <input name="form-category" type="radio" value="multi"><span>multiple</span>
            </div>
        </form>
    </div>
    <ul class="lower_section"></ul>
    <div class="split_btn-bottom badge badge-outline-light">
        <span class="add-clone">
        <i class="si si si-plus"></i> Add More
        </span>
    </div>
    <ul class="clone-listing" style="display:none;">
        <li class="show_list bd bd-2 rounded-20">
            <input type="number" value="" hidden readOnly name="detail_id" class="detail_id">
            <input type="text" value="" name="lang-1" class="sl-feild1 bd-0 rounded-10 sub-cat-title">
            <div class="sfx-input" data-suffix="%">
                <input type="number" value="" name="lang" class="sl-feild2 bd-0 sub-cat-num" oninput="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength);" maxlength = "3">
            </div>
            <button class="btn btn-outline-danger btn-icon sl-action-btn btn-icon bd-0">
            <i class="typcn typcn-trash"></i>
            </button>
        </li>
    </ul>
    </div>
        <span class="split__half-circle"><img src="../../assets/img/circle-edge.png"></span>
    </div>`;

$(".sub-que__wrapper").remove()

    $(".jcr-child3__categorry-form").prepend(subCatClone)

    // $(document.getElementById(currentElementParent)).trigger("dblclick")
    $(document.getElementById(currentElementParent)).trigger("click")
    $(document.getElementById(currentElementParent)).trigger("click")
    $(document.getElementById(currentElementParent)).trigger("click")
}

function queryLabelThired(){
    var firstCheckValue = $(".xs-col-2").hasClass('check__one');
    var firstCheckValue  = $(".xs-col-2").hasClass('check__two')
}

function storageVisible(){
    console.log(checkJrcCatList)
    if (checkJrcCatList !== null && localStorage.getItem('jrc_categories') !== null) {
    // if (localStorage.getItem('jcr_details') !== null && localStorage.getItem('jrc_categories') !== null) {
       dbConnection = true;
    } else {
        setNewArry = [{'key':'primary-list','addDetailsItem':[]},{'key':'secondary-list','addDetailsItem':[]},{'key':'objective-list','addDetailsItem':[]}];
        jrcCatList = [];
        localStorage.setItem("jrc_categories",JSON.stringify(jrcCatList));
        localStorage.setItem("jcr_details",JSON.stringify(setNewArry));
    }
}

function AddJcrData(getData){
    console.log(getData);
    var getKeyOfFormData = getData[0]['keyId'];
    // getStoreData = JSON.parse(localStorage.getItem("jcr_details"));
    var getStoreData = checkJrcCatList['getStoreData'];
    console.log("the getstoredata is",getStoreData)
    console.log("the  stringied getstoredata is",JSON.stringify( getStoreData))
    // alert(getKeyOfFormData);
    
    switch (getKeyOfFormData) {
    case getStoreData[0]['cat_name']:
        console.log("first list update  "+  getStoreData[0]['addDetailsItem'].length);
        if(getStoreData[0]['addDetailsItem'].length > 0){
            getStoreData[0]['addDetailsItem'].push(getData[1]);
            // localStorage.setItem("jcr_details",JSON.stringify(getStoreData))

            console.log("the stringigfied daaataaaaa isssss",  JSON.stringify({'getStoreData': getStoreData}))
            $.ajax({
                url:"/company/insert_jcr/",
                headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                type:'POST',
                contentType: 'application/json; charset=UTF-8',
                data: JSON.stringify({'getStoreData': getStoreData}),
                error: function (request, status, error) {
                      alert(error);
                }
           }).done(function(response){

               form1_response_data = response;
               formSwitch(true);
               checkJrcCatList=JSON.parse(response['getStoreData'])
               listSync()
               ajaxLoader(false);
            //    data=response['data'])
           });
            formCleanUp();
        }else{
            getStoreData[0]['addDetailsItem'].push(getData[1])
            console.log("the stringified data is",JSON.stringify({'getStoreData': getStoreData}))
            $.ajax({
                url:"/company/insert_jcr/",
                headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                type:'POST',
                contentType: 'application/json; charset=UTF-8',
                data: JSON.stringify({'getStoreData': getStoreData}),
                error: function (request, status, error) {
                      alert(error);
                }
           }).done(function(response){
                response1  = JSON.parse(response);
               console.log('insert jcr response 1',response1)
               response2 = JSON.parse(response1['getStoreData']);
               console.log('insert jcr response 2',response2['getStoreData'])
               form1_response_data = response;
   //            $(".percent-box").val('');
               formSwitch(true);
               checkJrcCatList = response2['getStoreData'];
               listSync()
               ajaxLoader(false);

           });
            // localStorage.setItem("jcr_details",JSON.stringify(getStoreData))
            formCleanUp();
        }
        break;
    case getStoreData[1]['cat_name']:
        //console.log("sec list update  "+  getStoreData[0]['addDetailsItem'].length);
        if(getStoreData[1]['addDetailsItem'].length > 0){
            getStoreData[1]['addDetailsItem'].push(getData[1]);
            // localStorage.setItem("jcr_details",JSON.stringify(getStoreData))
            console.log("the stringified data is",JSON.stringify({'getStoreData': getStoreData}))
            $.ajax({
                url:"/company/insert_jcr/",
                headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                type:'POST',
                contentType: 'application/json; charset=UTF-8',
                data: JSON.stringify({'getStoreData': getStoreData}),
                error: function (request, status, error) {
                      alert(error);
                }
           }).done(function(response){
               form1_response_data = response;
               formSwitch(true);
               checkJrcCatList=JSON.parse(response['getStoreData'])
               listSync()
               ajaxLoader(false);


           });
            formCleanUp();
        }else{
            getStoreData[1]['addDetailsItem'].push(getData[1])
            // localStorage.setItem("jcr_details",JSON.stringify(getStoreData))
            console.log("the stringified data is",JSON.stringify({'getStoreData': getStoreData}))

            $.ajax({
                url:"/company/insert_jcr/",
                headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                type:'POST',
                contentType: 'application/json; charset=UTF-8',
                data: JSON.stringify({'getStoreData': getStoreData}),
                error: function (request, status, error) {
                      alert(error);
                }
           }).done(function(response){
               form1_response_data = response;
               formSwitch(true);
               checkJrcCatList=JSON.parse(response['getStoreData'])
               listSync()
               ajaxLoader(false);


           });
            formCleanUp();
            //localStorage.setItem("jcr_details",JSON.stringify(getStoreData[1]['addDetailsItem'].push(getData))) 
        }
        break;
    case getStoreData[2]['cat_name']:
        console.log("third list update  "+  getStoreData[0]['addDetailsItem'].length);
        if(getStoreData[2]['addDetailsItem'].length > 0){
            getStoreData[2]['addDetailsItem'].push(getData[1]);
            // localStorage.setItem("jcr_details",JSON.stringify(getStoreData))
            console.log("the stringified data is",JSON.stringify({'getStoreData': getStoreData}))

            $.ajax({
                url:"/company/insert_jcr/",
                headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                type:'POST',
                contentType: 'application/json; charset=UTF-8',
                data: JSON.stringify({'getStoreData': getStoreData}),
                error: function (request, status, error) {
                      alert(error);
                }
           }).done(function(response){
               form1_response_data = response;
               formSwitch(true);
               checkJrcCatList=JSON.parse(response['getStoreData'])
               listSync()
               ajaxLoader(false);


           });
            formCleanUp();
        }else{
            getStoreData[2]['addDetailsItem'].push(getData[1])
            console.log(getStoreData)
            // localStorage.setItem("jcr_details",JSON.stringify(getStoreData))
            console.log("the stringified data is",JSON.stringify({'getStoreData': getStoreData}))

            $.ajax({
                url:"/company/insert_jcr/",
                headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                type:'POST',
                contentType: 'application/json; charset=UTF-8',
                data: JSON.stringify({'getStoreData': getStoreData}),
                error: function (request, status, error) {
                      alert(error);
                }
           }).done(function(response){
               form1_response_data = response;
               formSwitch(true);
               checkJrcCatList=JSON.parse(response['getStoreData'])
               listSync()
               ajaxLoader(false);


           });
            formCleanUp();
           //localStorage.setItem("jcr_details",JSON.stringify(getStoreData[1]['addDetailsItem'].push(getData)))
        }
        break;
    default:
        console.log("Sorry! key does not match to list");
        break;
    }
    listSync();
}

function listSync(){
    console.log('in list sync',checkJrcCatList);
    $(".colaps-tab .lavel-3").html('');
    if (checkJrcCatList['getStoreData'] !== "null") {
        // var showListItems = JSON.parse(localStorage.getItem("jcr_details"));
        //console.log(showListItems[0]['key']+'---'+showListItems[1]['key']+'---'+showListItems[2]['key'])
        var showListItems = checkJrcCatList['getStoreData'];

            console.log(showListItems)

        $.each(showListItems, function(iKey){
            console.log('showListItems[iKey].cat_name', showListItems[iKey].cat_name)
            switch(showListItems[iKey].cat_name) {
            case "primary-list":
                var checkList1 = showListItems[iKey]['addDetailsItem'];
                console.log('in primary', checkList1)
                      $.each(checkList1, function(i){
                        console.log(checkList1[i].cat_type+"----"+checkList1[i].cate_percent);
                        $("#primary-list .lavel-3").append("<li style='display: none;' data-percent="+checkList1[i].cate_percent+" data-item="+checkList1[i].cat_type+">"+checkList1[i].cat_type+"<span class='badge badge-success'>"+checkList1[i].cate_percent+"%</span></li>");
                      })
                break;
            case "secondary-list":
                var checkList1 = showListItems[iKey]['addDetailsItem'];
                    $.each(checkList1, function(i){
                        //console.log(checkList1[i].cat_type+"----"+checkList1[i].cate_percent);
                        $("#secondary-list .lavel-3").append("<li style='display: none;' data-percent="+checkList1[i].cate_percent+" data-item="+checkList1[i].cat_type+">"+checkList1[i].cat_type+"<span class='badge badge-success'>"+checkList1[i].cate_percent+"%</span></li>");
                    })
                break;
            case "objective-list":
                var checkList1 = showListItems[iKey]['addDetailsItem'];
                    $.each(checkList1, function(i){
                        //console.log(checkList1[i].cat_type+"----"+checkList1[i].cate_percent);
                        $("#objective-list .lavel-3").append("<li style='display: none;' data-percent="+checkList1[i].cate_percent+" data-item="+checkList1[i].cat_type+">"+checkList1[i].cat_type+"<span class='badge badge-success'>"+checkList1[i].cate_percent+"%</span></li>");
                    });
                break;
            default:
            console.log('key does not match to list');
        }
        })

//        showListItems.forEach(element => {
//        switch(element['cat_name']) {
//            case "primary-list":
//                var checkList1 = showListItems[0]['addDetailsItem'];
//                $.each(checkList1, function(i){
//                    console.log(checkList1[i].cat_type+"----"+checkList1[i].cate_percent);
//                    $("#primary-list .lavel-3").append("<li style='display: none;' data-percent="+checkList1[i].cate_percent+" data-item="+checkList1[i].cat_type+">"+checkList1[i].cat_type+"<span class='badge badge-success'>"+checkList1[i].cate_percent+"%</span></li>");
//                })
//            break;
//            case "secondary-list":
//                var checkList1 = showListItems[1]['addDetailsItem'];
//                $.each(checkList1, function(i){
//                    //console.log(checkList1[i].cat_type+"----"+checkList1[i].cate_percent);
//                    $("#secondary-list .lavel-3").append("<li style='display: none;' data-percent="+checkList1[i].cate_percent+" data-item="+checkList1[i].cat_type+">"+checkList1[i].cat_type+"<span class='badge badge-success'>"+checkList1[i].cate_percent+"%</span></li>");
//                })
//            break;
//            case "objective-list":
//                var checkList1 = showListItems[2]['addDetailsItem'];
//                $.each(checkList1, function(i){
//                    //console.log(checkList1[i].cat_type+"----"+checkList1[i].cate_percent);
//                    $("#objective-list .lavel-3").append("<li style='display: none;' data-percent="+checkList1[i].cate_percent+" data-item="+checkList1[i].cat_type+">"+checkList1[i].cat_type+"<span class='badge badge-success'>"+checkList1[i].cate_percent+"%</span></li>");
//                })
//            break;
//            default:
//            console.log('key does not match to list');
//        }
//        });
    }
}

function updateDateCategory(getCateList){ //update Main Category listing
    newListItems = [];
    console.log('in updateDateCategory getCateList', getCateList)
    $.each(getCateList, function(i){
        html = "";
        console.log('getCateList[i]', getCateList[i])
        console.log('getCateList[i]name', getCateList[i]['cat_name'])
        html += '<li id="'+getCateList[i]['cat_name']+'" class="colaps-tab branch" data-lscat="list-'+i+'">';
        switch(getCateList[i]['cat_name']) {
            case "primary-list":
                html += '<i class="si si-plus"></i><a href="javascript:void(0)" class="colaps-head-1">Primary<span data-poc="'+getCateList[i]['cat_value']+'" class="badge badge-success">'+getCateList[i]['cat_value']+'%</span></a>'; 
            break;
            case "secondary-list":
                html += '<i class="si si-plus"></i><a href="javascript:void(0)" class="colaps-head-1">Secoundry<span class="badge badge-success" data-poc="'+getCateList[i]['cat_value']+'">'+getCateList[i]['cat_value']+'%</span></a>';
            break;
            case "objective-list":
                html += '<i class="si si-plus"></i><a href="javascript:void(0)" class="colaps-head-1">Objective<span class="badge badge-success" data-poc="'+getCateList[i]['cat_value']+'">'+getCateList[i]['cat_value']+'%</span></a>';
            break;
            default:
        }
        html += '<ul class="lavel-3"></ul></li>';
        newListItems.push(html);
    })
   $(".lavel-2").append(newListItems);
}


async function phaseOneFormValidation(){ //phase-1 form Submit
    ajaxLoader(true);
    console.log(phaseOneData);
     checkGrandTotalOfCat = 0;
     var updateCategoryList = [];
     $(".phase_2f-details .psf_row").each(function(i){
         var getEleOfInput = $(this).find(".item-key").attr("name");
 //        console.log(getEleOfInput);
         var getInputVal = $(this).find(".percent-box").val();
         updateCategoryList.push({"cat_name":getEleOfInput,"cat_value":getInputVal});
         checkGrandTotalOfCat +=  Number(getInputVal);
     })
     if(checkGrandTotalOfCat==100){
         form1_response_data = [];
        localStorage.setItem("jrc_categories",JSON.stringify(updateCategoryList));
        checkJrcCatList=JSON.parse(await add_data(updateCategoryList))
        formSwitch(true);
        console.log('phaseOneFormValidation',checkJrcCatList)
        listSync()
        updateDateCategory(checkJrcCatList['getStoreData']);
          ajaxLoader(false);
//         $.ajax({
//              url:"/company/jcr/",
//              headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
//              type:'POST',
//              contentType: 'application/json; charset=UTF-8',
//              data: JSON.stringify({'updateCategoryList': updateCategoryList}),
//              error: function (request, status, error) {
//                    alert(error);
//              }
//         }).done(function(response){
//             console.log('responseJCRRRRRRRRRRRRRRRRR >>>>>>>>>',response);
//             form1_response_data = response;
// //            $(".percent-box").val('');
//             formSwitch(true);
//             console.log('responseJCRRRRRRRRRRRRRRRRR >>>>>>>>>',response);
//             checkJrcCatList=JSON.parse(response)
//             listSync()
//            //  ajaxLoader(false);
//
//         });
     }else{
         phaseOneData = false;
         formSwitch(false);
         ajaxLoader(false);
     }
     localStorage.setItem("jrc_categories",JSON.stringify(updateCategoryList));
 }


async function add_data(updateCategoryList){
    var return_data = await $.ajax({
              url:"/company/jcr/",
              headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
              type:'POST',
              contentType: 'application/json; charset=UTF-8',
              data: JSON.stringify({'updateCategoryList': updateCategoryList}),
              error: function (request, status, error) {
                    alert(error);
              }
         }).done(function(response){
//             form1_response_data = response;
         });
    return return_data
};


function enableNextButton(checkStatus){
    if(checkStatus){
        $("#nextFormActionBtn").removeClass('disabled');
        $("#nextFormActionBtn").addClass('showNextPage');
        $("#sampleSubmitBtn").hide();
        $("#nextFormActionBtn").show();
    }else{
        $("#nextFormActionBtn").addClass('disabled');
        $("#nextFormActionBtn").removeClass('showNextPage');
        $("#nextFormActionBtn").hide();
        $("#sampleSubmitBtn").show();
    }
}

function populateSubCatItems(getCatKeys){
    // console.log("the cat keys are ",getCatKeys)
  // console.log(getCatKeys);
   var fitlerByKeyItem = [];
//    getListItems = JSON.parse(localStorage.getItem("jcr_details"));
    getListItems = checkJrcCatList
//    console.log("the length of getlistitems",getListItems.length)
//    console.log(JSON.stringify(getListItems))
//    console.log(getListItems)
   var question_wrappers = $(".jcr-child3__categorry-form").children(".sub-que__wrapper")
   $.each(question_wrappers,function(index){
       question_wrappers[index].remove()
   })
    $.each(getListItems, function(idx){
        // console.log(getListItems[idx]['cat_name'])
       if(getListItems[idx]['cat_name'] == getCatKeys['parentKey']){
           var subCatListItems = getListItems[idx]['addDetailsItem'];
        //    console.log("subCatListItems",subCatListItems.length)
           $.each(subCatListItems, function(sIdx){
            //    console.log(subCatListItems[sIdx]['cat_type']+"====="+getCatKeys['subCatKey'])
               if(subCatListItems[sIdx]['cat_type'] == getCatKeys['subCatKey']){
                //    console.log("subCatListItems[sIdx]",subCatListItems[sIdx]['id'])
                    var childListItems = subCatListItems[sIdx]['cat_subtype']
                    // console.log("the child items",childListItems)
                    $(".left_section .add_newfeild").val(subCatListItems[sIdx]['cat_type']);
                    $(".left_section .add_id").val(subCatListItems[sIdx]['id']);
                    $(".left_section .add_parcent").val(subCatListItems[sIdx]['cate_percent']);
                        console.log("the sub list items",childListItems.length)
                        if(childListItems.length > 0){
                            $(".lower_section li").remove();
                            
                            var newItemsSplit = childListItems;
                           


                            console.log("child list items",childListItems.length)                            
                            $.each(childListItems,function(index){
                                // console.log(childListItems[index]["question"])
                                var id = childListItems[index]["id"]
                                var question = childListItems[index]["question"]
                                var q_percent =childListItems[index]["q_percent"]
                                var matching =childListItems[index]["matching"]
                                var single_checked = ""
                                var multiple_checked = ""
                                
                                if(matching == "single")
                                {
                                    single_checked = "checked"
                                }
                                else
                                {
                                    multiple_checked = "checked"
                                }

                                var sublistPopulate = `<div class="sub-que__wrapper">
                                    <p class="rt-remove-form rounded-10"><i class="typcn typcn-delete"></i></p>
                                    <div class="sample__form bd bd-10 rounded-20">
                                    <div class="upper__section">
                                        <form action="" class="upper-top__text-feilds" id="addFeild">
                                            <div class="add-quest-textarea">
                                                <input type="number" value="`+id+`" hidden readOnly name="q_add_id" class="q_add_id">
                                                <input type="text" placeholder="write something" value="`+question+`" name="input_text_one" class="upper-ls_full_text bd bd-0 rounded-10">
                                                <div class="sfx-input quest-percent-tab" data-suffix="%">
                                                <input type="number" value="`+q_percent+`" name="que-percent" class="sl-feild2 bd-0 sub-cat-num" oninput="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength);" maxlength="3">
                                                </div>
                                            </div>
                                            <div class="xs-col-2">
                                                <input name="form-category" type="radio" value="single" `+single_checked+`><span>single</span>
                                                <input name="form-category" type="radio" value="multi" `+multiple_checked+`><span>multiple</span>
                                            </div>
                                        </form>
                                    </div>
                                    <ul class="lower_section">`;

                                // var subChildListItems = childListItems[index]["details"]
                                var subChildListItems = childListItems[index]["details"]
                                console.log("sub childdds===============>>>",childListItems[index])

                                $.each(subChildListItems, function(idx){
                                    var modIdNew = idx+1;
                                // console.log("======================>",subChildListItems[idx])
                                    sublistPopulate += '<li class="show_list bd bd-2 rounded-20 xs-clone clone-'+modIdNew+'"><input type="number" hidden readOnly value="'+subChildListItems[idx]["id"]+'" name="detail_id" class="detail_id"><input type="text" value="'+subChildListItems[idx]["title"]+'" name="lang-1" class="sl-feild1 bd-0 rounded-10 sub-cat-title">';
                                    sublistPopulate += '<div class="sfx-input" data-suffix="%"><input type="number" value="'+subChildListItems[idx]["percent"]+'" name="lang" class="sl-feild2 bd-0 sub-cat-num" oninput="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength);" maxlength = "3"></div>';
                                    sublistPopulate += '<button class="btn btn-outline-danger btn-icon sl-action-btn btn-icon bd-0"><i class="typcn typcn-trash"></i></button></li>';
                                })
                                sublistPopulate += `</li>

                             </ul>
                             <div class="split_btn-bottom badge badge-outline-light">
                                <span class="add-clone">
                                <i class="si si si-plus"></i> Add More
                                </span>
                             </div>
                             <ul class="clone-listing" style="display:none;">
                                <li class="show_list bd bd-2 rounded-20">
                                   <input type="number" value="" hidden readOnly name="detail_id" class="detail_id">
                                   <input type="text" value="" name="lang-1" class="sl-feild1 bd-0 rounded-10 sub-cat-title">
                                   <div class="sfx-input" data-suffix="%">
                                      <input type="number" value="" name="lang" class="sl-feild2 bd-0 sub-cat-num" oninput="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength);" maxlength="3">
                                   </div>
                                   <button class="btn btn-outline-danger btn-icon sl-action-btn btn-icon bd-0">
                                   <i class="typcn typcn-trash"></i>
                                   </button>
                                </li>
                             </ul>
                          </div>
                          <span class="split__half-circle"><img src="../../assets/img/circle-edge.png"></span>
                       </div>`
                       $(".jcr-child3__categorry-form").prepend(sublistPopulate);
                            })
                            



                   
                           
                        }
                        else{
                            subCatClone = `<div class="sub-que__wrapper">
                            <p class="rt-remove-form rounded-10"><i class="typcn typcn-delete"></i></p>
                            <div class="sample__form bd bd-10 rounded-20">
                            <div class="upper__section">
                                <form action="" class="upper-top__text-feilds" id="addFeild">
                                    <div class="add-quest-textarea">
                                        <input type="number" value="" hidden readOnly name="q_add_id" class="q_add_id">
                                        <input type="text" placeholder="write something" value="" name="input_text_one" class="upper-ls_full_text bd bd-0 rounded-10">
                                        <div class="sfx-input quest-percent-tab" data-suffix="%">
                                        <input type="number" value="" name="que-percent" class="sl-feild2 bd-0 sub-cat-num" oninput="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength);" maxlength="3">
                                        </div>
                                    </div>
                                    <div class="xs-col-2">
                                        <input name="form-category" type="radio" value="single" checked><span>single</span>
                                        <input name="form-category" type="radio" value="multi"><span>multiple</span>
                                    </div>
                                </form>
                            </div>
                            <ul class="lower_section"></ul>
                            <div class="split_btn-bottom badge badge-outline-light">
                                <span class="add-clone">
                                <i class="si si si-plus"></i> Add More
                                </span>
                            </div>
                            <ul class="clone-listing" style="display:none;">
                                <li class="show_list bd bd-2 rounded-20">
                                    <input type="number" value="" hidden readOnly name="detail_id" class="detail_id">
                                    <input type="text" value="" name="lang-1" class="sl-feild1 bd-0 rounded-10 sub-cat-title">
                                    <div class="sfx-input" data-suffix="%">
                                        <input type="number" value="" name="lang" class="sl-feild2 bd-0 sub-cat-num" oninput="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength);" maxlength = "3">
                                    </div>
                                    <button class="btn btn-outline-danger btn-icon sl-action-btn btn-icon bd-0">
                                    <i class="typcn typcn-trash"></i>
                                    </button>
                                </li>
                            </ul>
                            </div>
                                <span class="split__half-circle"><img src="../../assets/img/circle-edge.png"></span>
                            </div>`;
                            $(".jcr-child3__categorry-form").prepend(subCatClone)
                        }
               }
           })
       }
    })
}

/**Activities**/
function ajaxLoader(loaderFlag){
    if(loaderFlag){$("#global-loader").show();}else{setTimeout(function(){  $("#global-loader").hide(); }, 700); }
}

function formCleanUp(){
    // $("#rmChildList").trigger('click');
    var flag = {'reset':true,'delete':true};
    resetChildClonelist(flag);
    $('.left_section').each(function(){
        $(this).find('input').val('');
    });
}

function snakBarShow(getParamOfMsg){ //Activity of Snackbar 
  //{msg:"Snackbars contain a text label that directly relates to the process being performed"}
  var newMsg = getParamOfMsg;
  $("#snackbar").html('');
  $("#snackbar").append('<p>'+newMsg+'<p>');
  $("#snackbar").addClass('show')
  setTimeout(function(){ $("#snackbar").removeClass('show') }, 3000);
}

function formSwitch(checActiveFlag){
    if(checActiveFlag){
        $(".jcr__phase-1").hide();
        $(".jcr__phase-2").show();
    }else{
        $(".jcr__phase-1").show();
        $(".jcr__phase-2").hide();
    }
}

function jcrTemplateUpdate(){
    // checkJrcCatList = JSON.parse(localStorage.getItem("jrc_categories")); //get main category list items
//    var checkJrcCatList = get_jcrData(); //get main category list items
    console.log('checkJrcCatList in jcrTemplateUpdate', checkJrcCatList)
    if(checkJrcCatList['getStoreData']=="null"){
        alert('in false');
        formSwitch(false);
    }else{
        updateDateCategory(checkJrcCatList['getStoreData']);
        formSwitch(true);
    }
}


function checkFormDataCalucations()
{
    var currentCat = $(".active_batch");
    var currentCatElements = currentCat.closest(".colaps-tab").find(".lavel-3 li");
    var sumOfSubCats = 0
    var newSubCatElement = $(".left_section")
    var newSubCatEleLabel = newSubCatElement.find(".add_newfeild ").val()
    var newSubCatEleValue = newSubCatElement.find(".add_newfeild ").val()
    var emptyFlag = false

    // var textInputs = $(".form_model").find(".sub-cat-title,.mc-title,.upper-ls_full_text,.mc-num,.sub-cat-num")
    var textInputs = document.querySelectorAll(".sub-cat-title,.mc-title,.upper-ls_full_text,.mc-num,.sub-cat-num")
    console.log("text inputs",textInputs)

    textInputs = $(textInputs)
  
    
    //CHECK FOR EMPTY INPUTS!!!!!!!!!!!!!1
    $.each(textInputs,function(index){
        console.log(!textInputs.eq(index).val(),"----", textInputs.eq(index).closest(".clone-listing").length)
        if(!textInputs.eq(index).val() )
        {

            if(textInputs.eq(index).closest(".clone-listing").length == 0)
            {
                emptyFlag=true
                console.log("value",textInputs.eq(index).val())
                addRedBorder(textInputs.eq(index))
                // setTimeout(function(){textInputs.eq(index).addClass('ntValidShadow'); },0);
                // setTimeout(function(){textInputs.eq(index).removeClass('ntValidShadow'); },2500);
            }                       
        }
    })
    
    if(emptyFlag)
    {
        showMsg = "Please fill all the fields!!!"
        snakBarShow(showMsg);
        return false
    }
    //FINISH CHECK FOR EMPTY INPUTS

    //CHECK FOR SUB CATEGORY PERCENT TO NOT EXCEED 100%

    if(currentElement =="")
    {
            $.each(currentCatElements,function(index){

                sumOfSubCats += parseInt(currentCatElements.eq(index).attr("data-percent"));
                console.log("sum of subcarts",sumOfSubCats)
                console.log(parseInt(sumOfSubCats) + parseInt(document.querySelector(".add_parcent").value))
                if(parseInt(sumOfSubCats) + parseInt(document.querySelector(".add_parcent").value) > 100)
                {
                    
                    emptyFlag =  true
                    showMsg = "the total of all categories exceed 100%"
                    snakBarShow(showMsg);
                    addRedBorder($(document.querySelector(".add_parcent")))
                    // setTimeout(function(){$(document.querySelector(".add_parcent")).addClass('ntValidShadow'); },0);
                    // setTimeout(function(){$(document.querySelector(".add_parcent")).removeClass('ntValidShadow'); },2500);
                    $.each(currentCatElements,function(i){
                    
                        setTimeout(function(){ currentCatElements.eq(i).addClass('ntValidShadow'); },0);
                    setTimeout(function(){ currentCatElements.eq(i).removeClass('ntValidShadow'); },2500);
                    })
                }

    
        });
    }
    

    //FINISH CHECK FOR SUB CATEGORY TO NOT EXCEED BY 100%

    
    // if(newSubCatElement)



    var all_que_wrappers = $(".sub-que__wrapper")

    $.each(all_que_wrappers,function(index){
        var currentElement= all_que_wrappers.eq(index)
        var selectedOption = currentElement.find("[name='form-category']:checked").val()

        var allSubCatPercents = currentElement.find(".lower_section").find(".sub-cat-num")
        console.log("all sub_cat opereecentsns ",allSubCatPercents)
    
        //CHECK FOR SINGLE ELEMENTS TO HAVE ATLEAST ONE FIELD WITH 100%

        if(selectedOption == "single")
        {
            
            var hasHundred = false

            $.each(allSubCatPercents,function(i){                
                console.log("has hundreeed vallsslssss",allSubCatPercents.eq(i).val())
                if(allSubCatPercents.eq(i).val() == "100")
                {
                    hasHundred = true
                }
            })

            console.log("the has hundred is",hasHundred)
            if(hasHundred == false)
            {
                showMsg = "All sub categories with selected option `single ` should have atleast one field with 100%"
                snakBarShow(showMsg);
                emptyFlag = true
                addRedBorder(currentElement)
            }

        }
          //FINISH CHECK FOR SINGLE ELEMENTS TO HAVE ATLEAST ONE FIELD WITH 100%

          // CHECK FOR MUTLIPELE ELEMENTS TO HAVE THEIR SUM EQUAL TO EXACTLY 100

        else{
            var sumOfAllSubCat = 0
            var sumHundred = false
            $.each(allSubCatPercents,function(i){                
                console.log("has hundreeed vallsslssss",allSubCatPercents.eq(i).val())
                 sumOfAllSubCat += parseInt(allSubCatPercents.eq(i).val())
                if( sumOfAllSubCat ==100)
                {
                    sumHundred = true
                }                
            })
        
            console.log("the sum hundred usssssss",sumOfAllSubCat)
            if(sumHundred == false)
            {
                showMsg = "All sub categories with selected option `multiple` should add upto exactly 100%"
                snakBarShow(showMsg);
                emptyFlag = true
                addRedBorder(currentElement)
            }

        }
        //FINISH CHECK FOR MUTLIPELE ELEMENTS TO HAVE THEIR SUM EQUAL TO EXACTLY 100



    })

    // CHECK FOR ALL SUB CAT PARENT ELEMENTS TO HAVE THIER SUM EQUAL TO EXACTLY 100%

    var sumOfSubCatParents = 0
    var isSumOfSubCatParHundred = false
    $.each(all_que_wrappers,function(j){
       
        sumOfSubCatParents += parseInt(all_que_wrappers.eq(j).find(".upper__section").find(".sub-cat-num").val())
    })

    if(sumOfSubCatParents == 100)
    {
        isSumOfSubCatParHundred = true
    }

    if(isSumOfSubCatParHundred == false)
    {
        showMsg = "THE SUM OF ALL SUBCATEGORY TITLE PERCENT SHOULD ADD UPTO EXACTLY 100%"
        snakBarShow(showMsg);
        emptyFlag = true
        $.each(all_que_wrappers,function(j){
            addRedBorder(all_que_wrappers.eq(j))
        })
        
    }
    
    

      

    console.log("the vlayue of empoty falg is",emptyFlag)
    if(emptyFlag)
    {
        return false
    }
    else
    {
        return true
    }
    
}


function addRedBorder(element) 
{
    setTimeout(function(){ element.addClass('ntValidShadow'); },0);
    setTimeout(function(){ element.removeClass('ntValidShadow'); },2500);
}


