$(document).ready(function(){
    init();
    /**Current Address Dropls selectors**/
    primaryCountryLs = $(".prm-country-ls");
    primaryStateLs = $(".prm-state-ls");
    primaryCityLs = $(".prm-city-ls");
    /**Permanent Address Dropls selectors**/
    secoundCountryLs = $(".secoundry-country-ls");
    secoundStateLs = $(".secoundry-state-ls");
    secoundCityLs = $(".secoundry-city-ls");
    
    /**Other Selectors**/
    preferenceCountryLs = $(".prf-country_list");
//    noticeInput = $(".notice-days");
    experFormCheckBoxOfCurrentWork = $(".workStatus__checkMark");
    pursuingBtnOfEduFrom = $(".checked-edu-purse");
    /**other selectors**/
    formSubmitAction = $('.candidateFormSubmit');

    $("#basicFormDatePicker").datepicker({
        onSelect: function(value, ui) {
            var today = new Date(),
            age = today.getFullYear() - ui.selectedYear;
        },
        yearRange: '-70:-18',
        dateFormat: 'dd/mm/yy',
        changeMonth: true,
        changeYear: true, 
    })
    

  $(".address__checkMark").on('change',function(){ //Permanent Address Checkbox onchnage Event
    if($(this).is(":checked")){
      let checked = true;
      addressFromUpdate(checked);
    }else{
      let checked = false;
      addressFromUpdate(checked);
    }
  });
  $(document).on('click','.delete-edu-details-ls', function(){ //edu-clone form remove
    $(this).closest('.edu-form__container').remove();
  })
  $(document).on('click','.delete-edu-gap-ls',function(){ //edu gap clone form remove
    $(this).closest('.edu-str_line').remove();
  })
  $(document).on('click','.delete-exper-gap-ls',function(){ //exper gap clone form remove
    $(this).closest('.exper-str_line').remove();
  })
  $(document).on('click','.delete-exper-clone-ls',function(){ //delete experence details clone list
    $(this).closest('.experience_details__input-section').remove();
  })
  $(document).on('click','.portFormClonedelete',function(){ //delete experence details clone list
    $(this).closest('.port-form-col__list').remove();
  })
  $('.experiance-val').on('keyup',function(){
    var getValueOfExperience = $.isNumeric($(this).val());
    if(getValueOfExperience == 'NaN' || getValueOfExperience == 'null' || getValueOfExperience == 'false' || getValueOfExperience == 'undefined '){
      $(this).after("<p style='color: #ff0000;'>invalid value</p>");
      setTimeout(function(){
        $(this).next('p').remove();
      },2500)
    }
  })

  $("#primaryAddressForm :input").on("change",function() { //Current Address form onChange Event
    if($(".address__checkMark").is(":checked")){
      setTimeout(function(){
        addressFromUpdate(true);
      },1200)
    }
  });
  $(document).on('change','.check-edugap-form', function(){ //edu-gap checkbox click-event
    if($(this).is(":checked")){
      eduGapInputValidation(true);
      $(this).closest('.edu-gap-details__head-section').find('.edugap-right-head__section .edugap-addmore-btn').addClass('active');
      $(this).closest('.edu-head-section').next('.collapse-list').slideDown();
      $(this).closest('.edu-head-section').addClass("border_shade");
     /* $(".edugap-addmore-btn").addClass('active');
      $(".collapse-list").slideDown();
      $(".edu-head-section").addClass("border_shade");*/
    }else{
      eduGapInputValidation(false);
      $(this).closest('.edu-gap-details__head-section').find('.edugap-right-head__section .edugap-addmore-btn').removeClass('active');
      $(this).closest('.edu-head-section').next('.collapse-list').slideUp();
      $(this).closest('.edu-head-section').removeClass("border_shade");
      /*$(".edugap-addmore-btn").removeClass('active');
      $(".collapse-list").slideUp();
      $(".edu-head-section").removeClass("border_shade");*/
    }
  })
  $(document).on('change','.check-expergap-form', function(){ //experience gap checkbox click-event
    if($(this).is(":checked")){
      experGapInputValidation(true);
     /* $(".exper-gap-addmore-btn").addClass('active');
      $(".collapse-list").slideDown();
      $(".expergap-left-head__section").addClass("border_shade");*/
      $(this).closest('.exper-gap-details__head-section').find('.exper-gap-right-head__section .exper-gap-addmore-btn').addClass('active');
      $(this).closest('.exper-head-section').next('.collapse-list').slideDown();
      $(this).closest('.exper-head-section').addClass("border_shade");

    }else{
      experGapInputValidation(false);
      /*$(".exper-gap-addmore-btn").removeClass('active');
      $(".collapse-list").slideUp();
      $(".expergap-left-head__section").removeClass("border_shade");*/
      $(this).closest('.exper-gap-details__head-section').find('.exper-gap-right-head__section .exper-gap-addmore-btn').removeClass('active');
      $(this).closest('.exper-head-section').next('.collapse-list').slideUp();
      $(this).closest('.exper-head-section').removeClass("border_shade");
    }
  })

  $(document).on("click","#eduAddMoreClone", function(e){ //add clone btn of education form
    eduDetailscloneForm = "";
    var FromSelectorsClone = "";
    var getLengthOfEduList = $(document).find("#eduDetailsForm .edu-form__container").length;
    var FromSelectorsClone = $(this).closest('.edu_details_form').eq(0).find('.edu-form__container').find('.start-date__selector').html();
    
    $("#eduDetailsForm .edu-form__container").each(function(idx){
      checkIndex = idx+1;
      if(getLengthOfEduList == checkIndex){
        eduDetailscloneForm = `<div class="edu-form__container str_line xsc-list clone-`+checkIndex+` "><div class="row row-sm"><div class="col-lg"><div class="row edu-upper-section"><div class="col-lg mg-t-10 mg-lg-t-0"> <label class="req-field">Institude/School:</label> <input class="form-control edu-name" class="form-control edu-name" value="" required name="edu_institute" type="text"></div><div class="col-lg mg-t-10 mg-lg-t-0"> <label class="req-field">Department:</label> <input class="form-control edu-field" name="edu_department" value="" required name="edu-field-name" type="text"></div><div class="col-lg mg-t-10 mg-lg-t-0"> <label class="req-field">Degree:</label> <input class="form-control edu-degree" name="edu_degree" value="" required name="edu-degree-name" type="text"></div></div></div></div><div class="row row-sm"><div class="col-lg"><div class="row edu-middle-section mg-lg-t-20"><div class="col-lg mg-t-10 mg-lg-t-0"> <label>Duration:</label> <input class="form-control edu-duration-info" value="" name="edu_duration" type="number"></div><div class="col-lg mg-t-10 mg-lg-t-0">`+FromSelectorsClone+`</div><div class="col-lg mg-t-10 mg-lg-t-0"><div class="end-date__selector inline-list__view"> <label class="req-field">To</label><div class="fx-row end-duration"> <select class="end-month form-control edu-to-month" name="edu-detail-end-month" required disabled><option label="Month" value="" class="null-selector"></option> </select> <select class="end-year form-control edu-to-year" name="edu-detail-end-year" required disabled><option label="Year" value="" class="null-selector"></option> </select></div></div></div></div></div></div><div class="row row-sm mg-t-20"><div class="col-lg"><div class="edu-checkfield-btn"> <label>Pursuing:</label> <input class="form-control checked-edu-purse check-size" value="" name="edu_pursuing_check" type="checkbox"></div></div><div class="col-lg delete-right-side"> <button class="delete-edu-details-ls btn btn-sm btn-outline-danger btn-block" type="button"><i class="fas fa-trash-alt"></i>Delete</button></div></div></div>`;
        $(document).find(".edu-form__container:last").after(eduDetailscloneForm)
      }
    })
    //$(".edu-form__container:last-child").find(".checked-edu-purse").prop("checked", false);
  })


  $(document).on("click","#eduGapAddMoreClone",function(){  //add clone btn of education gap form
    var eduGapFormClone = "";
    var fromSelectorsClone = "";
    
    var getLengthOfEduList = $(this).closest(".edu_gap_form").find(".collapse-list .edu-gap__from").length;
    //var cloneClass= 'row row-sm edu-str_line edugap-clone-'+getLengthOfEduList;
    fromSelectorsClone = $(this).closest("#eduGapDetailForm").find('.edu-gap__from:first-child .edugap-left-upper__section').html();
    //$(".collapse-list .edu-gap__from").each(function(idx){
      console.log($(this).closest(".edu_gap_form").find(".collapse-list .edu-gap__from"))
    $(this).closest(".edu_gap_form").find(".collapse-list .edu-gap__from").each(function(idx){
      checkIndex = idx+1;
      if(getLengthOfEduList == checkIndex){
        eduGapFormClone = `<div class="row row-sm edu-str_line edugap-clone-`+getLengthOfEduList+`"><div class="col-lg-4 col-md-12 col-sm-12"><div class="row edugap-left-upper__section"> `+fromSelectorsClone+`</div><div class="row edugap-left-lower__section"><div class="col-lg mg-t-10 mg-lg-t-10"> <label class="req-field">To</label><div class="fx-row"> <select class="end-month form-control edugap-to-month" name="edugap-end-month" disabled required><option label="Month" value="" class="null-selector"></option> </select> <select class="end-year form-control edugap-to-year" name="edugap-start-year" disabled required><option label="Year" value="" class="null-selector"></option> </select></div></div></div></div><div class="col-lg-8 col-md-12 col-sm-12"><div class="row edugap-left-lower__section"><div class="col-md-12 col-sm-12 col-lg-12"> <label class="req-field">Reason:</label><textarea class="form-control edugap-reason-textbox" value="" name="edugap-reason" placeholder="" rows="4"></textarea></div></div></div><div class="row row-sm bottom-row"><div class="col-lg edu-gap-delete-wrapper"> <button class="delete-edu-gap-ls btn btn-sm btn-outline-danger btn-block" type="button"><i class="fas fa-trash-alt"></i>Delete</button></div></div></div>`;

        $(".collapse-list .edu-gap__from").after(eduGapFormClone);
      // cloneItem =  $(".edu-gap__from").clone().attr("class", cloneClass);
       //$(".collapse-list .edu-gap__from").after(cloneItem);
      }
    })
  })

  $(document).on("click","#experGapAddMoreClone",function(){  //add clone btn of Experience gap form
    var experGapFormClone = "";
    var fromSelectorsClone = "";
    var getLengthOfExperList = $(this).closest(".exper_gap_form").find(".collapse-list .exper-gap__from").length;
    console.log('aa'+getLengthOfExperList)
    fromSelectorsClone = $(this).closest("#experGapDetailForm").find('.exper-gap__from:first-child .exper-gap-left-upper__section').html();
    console.log("htmlsas",fromSelectorsClone);
    $(this).closest(".exper_gap_form").find(".collapse-list .exper-gap__from").each(function(idx){
      checkIndex = idx+1;
      if(getLengthOfExperList == checkIndex){

        experGapFormClone = `<div class="row row-sm exper-str_line expergap-clone-`+getLengthOfExperList+`"><div class="col-lg-4 col-md-12 col-sm-12"><div class="row exper-gap-left-upper__section">`+fromSelectorsClone+`</div><div class="row exper-gap-left-lower__section"><div class="col-lg mg-t-10 mg-lg-t-10"> <label class="req-field">To</label><div class="fx-row"> <select class="end-month form-control exper-gap-to-month" name="expergap-end-month" disabled><option label="Month" value="" class="null-selector"></option> </select> <select class="end-year form-control exper-gap-to-year" name="expergap-end-year" disabled><option label="Year" value="" class="null-selector"></option> </select></div></div></div></div><div class="col-lg-8 col-md-12 col-sm-12"><div class="row exper-gap-left-lower__section"><div class="col-md-12 col-sm-12 col-lg-12"> <label class="req-field">Reason:</label><textarea class="form-control exper-gap-reason-textbox" value="" name="expergap-reason" placeholder="" rows="4"></textarea></div></div></div><div class="row row-sm bottom-row"><div class="col-lg exper-gap-delete-wrapper"> <button class="delete-exper-gap-ls btn btn-sm btn-outline-danger btn-block" type="button"> <i class="fas fa-trash-alt"></i>Delete </button></div></div></div>`;

        $(this).closest(".exper_gap_form").find(".collapse-list .exper-gap__from").after(experGapFormClone);
      }
    })
  })

   $(document).on('click','#portfolioAddCloneAction',function(){
        portFolioCloneEle = "";
        getLenghtFormLs = $(this).closest('#tagSelectorSection').find('.portfolio-form-section_row .port-form-col__list').length;

        portFolioCloneEle += `<div class="col-lg port-form-col__list pfc-top-border mg-t-50">
            <div class="row addTagsSelectorView">
                <div class="xs-one-third col-lg mg-t-10 mg-lg-t-0">
                    <label>Project name:</label>
                    <input type="text" value="" name="project_name" class="port-project-name form-control">
                </div>
                <div class="xs-one-third col-lg mg-t-10 mg-lg-t-0">
                    <label>Project link:</label>
                    <input type="text" value="" name="project_link" class="port-project-links form-control">
                  </div>
                <div class="xs-one-third col-lg mg-t-10 mg-lg-t-0">
                    <label>Attachment:</label>
                    <div class="input-group file-browser">
                        <input type="text" class="form-control border-right-0 browse-file port-project-attach" placeholder="choose" readonly>
                        <label class="input-group-btn">
                            <span class="btn btn-default">
                              Browse <input type="file" name="portfolio_attachment" value="" style="display: none;" multiple>
                            </span>
                        </label>
                    </div>
                </div>
            </div>
            <div class="row addTagsSelectorView">
                <div class="xs-one-full col-lg mg-t-10 mg-lg-t-0">
                    <label>Description:</label>
                    <textarea class="portfolioMultiForm" name="portfolio_description"></textarea>
                 </div>
            </div>
            <div class="row deleteActionCol">
                <div class="xs-one-full col-lg mg-t-10">
                <button class="portFormClonedelete btn btn-sm btn-outline-danger" type="button">
                  <i class="fas fa-trash-alt"></i><label>Remove</label>
                </button>
            </div>
        </div>
        </div>`;

        $(this).closest('#tagSelectorSection').find('.portfolio-form-section_row .port-form-col__list:last-child').after(portFolioCloneEle);
        setTimeout(function(){
            var getSelectorOfEditor =  $(this).closest('#tagSelectorSection').find('.portfolio-form-section_row .port-form-col__list:last-child .portfolioMultiForm');
            afterChangeList(getSelectorOfEditor);
        },200)
   });

  primaryCountryLs.on('change', async function(){ //current address country selected to update state list
    var primaryStateLsObj = [];
    fetchPrimaryStateLS = "";
    selectedCountryVal = $(this).children("option:selected").val();
    if(selectedCountryVal !== ""){
      console.log("get value of country code"+selectedCountryVal)
      primaryStateLsObj = await setStateList(selectedCountryVal);
      if(primaryStateLsObj.length){
        fetchPrimaryStateLS += '<option label="Choose one"></option>';
        $.each(primaryStateLsObj, function(objKey){
          fetchPrimaryStateLS += "<option value="+primaryStateLsObj[objKey].id+">"+primaryStateLsObj[objKey].name+"</option>";
        })
        primaryStateLs.removeAttr('disabled');
        //primaryStateLs.append(fetchPrimaryStateLS);
        primaryStateLs
          .find('option')
          .remove()
          .end()
          .append(fetchPrimaryStateLS)
      }else{
        fetchPrimaryStateLS += '<option label="Choose one"></option>';
        primaryStateLs
        .find('option')
        .remove()
        .end()
        .append(fetchPrimaryStateLS)
        primaryStateLs.attr('disabled','');

        primaryCityLs
        .find('option')
        .remove()
        .end()
        .append(fetchPrimaryStateLS)
        primaryCityLs.attr('disabled','');
      }
    }else{
      console.log("ELSE ->>get value of country code"+selectedCountryVal)
      fetchPrimaryStateLS += '<option label="Choose one"></option>';
      primaryStateLs
      .find('option')
      .remove()
      .end()
      .append(fetchPrimaryStateLS)
      primaryStateLs.attr('disabled','');

      primaryCityLs
      .find('option')
      .remove()
      .end()
      .append(fetchPrimaryStateLS)
      primaryCityLs.attr('disabled','');
    }
  })

  secoundCountryLs.on('change', async function(){ //Permanent address country selected to update state list
    var secStateLsObj = [];
    var fetchParmanentStateLS = "";
    secoundStateLs.find('option').remove();
    selectedCountryVal = $(this).children("option:selected").val();
    if(selectedCountryVal !== ''){
      secStateLsObj = await setStateList(selectedCountryVal);
      if(secStateLsObj.length){
        fetchParmanentStateLS += '<option label="Choose one"></option>';
        $.each(secStateLsObj, function(objKey){
          fetchParmanentStateLS += "<option value="+secStateLsObj[objKey].id+">"+secStateLsObj[objKey].name+"</option>";
        })
        secoundStateLs.removeAttr('disabled');
        //secoundStateLs.append('<option label="Choose one"></option>');
        //secoundStateLs.append(fetchParmanentStateLS);
          secoundStateLs
          .find('option')
          .remove()
          .end()
          .append(fetchParmanentStateLS)
      }else{
        fetchParmanentStateLS += '<option label="Choose one"></option>';
        secoundStateLs
          .find('option')
          .remove()
          .end()
          .append(fetchParmanentStateLS)

          secoundCityLs
          .find('option')
          .remove()
          .end()
          .append(fetchParmanentStateLS)
          secoundCityLs.attr('disabled','');
      }
    }else{
      fetchParmanentStateLS += '<option label="Choose one"></option>';
      secoundStateLs
      .find('option')
      .remove()
      .end()
      .append(fetchParmanentStateLS)
      secoundStateLs.attr('disabled','');

      secoundCityLs
          .find('option')
          .remove()
          .end()
          .append(fetchParmanentStateLS)
          secoundCityLs.attr('disabled','');
    }
  })
  
  $(document).on('change','.prf-country_list', function(){ //preference country selector
    var prefCitiesLs = $(document).find('.prf-city_list');
    var secCitieseLsObj = [];
    var fetchParmanentStateLS = "";
    prefCitiesLs.find('option').remove();
    selectedCountryVal = $(this).children("option:selected").val();
    if(selectedCountryVal !== ''){
      secCitieseLsObj = setCitiesListFilterByCountry(selectedCountryVal);
      console.log(secCitieseLsObj.length)
      if(secCitieseLsObj.length || !secCitieseLsObj.length == 'undefined'){
        fetchParmanentStateLS += '<option label="Choose one"></option>';
        $.each(secCitieseLsObj, function(objKey){
          fetchParmanentStateLS += "<option value="+secCitieseLsObj[objKey].id+">"+secCitieseLsObj[objKey].name+"</option>";
        })
        console.log(fetchParmanentStateLS)
        prefCitiesLs.removeAttr('disabled');
        prefCitiesLs
          .find('option')
          .remove()
          .end()
          .append(fetchParmanentStateLS)
      }else{
        fetchParmanentStateLS += '<option label="Choose one"></option>';
        prefCitiesLs
          .find('option')
          .remove()
          .end()
          .append(fetchParmanentStateLS)
        console.log(fetchParmanentStateLS)
      }
    }else{
      fetchParmanentStateLS += '<option label="Choose one"></option>';
      prefCitiesLs
      .find('option')
      .remove()
      .end()
      .append(fetchParmanentStateLS)
      prefCitiesLs.attr('disabled','');
      console.log(fetchParmanentStateLS)
    }
  })

  primaryStateLs.on('change', async function(){//current address state selected to update city list
    var primaryCitiesLsObj = [];
    fetchPrimaryCitiesLS = "";
    selectedStateVal = $(this).children("option:selected").val();
    if(selectedStateVal !== ''){
      primaryCitiesLsObj = await setCitiesList(selectedStateVal);
        if(primaryCitiesLsObj.length){
          fetchPrimaryCitiesLS += '<option label="Choose one"></option>';
          $.each(primaryCitiesLsObj, function(objKey){
            fetchPrimaryCitiesLS += "<option value="+primaryCitiesLsObj[objKey].id+">"+primaryCitiesLsObj[objKey].name+"</option>";
          })
          primaryCityLs.removeAttr('disabled');
          primaryCityLs
          .find('option')
          .remove()
          .end()
          .append(fetchPrimaryCitiesLS)
        }else{
          fetchPrimaryCitiesLS += '<option label="Choose one"></option>';
          primaryCityLs
          .find('option')
          .remove()
          .end()
          .append(fetchPrimaryCitiesLS)
          primaryCityLs.attr('disabled','');
        }
    }else{
      fetchPrimaryCitiesLS += '<option label="Choose one"></option>';
      primaryCityLs
      .find('option')
      .remove()
      .end()
      .append(fetchPrimaryCitiesLS)
      primaryCityLs.attr('disabled','');
    }
  })

  secoundStateLs.on('change', async function(){ //Permanent address state selected to update city list
    var secoundCitiesLsObj = [];
    fetchSecoundryCitiesLS = "";
    selectedStateVal = $(this).children("option:selected").val();
    if(selectedStateVal !== ''){
      secoundCitiesLsObj = await setCitiesList(selectedStateVal);
        if(secoundCitiesLsObj.length){
          fetchSecoundryCitiesLS += '<option label="Choose one"></option>';
          $.each(secoundCitiesLsObj, function(objKey){
            fetchSecoundryCitiesLS += "<option value="+secoundCitiesLsObj[objKey].id+">"+secoundCitiesLsObj[objKey].name+"</option>";
          })
          secoundCityLs.removeAttr('disabled');
          secoundCityLs
          .find('option')
          .remove()
          .end()
          .end()
          .append(fetchSecoundryCitiesLS)
        }else{
          fetchSecoundryCitiesLS += '<option label="Choose one"></option>';
          secoundCityLs
          .find('option')
          .remove()
          .end()
          .append(fetchSecoundryCitiesLS)
          secoundCityLs.attr('disabled','');
        }
    }else{
      fetchSecoundryCitiesLS += '<option label="Choose one"></option>';
      secoundCityLs
      .find('option')
      .remove()
      .end()
      .append(fetchSecoundryCitiesLS)
      secoundCityLs.attr('disabled','');
    }
  })

  // experFormCheckBoxOfCurrentWork
  $(document).on('change','.workStatus__checkMark',function(){
    var endMonthSelector = $(this).closest('.experience_details__input-section').find('.end-month')
    var endYearSelector = $(this).closest('.experience_details__input-section').find('.end-year')
//    var noticeTimeSelector = $(this).closest('.fx-inline').find('.notice-days');
    if($(this).is(":checked")){
//      noticeTimeSelector.removeAttr('disabled');
//      noticeTimeSelector.attr('required','');

      endMonthSelector.find("option:nth-child(1)").prop('selected', true);
      endMonthSelector.removeAttr('required');
      endMonthSelector.attr('disabled','')

      endYearSelector.find("option:nth-child(1)").prop('selected', true);
      endYearSelector.removeAttr('required');
      endYearSelector.attr('disabled','');
    }else{
//      noticeTimeSelector.attr('disabled','');
//      noticeTimeSelector.removeAttr('required');
//      if(noticeTimeSelector.hasClass('parsley-error')){
//        noticeTimeSelector.removeClass('parsley-error');
//        noticeTimeSelector.next('.parsley-errors-list').remove()
//      }
      
      endMonthSelector.attr('required','');
      endMonthSelector.removeAttr('disabled')
      endYearSelector.attr('required','');
      endYearSelector.removeAttr('disabled');
//      noticeTimeSelector.find("option:nth-child(1)").prop('selected', true);
    }
  })
 // noticeInput.on('change',function(){if($(this).val() < 0){$(this).val(0) }})  //onchange to check notice-period value

 $(document).on('click','.checked-edu-purse', function(){ //Education Details Pursuing check event
  var endMonthSelector = $(this).closest('.edu-form__container').find('.end-month')
  var endYearSelector = $(this).closest('.edu-form__container').find('.end-year')
  //var monthOption = '<option label="Month" value="" class="null-selector"></option>';
  //var yearOption = '<option label="Year" value="" class="null-selector"></option>';
  console.log(endMonthSelector.find("option:nth-child(1)"))
    if($(this).is(":checked")){
      //month selector element
     endMonthSelector.find("option:nth-child(1)").prop('selected', true);
     endMonthSelector.removeAttr('required');
     endMonthSelector.attr('disabled','')
    //year selector element
     endYearSelector.find("option:nth-child(1)").prop('selected', true);
     endYearSelector.removeAttr('required');
     endYearSelector.attr('disabled','');
    }else{
      endMonthSelector.attr('required','');
      endMonthSelector.removeAttr('disabled')
      endYearSelector.attr('required','');
      endYearSelector.removeAttr('disabled');
    }
  })


  $("#preferenceAddMoreModel").on('click',function(){
   var addListItem = "";
     getLable = $("#fieldTitle").val();
     getValue = $("#fieldDetails").val();
     if(getLable !== "" && getValue !== ""){
      addListItem += '<div class="col-4 mg-t-10 mg-lg-t-0 manual-feild__items mg-lg-b-20"><div class="removeLableFeild"><i class="typcn typcn-trash"></i></div><label>'+getLable+':</label><input class="form-control" value="'+getValue+'" required  type="text"></div>';
     }
     $(".pref-addmore-btn").before(addListItem);
     $("#popUpModelClose").trigger('click');
     $("#fieldTitle").val('');
     $("#fieldDetails").val('');
  })

  $(document).on('click','.removeLableFeild', function(){
    $(this).closest('.manual-feild__items').remove();
  });

  $(document).on('click','#addFormUploadFileds',function(){ //add other attachment file uploader clone event
    var lengthOfOtherDocs = $(this).closest('.resume-upper_section').next('.other-upload-clone__section').find('.attachform-upper-section').length;
    var newFormClone = '';
    newFormClone = `<div class="row attachform-upper-section">
                    <div class="col-8 mg-t-10 mg-lg-t-0 right-form_uploader">
                      <div class="left mini_upload-form">
                        <label>File Name:</label>
                        <div class="input-group file-browser">
                          <input type="text"  name="file_name" class="form-control browse-file" placeholder="enter file name">
                        </div>
                      </div>
                      <div class="right mini_upload-form">
                        <label>Browse File:</label>
                        <div class="input-group file-browser">
                          <input type="text" class="form-control border-right-0 browse-file" placeholder="choose" readonly>
                          <label class="input-group-btn">
                            <span class="btn btn-default">
                              Browse <input type="file" name="file" value="" style="display: none;" multiple>
                            </span>
                          </label>
                        </div>
                      </div>
                    </div>
                    <div class="col-4 mg-t-10 mg-lg-t-0 upload-section">
                      <label class="no-text">no-view</label>
                      <button class="removeOtherUploadFile btn btn-outline-danger" type="button">
                        <i class="fas fa-trash-alt"></i><label>Remove</label>
                      </button>
                    </div>
                  </div>`;
    console.log(lengthOfOtherDocs)
    if(lengthOfOtherDocs < 5){
      $(this).closest('.resume-upper_section').next('.other-upload-clone__section').append(newFormClone);
    }else{
      alert('Soory! you can upload more then any 5 other documents...')
    }
  })
  $(document).on('click','.removeOtherUploadFile', function(){ //remove selected other-upload form
    $(this).closest('.attachform-upper-section').remove()
  })
  var newCount = 1;


  
$(document).on('click', '.exper-clone-delete',function(){
    $(this).closest('.experience_details__input-section').remove();
})
  /*$("#fiter-lang").keyup(function(){
    var filter = $(this).val(), count = 0;
    $(".langMegaList li").each(function(){
    if ($(this).text().search(new RegExp(filter, "i")) < 0) {
        $(this).fadeOut();
     } else {
        $(this).show();
        count++;
     }
    });
  });*/
  $(".langMegaList").on('change',function(){ //language selector
   
   var previewLsOfLang = "";
   var selectedLangValue =  $(this).find("option:selected").val();
   var selectedLangLabel =  $(this).find("option:selected").text();
   if(!selectedLangValue == "" || !selectedLangValue == "undefined"){
    previewLsOfLang += `<div class="lang-previewBox">
                        <div class="xs-cell lang-name" data-item="`+selectedLangValue+`">`+selectedLangLabel+`</div>
                        <div class="xs-cell lang-read-act"><input type="checkbox" value="read" name="lang-read" class="read-option lang-mark"></div>
                        <div class="xs-cell lang-write-act"><input type="checkbox" value="write" name="lang-write" class="write-option lang-mark"></div>
                        <div class="xs-cell lang-speak-act"><input type="checkbox" value="speak" name="lang-speak" class="speak-option lang-mark"></div>
                        <div class="xs-cell lang-delete-act"><div class="langdeleteactbtn btn btn-sm btn-outline-danger"><i class="fas fa-trash-alt"></i></div></div>
                      </div>`;
    $(".lower-details_section").append(previewLsOfLang)
    $(".lang-prop-list").addClass("showList");
   }
   $(this).find("option:selected").remove();
  })
 
  $(document).on('click','.langdeleteactbtn',function(){ //remvoe Selectel Language
    var langListCount = $(this).closest('.lower-details_section').find('.lang-previewBox').length
    if(langListCount == '1'){
      $(".lang-prop-list").removeClass("showList");
    }
    var getLangTitle = $(this).closest('.lang-previewBox').find('.lang-name').text();
    var getLangDataItem = $(this).closest('.lang-previewBox').find('.lang-name').data('item');
    $('.langMegaList').append(`<option class='language-list' value='`+getLangDataItem+`'>`+getLangTitle+`</option>`);
    $(this).closest('.lang-previewBox').remove();
  })

  /**Skill selectors**/




  $(document).find('.professionSkills').select2({
    searchInputPlaceholder: 'Search',
    tags:true
  });
  $(document).find('.addTagsSelectorViewerList').select2({
    placeholder: 'Choose',
    searchInputPlaceholder: 'Search'
  });
  /**form submit**/
  formSubmitAction.on('click',function(){
    var getContactNumberVal = $(document).find('#phone-num').val()
    if(getContactNumberVal !== ""){
      contactNumberValid();
    }else{
      $(document).find('#phone-num').addClass('error');
    }
  })




});





/**document load function end**/
/***function Section***/
function init() {
    // initialisation stuff here
    tinymce.init({
      selector: '.portfolioMultiForm',
      menubar: false,
      plugins: 'lists advlist',
      toolbar: 'bullist numlist bold',
      branding: 'False',
    });
    startMonthYearSelectorUpdateList();
    contactNumByCountryCode();
    getCountryList();
    contactNumberValid();
//    languageListPopulate();
}

function afterChangeList(changeEle){
  tinymce.init({
    selector: '.portfolioMultiForm',
    menubar: false,
    plugins: 'lists advlist',
    toolbar: 'bullist numlist bold',
    branding: 'False',
  });
}

function startMonthYearSelectorUpdateList(){
  const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  let qntYears = 52;
  let selectYear = $(document).find(".start-year");
  let selectMonth = $(document).find(".start-month");
  let currentYear = new Date().getFullYear();

  for (var y = 0; y < qntYears; y++) {
    let yearElem = document.createElement("option");
    yearElem.value = currentYear
    yearElem.textContent = currentYear;
    selectYear.append(yearElem);
    currentYear--;
  }

  for (var m = 0; m < 12; m++) {
    let month = monthNames[m];
    let monthElem = document.createElement("option");
    monthElem.value = m+1;
    monthElem.textContent = month;
    selectMonth.append(monthElem);
  }
}
/*function eduToStartYear(getFromYear){
  $(".edu-to-year option").remove();
  const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  let qntYears = new Date().getFullYear() - getFromYear;
  let selectYear = $(".edu-to-year");
  let selectMonth = $(".edu-to-month");
  let currentYear = new Date().getFullYear();
  $(".edu-to-month").removeAttr('disabled');
  $(".edu-to-year").removeAttr('disabled');

  for (var y = 0; y < qntYears; y++) {
    let yearElem = document.createElement("option");
    yearElem.value = currentYear
    yearElem.textContent = currentYear;
    selectYear.append(yearElem);
    currentYear--;
  }

  for (var m = 0; m < 12; m++) {
    let month = monthNames[m];
    let monthElem = document.createElement("option");
    monthElem.value = m;
    monthElem.textContent = month;
    selectMonth.append(monthElem);
  }
}*/

function eduEndMonthYearList(getFromYear,getSelectorEle){ //edu-list month year append function
  getSelectorEle.find('.end-month option').not(':first').remove();
  getSelectorEle.find('.end-year option').not(':first').remove();
  monthDomEle = getSelectorEle.find('.end-month');
  yearDomEle = getSelectorEle.find('.end-year');
  monthDomEle.removeAttr('disabled');
  yearDomEle.removeAttr('disabled');
  showItems = {"monthEle":monthDomEle,"yearEle":yearDomEle,"startYearVal":getFromYear};
  loadEndOfYearMonthSelector(showItems) //passsing month and year DOM elements with start year value
}

function experienceEndMonthYearList(getFromYear,getSelectorEle){ //experience-list month year append function
  getSelectorEle.find('.end-month option').not(':first').remove();
  getSelectorEle.find('.end-year option').not(':first').remove();
  monthDomEle = getSelectorEle.find('.end-month');
  yearDomEle = getSelectorEle.find('.end-year');
  monthDomEle.removeAttr('disabled');
  yearDomEle.removeAttr('disabled');
  showItems = {"monthEle":monthDomEle,"yearEle":yearDomEle,"startYearVal":getFromYear};
  loadEndOfYearMonthSelector(showItems) //passsing month and year DOM elements with start year value
}

function loadEndOfYearMonthSelector(getSelectorItems){
  const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  let qntYears = new Date().getFullYear() - getSelectorItems.startYearVal + 1;
  //let selectYear = $(".edu-to-year");
  //let selectMonth = $(".edu-to-month");
  let currentYear = new Date().getFullYear();

  for (var y = 0; y < qntYears; y++) {
    let yearElem = document.createElement("option");
    yearElem.value = currentYear
    yearElem.textContent = currentYear;
    getSelectorItems.yearEle.append(yearElem);
    currentYear--;
  }

  for (var m = 0; m < 12; m++) {
    let month = monthNames[m];
    let monthElem = document.createElement("option");
    monthElem.value = m+1;
    monthElem.textContent = month;
    getSelectorItems.monthEle.append(monthElem);
  }
}

function addressFromUpdate(checkFlag){
  getCurrentform = $("#primaryAddressForm");
  getPermanentform = $("#parmanentAddressForm");
  if(checkFlag == true){
    getPermanentform.find('.country-list').attr('disabled','').val(getCurrentform.find('.country-list').val());
    updateParmanentStateCityList(); //Update State list
    getPermanentform.find('.zip-code').attr('disabled','').val(getCurrentform.find('.zip-code').val());
    getPermanentform.find('.address-text-area').attr('disabled','').val(getCurrentform.find('.address-text-area').val());
  }else{
    getPermanentform.find('.country-list').removeAttr('disabled').val('');
    getPermanentform.find('.state-list').val('');
    getPermanentform.find('.city-list').val('');
    getPermanentform.find('.zip-code').removeAttr('disabled').val('');
    getPermanentform.find('.address-text-area').removeAttr('disabled').val('');
  }
}

function eduGapInputValidation(isActive){ //On checked to toggle required field of Education Gap Form.
	if(isActive){
		$(".collapse-list .edu-gap__from").each(function(){
			$(this).find("select").attr("required","")
			$(this).find("textarea").attr("required","")
		});
    $(".collapse-list .edu-str_line").each(function(){
			$(this).find("select").attr("required","")
			$(this).find("textarea").attr("required","")
		})
	}else{
		$(".collapse-list .edu-gap__from").each(function(){
			$(this).find("select").removeAttr("required");
			$(this).find("textarea").removeAttr("required");
		});
    $(".collapse-list .edu-str_line").each(function(){
			$(this).find("select").attr("required","")
			$(this).find("textarea").attr("required","")
		})
	}
}

function experGapInputValidation(isActive){ //On checked to toggle required field of Education Gap Form.
	if(isActive){
		$(".collapse-list .exper-gap__from").each(function(){
			$(this).find("select").attr("required","")
			$(this).find("textarea").attr("required","")
		});
    $(".collapse-list .exper-str_line").each(function(){
			$(this).find("select").attr("required","")
			$(this).find("textarea").attr("required","")
		})
	}else{
		$(".collapse-list .exper-gap__from").each(function(){
			$(this).find("select").removeAttr("required");
			$(this).find("textarea").removeAttr("required");
		});
    $(".collapse-list .exper-str_line").each(function(){
			$(this).find("select").attr("required","")
			$(this).find("textarea").attr("required","")
		})
	}
}

function contactNumByCountryCode(){
  var cChtml= "";
  var setCountryCode = [{"key":"AF","value":"93"},{"key":"AL","value":"355"},{"key":"DZ","value":"213"},{"key":"AS","value":"1684"},{"key":"AD","value":"376"},{"key":"AO","value":"244"},{"key":"AI","value":"1264"},{"key":"AQ","value":"0"},{"key":"AG","value":"1268"},{"key":"AR","value":"54"},{"key":"AM","value":"374"},{"key":"AW","value":"61"},{"key":"AU","value":"43"},{"key":"AT","value":"994"},{"key":"AZ","value":"1242"},{"key":"BS","value":"973"},{"key":"BH","value":"880"},{"key":"BD","value":"1246"},{"key":"BB","value":"375"},{"key":"BY","value":"32"},{"key":"BE","value":"501"},{"key":"BZ","value":"229"},{"key":"BJ","value":"1441"},{"key":"BM","value":"975"},{"key":"BT","value":"591"},{"key":"BO","value":"387"},{"key":"BA","value":"267"},{"key":"BW","value":"0"},{"key":"BV","value":"55"},{"key":"BR","value":"246"},{"key":"IO","value":"673"},{"key":"BG","value":"226"},{"key":"BF","value":"257"},{"key":"BI","value":"855"},{"key":"KH","value":"237"},{"key":"CM","value":"1"},{"key":"CA","value":"238"},{"key":"CV","value":"1345"},{"key":"KY","value":"236"},{"key":"CF","value":"235"},{"key":"TD","value":"56"},{"key":"CL","value":"86"},{"key":"CN","value":"61"},{"key":"CX","value":"672"},{"key":"CC","value":"57"},{"key":"CO","value":"269"},{"key":"KM","value":"242"},{"key":"CG","value":"242"},{"key":"CD","value":"682"},{"key":"CK","value":"506"},{"key":"CR","value":"225"},{"key":"CI","value":"385"},{"key":"HR","value":"53"},{"key":"CU","value":"357"},{"key":"CY","value":"420"},{"key":"CZ","value":"45"},{"key":"DK","value":"253"},{"key":"DJ","value":"1767"},{"key":"DM","value":"1809"},{"key":"DO","value":"670"},{"key":"TP","value":"593"},{"key":"EC","value":"20"},{"key":"EG","value":"503"},{"key":"GQ","value":"291"}];
  $.each(setCountryCode, function(czId){
    cChtml += "<option value="+setCountryCode[czId].key+"> +"+setCountryCode[czId].value+"</option>";
  })
  $("#cc-list").append(cChtml);
}


async function getCountryList(){
  var newCountryList;
  await $.get( "/company/all_countries",
  function( responsive ) {
    newCountryList = responsive;
  });
  setTimeout(function(){
     showList = "";
     var filterObj = newCountryList;
     $.each(filterObj, function(i){
      showList += "<option value="+filterObj[i].id+">"+filterObj[i].country_name+"</option>";
     })
     primaryCountryLs.append(showList);
     secoundCountryLs.append(showList);
     preferenceCountryLs.append(showList);
  },2500)
}

async function setStateList(getCounrtyCode){ //request of state list
  var changeStateLs;
  var fetchStateLs;
  await $.get("/company/all_states/"+getCounrtyCode,
  function( responsive ) {
    console.log(responsive)
    fetchStateLs = responsive;
  });
  console.log('fetchStateLs >>>>>>>>>>>>>.',fetchStateLs)
// fetchStateLs = [{"id":1,"country_name":"Afghanistan","states":[{"id":3901,"name":"Badakhshan"},{"id":3871,"name":"Badghis"},{"id":3875,"name":"Baghlan"},{"id":3884,"name":"Balkh"},{"id":3872,"name":"Bamyan"},{"id":3892,"name":"Daykundi"},{"id":3899,"name":"Farah"},{"id":3889,"name":"Faryab"},{"id":3870,"name":"Ghazni"},{"id":3888,"name":"Ghor"},{"id":3873,"name":"Helmand"},{"id":3887,"name":"Herat"},{"id":3886,"name":"Jowzjan"},{"id":3902,"name":"Kabul"},{"id":3890,"name":"Kandahar"},{"id":3879,"name":"Kapisa"},{"id":3878,"name":"Khost"},{"id":3876,"name":"Kunar"},{"id":3900,"name":"Kunduz Province"},{"id":3891,"name":"Laghman"},{"id":3897,"name":"Logar"},{"id":3882,"name":"Nangarhar"},{"id":3896,"name":"Nimruz"},{"id":3880,"name":"Nuristan"},{"id":3894,"name":"Paktia"},{"id":3877,"name":"Paktika"},{"id":3881,"name":"Panjshir"},{"id":3895,"name":"Parwan"},{"id":3883,"name":"Samangan"},{"id":3885,"name":"Sar-e Pol"},{"id":3893,"name":"Takhar"},{"id":3898,"name":"Urozgan"},{"id":3874,"name":"Zabul"}]}];
  $.each(fetchStateLs, function(objKey){
    if(fetchStateLs[objKey].id == getCounrtyCode){
      changeStateLs = fetchStateLs[objKey].states;
    }
  })
  return changeStateLs;
}

async function setCitiesList(getStateCode){ //request of Cities list
  var changeCityLs;
  console.log('check state code->>',getStateCode)
  await $.get( "/company/all_cities/"+getStateCode,
  function( responsive ) {
    fetchCitiesLs = responsive;
  });
// fetchCitiesLs = [{"id":3901,"state_name":"Badakhshan","cites":[{"id":52,"name":"Ashkasham","latitude":"36.68333000","longitude":"71.53333000"},{"id":68,"name":"Fayzabad","latitude":"37.11664000","longitude":"70.58002000"},{"id":78,"name":"Jurm","latitude":"36.86477000","longitude":"70.83421000"},{"id":84,"name":"Khandud","latitude":"36.95127000","longitude":"72.31800000"},{"id":115,"name":"Raghistan","latitude":"37.66079000","longitude":"70.67346000"},{"id":131,"name":"Wakhan","latitude":"37.05710000","longitude":"73.34928000"}]},{"id":3871,"state_name":"Badghis","cites":[{"id":72,"name":"Ghormach","latitude":"35.73062000","longitude":"63.78264000"},{"id":108,"name":"Qala i Naw","latitude":"34.98735000","longitude":"63.12891000"}]},{"id":3875,"state_name":"Baghlan","cites":[{"id":54,"name":"Baghlan","latitude":"36.13068000","longitude":"68.70829000"},{"id":140,"name":"?ukumati Dahanah-ye Ghori","latitude":"35.90617000","longitude":"68.48869000"},{"id":101,"name":"Nahrin","latitude":"36.06490000","longitude":"69.13343000"},{"id":105,"name":"Pul-e Khumri","latitude":"35.94458000","longitude":"68.71512000"}]},{"id":3884,"state_name":"Balkh","cites":[{"id":55,"name":"Balkh","latitude":"36.75635000","longitude":"66.89720000"},{"id":65,"name":"Dowlatabad","latitude":"36.98821000","longitude":"66.82069000"},{"id":85,"name":"Khulm","latitude":"36.69736000","longitude":"67.69826000"},{"id":91,"name":"Lab-Sar","latitude":"36.02634000","longitude":"66.83799000"},{"id":97,"name":"Mazar-e Sharif","latitude":"36.70904000","longitude":"67.11087000"},{"id":112,"name":"Qarchi Gak","latitude":"37.03999000","longitude":"66.78891000"}]},{"id":3872,"state_name":"Bamyan","cites":[{"id":57,"name":"Bamyan","latitude":"34.82156000","longitude":"67.82734000"},{"id":104,"name":"Panjab","latitude":"34.38795000","longitude":"67.02327000"}]},{"id":3892,"state_name":"Daykundi","cites":[{"id":102,"name":"Nili","latitude":"33.76329000","longitude":"66.07617000"}]},{"id":3899,"state_name":"Farah","cites":[{"id":66,"name":"Farah","latitude":"32.37451000","longitude":"62.11638000"}]}]
  $.each(fetchCitiesLs, function(objKey){
    if(fetchCitiesLs[objKey].id == getStateCode){
      changeCityLs = fetchCitiesLs[objKey].cities;
    }
  })
  return changeCityLs;
}

 function setCitiesListFilterByCountry(getCountryCode){ //request of cities list filter by country
  var changeFilterCityLs;
  console.log('check state code->>'+getCountryCode)
  /*$.get( "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/countries%2Bstates%2Bcities.json", 
  function( responsive ) {
    fetchLsItems = JSON.parse(responsive);
  });*/
 fetchCitiesLs = [{"id":1,"country_name":"Afghanistan","cites":[{"id":52,"name":"Ashkasham","latitude":"36.68333000","longitude":"71.53333000"},{"id":68,"name":"Fayzabad","latitude":"37.11664000","longitude":"70.58002000"},{"id":78,"name":"Jurm","latitude":"36.86477000","longitude":"70.83421000"},{"id":84,"name":"Khandud","latitude":"36.95127000","longitude":"72.31800000"},{"id":115,"name":"Raghistan","latitude":"37.66079000","longitude":"70.67346000"},{"id":131,"name":"Wakhan","latitude":"37.05710000","longitude":"73.34928000"}]},{"id":2,"country_name":"Albania","cites":[{"id":72,"name":"Ghormach","latitude":"35.73062000","longitude":"63.78264000"},{"id":108,"name":"Qala i Naw","latitude":"34.98735000","longitude":"63.12891000"}]},{"id":3,"country_name":"Algeria","cites":[{"id":54,"name":"Baghlan","latitude":"36.13068000","longitude":"68.70829000"},{"id":140,"name":"?ukumati Dahanah-ye Ghori","latitude":"35.90617000","longitude":"68.48869000"},{"id":101,"name":"Nahrin","latitude":"36.06490000","longitude":"69.13343000"},{"id":105,"name":"Pul-e Khumri","latitude":"35.94458000","longitude":"68.71512000"}]},{"id":4,"country_name":"American Samoa","cites":[{"id":55,"name":"Balkh","latitude":"36.75635000","longitude":"66.89720000"},{"id":65,"name":"Dowlatabad","latitude":"36.98821000","longitude":"66.82069000"},{"id":85,"name":"Khulm","latitude":"36.69736000","longitude":"67.69826000"},{"id":91,"name":"Lab-Sar","latitude":"36.02634000","longitude":"66.83799000"},{"id":97,"name":"Mazar-e Sharif","latitude":"36.70904000","longitude":"67.11087000"},{"id":112,"name":"Qarchi Gak","latitude":"37.03999000","longitude":"66.78891000"}]},{"id":5,"country_name":"Andorra","cites":[{"id":57,"name":"Bamyan","latitude":"34.82156000","longitude":"67.82734000"},{"id":104,"name":"Panjab","latitude":"34.38795000","longitude":"67.02327000"}]},{"id":3892,"state_name":"Daykundi","cites":[{"id":102,"name":"Nili","latitude":"33.76329000","longitude":"66.07617000"}]},{"id":6,"country_name":"Angola","cites":[{"id":66,"name":"Farah","latitude":"32.37451000","longitude":"62.11638000"}]}]
  $.each(fetchCitiesLs, function(objKey){
    if(fetchCitiesLs[objKey].id == getCountryCode){
      changeFilterCityLs = fetchCitiesLs[objKey].cites;
    }
  })
  return changeFilterCityLs;
 }

 function updateParmanentStateCityList(){
  $(".secoundry-state-ls option").remove();
  $(".secoundry-city-ls option").remove();
  var updateStateLs = "<option value="+$(".prm-state-ls option:selected").val()+" selected>"+$(".prm-state-ls option:selected").text()+"<option>";
  var updateCityLs = "<option value="+$(".prm-city-ls option:selected").val()+" selected>"+$(".prm-city-ls option:selected").text()+"<option>";
  $(".secoundry-state-ls").append(updateStateLs);
  $(".secoundry-city-ls").append(updateCityLs);
}

function prefrenceCustomFeildItems(getFiledItems){
  addListItem = "";
  addListItem += '<div class="col-4 mg-t-10 mg-lg-t-0 manual-feild__items">';
  $.each(getFiledItems, function(k){
    console.log(getFiledItems[k].title);
    addListItem += '<label>'+getFiledItems[k]['title']+':</label>';
    addListItem += '<input class="form-control" value="'+getFiledItems[k]['formVal']+'" required  type="text">';
  })
  addListItem += '</div>';
  $(".pref-addmore-btn").before(addListItem);
  $("#popUpModelClose").trigger('click');
}

window.addEventListener('DOMContentLoaded', (event) => { //window load function
  $(document).on('change','.edu-from-year',function(){ //education start year selector event
    var getStartYear = $(this).children("option:selected").val();
    var selectorElementProp = $(this).closest('.edu-middle-section').find('.end-date__selector');
    $(this).closest('.edu-form__container').find('.checked-edu-purse').prop("checked", false)
    if(getStartYear !== ''){
      //eduToStartYear(getStartYear);
      eduEndMonthYearList(getStartYear,selectorElementProp)
    }
  })
  $(document).on('change','.edugap-form-year',function(){ //education gap ->start year selector event
    var getStartYear = $(this).children("option:selected").val();
    var selectorElementProp = $(this).closest('.edugap-left-upper__section').next('.edugap-left-lower__section');
    if(getStartYear !== ''){
      //eduToStartYear(getStartYear);
      eduEndMonthYearList(getStartYear,selectorElementProp)
    }
  })

  $(document).on('change','.exper-gap-form-year',function(){ //Experience gap ->start year selector event
    var getStartYear = $(this).children("option:selected").val();
    var selectorElementProp = $(this).closest('.exper-gap-left-upper__section').next('.exper-gap-left-lower__section');
    if(getStartYear !== ''){
      //eduToStartYear(getStartYear);
      experienceEndMonthYearList(getStartYear,selectorElementProp)
    }
  })

  $(document).on('change','.expr-from-year',function(){ //Experience Details ->start year selector event
    var getStartYear = $(this).children("option:selected").val();
    var selectorElementProp = $(this).closest('.expr-middle-section').children().next().find('.inline-list__view');
    //console.log(selectorElementProp)
    if(getStartYear !== ''){
      //eduToStartYear(getStartYear);
      eduEndMonthYearList(getStartYear,selectorElementProp)
    }
  })
  
});

function contactNumberValid(){ //contact number validation function
  var input = document.querySelector("#phone-num"),
  errorMsg = document.querySelector("#error-msg"),
  validMsg = document.querySelector("#valid-msg");

// here, the index maps to the error code returned from getValidationError - see readme
var errorMap = ["Invalid number", "Invalid country code", "Too short", "Too long", "Invalid number"];

  var iti = window.intlTelInput(input, {
    utilsScript: "https://intl-tel-input.com/node_modules/intl-tel-input/build/js/utils.js?1613236686837"
  });
  
  var reset = function() {
    input.classList.remove("error");
    errorMsg.innerHTML = "";
    errorMsg.classList.add("vaild-msg-hide");
    validMsg.classList.add("vaild-msg-hide");
  };
  
  // on blur: validate
  input.addEventListener('blur', function() {
    reset();
    if (input.value.trim()) {
      if (iti.isValidNumber()) {
        validMsg.classList.remove("vaild-msg-hide");
      } else {
        input.classList.add("error");
        var errorCode = iti.getValidationError();
        errorMsg.innerHTML = errorMap[errorCode];
        errorMsg.classList.remove("vaild-msg-hide");
      }
    }
  });
  
  // on keyup / change flag: reset
  input.addEventListener('change', reset);
  input.addEventListener('keyup', reset);

}

function languageListPopulate(){ //language
//  var languageList = [{"Country":"Aruba","Language":"Dutch"},{"Country":"Aruba","Language":"English"},{"Country":"Aruba","Language":"Papiamento"},{"Country":"Aruba","Language":"Spanish"},{"Country":"Afghanistan","Language":"Balochi"},{"Country":"Afghanistan","Language":"Dari"},{"Country":"Afghanistan","Language":"Pashto"},{"Country":"Afghanistan","Language":"Turkmenian"},{"Country":"Afghanistan","Language":"Uzbek"},{"Country":"Angola","Language":"Ambo"},{"Country":"Angola","Language":"Chokwe"},{"Country":"Angola","Language":"Kongo"},{"Country":"Angola","Language":"Luchazi"},{"Country":"Angola","Language":"Luimbe-nganguela"},{"Country":"Angola","Language":"Luvale"},{"Country":"Angola","Language":"Mbundu"},{"Country":"Angola","Language":"Nyaneka-nkhumbi"},{"Country":"Angola","Language":"Ovimbundu"},{"Country":"Anguilla","Language":"English"},{"Country":"Albania","Language":"Albaniana"},{"Country":"Albania","Language":"Greek"},{"Country":"Albania","Language":"Macedonian"},{"Country":"Andorra","Language":"Catalan"},{"Country":"Andorra","Language":"French"},{"Country":"Andorra","Language":"Portuguese"},{"Country":"Andorra","Language":"Spanish"},{"Country":"Netherlands Antilles","Language":"Dutch"},{"Country":"Netherlands Antilles","Language":"English"},{"Country":"Netherlands Antilles","Language":"Papiamento"},{"Country":"United Arab Emirates","Language":"Arabic"},{"Country":"United Arab Emirates","Language":"Hindi"},{"Country":"Argentina","Language":"Indian Languages"},{"Country":"Argentina","Language":"Italian"},{"Country":"Argentina","Language":"Spanish"},{"Country":"Armenia","Language":"Armenian"},{"Country":"Armenia","Language":"Azerbaijani"},{"Country":"American Samoa","Language":"English"},{"Country":"American Samoa","Language":"Samoan"},{"Country":"American Samoa","Language":"Tongan"},{"Country":"Antigua and Barbuda","Language":"Creole English"},{"Country":"Antigua and Barbuda","Language":"English"},{"Country":"Australia","Language":"Arabic"},{"Country":"Australia","Language":"Canton Chinese"},{"Country":"Australia","Language":"English"},{"Country":"Australia","Language":"German"},{"Country":"Australia","Language":"Greek"},{"Country":"Australia","Language":"Italian"},{"Country":"Australia","Language":"Serbo-Croatian"},{"Country":"Australia","Language":"Vietnamese"},{"Country":"Austria","Language":"Czech"},{"Country":"Austria","Language":"German"},{"Country":"Austria","Language":"Hungarian"},{"Country":"Austria","Language":"Polish"},{"Country":"Austria","Language":"Romanian"},{"Country":"Austria","Language":"Serbo-Croatian"},{"Country":"Austria","Language":"Slovene"},{"Country":"Austria","Language":"Turkish"},{"Country":"Azerbaijan","Language":"Armenian"},{"Country":"Azerbaijan","Language":"Azerbaijani"},{"Country":"Azerbaijan","Language":"Lezgian"},{"Country":"Azerbaijan","Language":"Russian"},{"Country":"Burundi","Language":"French"},{"Country":"Burundi","Language":"Kirundi"},{"Country":"Burundi","Language":"Swahili"},{"Country":"Belgium","Language":"Arabic"},{"Country":"Belgium","Language":"Dutch"},{"Country":"Belgium","Language":"French"},{"Country":"Belgium","Language":"German"},{"Country":"Belgium","Language":"Italian"},{"Country":"Belgium","Language":"Turkish"},{"Country":"Benin","Language":"Adja"},{"Country":"Benin","Language":"Aizo"},{"Country":"Benin","Language":"Bariba"},{"Country":"Benin","Language":"Fon"},{"Country":"Benin","Language":"Ful"},{"Country":"Benin","Language":"Joruba"},{"Country":"Benin","Language":"Somba"},{"Country":"Burkina Faso","Language":"Busansi"},{"Country":"Burkina Faso","Language":"Dagara"},{"Country":"Burkina Faso","Language":"Dyula"},{"Country":"Burkina Faso","Language":"Ful"},{"Country":"Burkina Faso","Language":"Gurma"},{"Country":"Burkina Faso","Language":"Mossi"},{"Country":"Bangladesh","Language":"Bengali"},{"Country":"Bangladesh","Language":"Chakma"},{"Country":"Bangladesh","Language":"Garo"},{"Country":"Bangladesh","Language":"Khasi"},{"Country":"Bangladesh","Language":"Marma"},{"Country":"Bangladesh","Language":"Santhali"},{"Country":"Bangladesh","Language":"Tripuri"},{"Country":"Bulgaria","Language":"Bulgariana"},{"Country":"Bulgaria","Language":"Macedonian"},{"Country":"Bulgaria","Language":"Romani"},{"Country":"Bulgaria","Language":"Turkish"},{"Country":"Bahrain","Language":"Arabic"},{"Country":"Bahrain","Language":"English"},{"Country":"Bahamas","Language":"Creole English"},{"Country":"Bahamas","Language":"Creole French"},{"Country":"Bosnia and Herzegovina","Language":"Serbo-Croatian"},{"Country":"Belarus","Language":"Belorussian"},{"Country":"Belarus","Language":"Polish"},{"Country":"Belarus","Language":"Russian"},{"Country":"Belarus","Language":"Ukrainian"},{"Country":"Belize","Language":"English"},{"Country":"Belize","Language":"Garifuna"},{"Country":"Belize","Language":"Maya Languages"},{"Country":"Belize","Language":"Spanish"},{"Country":"Bermuda","Language":"English"},{"Country":"Bolivia","Language":"Aimará"},{"Country":"Bolivia","Language":"Guaraní"},{"Country":"Bolivia","Language":"Ketua"},{"Country":"Bolivia","Language":"Spanish"},{"Country":"Brazil","Language":"German"},{"Country":"Brazil","Language":"Indian Languages"},{"Country":"Brazil","Language":"Italian"},{"Country":"Brazil","Language":"Japanese"},{"Country":"Brazil","Language":"Portuguese"},{"Country":"Barbados","Language":"Bajan"},{"Country":"Barbados","Language":"English"},{"Country":"Brunei","Language":"Chinese"},{"Country":"Brunei","Language":"English"},{"Country":"Brunei","Language":"Malay"},{"Country":"Brunei","Language":"Malay-English"},{"Country":"Bhutan","Language":"Asami"},{"Country":"Bhutan","Language":"Dzongkha"},{"Country":"Bhutan","Language":"Nepali"},{"Country":"Botswana","Language":"Khoekhoe"},{"Country":"Botswana","Language":"Ndebele"},{"Country":"Botswana","Language":"San"},{"Country":"Botswana","Language":"Shona"},{"Country":"Botswana","Language":"Tswana"},{"Country":"Central African Republic","Language":"Banda"},{"Country":"Central African Republic","Language":"Gbaya"},{"Country":"Central African Republic","Language":"Mandjia"},{"Country":"Central African Republic","Language":"Mbum"},{"Country":"Central African Republic","Language":"Ngbaka"},{"Country":"Central African Republic","Language":"Sara"},{"Country":"Canada","Language":"Chinese"},{"Country":"Canada","Language":"Dutch"},{"Country":"Canada","Language":"English"},{"Country":"Canada","Language":"Eskimo Languages"},{"Country":"Canada","Language":"French"},{"Country":"Canada","Language":"German"},{"Country":"Canada","Language":"Italian"},{"Country":"Canada","Language":"Polish"},{"Country":"Canada","Language":"Portuguese"},{"Country":"Canada","Language":"Punjabi"},{"Country":"Canada","Language":"Spanish"},{"Country":"Canada","Language":"Ukrainian"},{"Country":"Cocos (Keeling) Islands","Language":"English"},{"Country":"Cocos (Keeling) Islands","Language":"Malay"},{"Country":"Switzerland","Language":"French"},{"Country":"Switzerland","Language":"German"},{"Country":"Switzerland","Language":"Italian"},{"Country":"Switzerland","Language":"Romansh"},{"Country":"Chile","Language":"Aimará"},{"Country":"Chile","Language":"Araucan"},{"Country":"Chile","Language":"Rapa nui"},{"Country":"Chile","Language":"Spanish"},{"Country":"China","Language":"Chinese"},{"Country":"China","Language":"Dong"},{"Country":"China","Language":"Hui"},{"Country":"China","Language":"Mantu"},{"Country":"China","Language":"Miao"},{"Country":"China","Language":"Mongolian"},{"Country":"China","Language":"Puyi"},{"Country":"China","Language":"Tibetan"},{"Country":"China","Language":"Tujia"},{"Country":"China","Language":"Uighur"},{"Country":"China","Language":"Yi"},{"Country":"China","Language":"Zhuang"},{"Country":"Cote d'Ivoire","Language":"Akan"},{"Country":"Cote d'Ivoire","Language":"Gur"},{"Country":"Cote d'Ivoire","Language":"Kru"},{"Country":"Cote d'Ivoire","Language":"Malinke"},{"Country":"Cote d'Ivoire","Language":"[South]Mande"},{"Country":"Cameroon","Language":"Bamileke-bamum"},{"Country":"Cameroon","Language":"Duala"},{"Country":"Cameroon","Language":"Fang"},{"Country":"Cameroon","Language":"Ful"},{"Country":"Cameroon","Language":"Maka"},{"Country":"Cameroon","Language":"Mandara"},{"Country":"Cameroon","Language":"Masana"},{"Country":"Cameroon","Language":"Tikar"},{"Country":"Congo, The Democratic Republic of the","Language":"Boa"},{"Country":"Congo, The Democratic Republic of the","Language":"Chokwe"},{"Country":"Congo, The Democratic Republic of the","Language":"Kongo"},{"Country":"Congo, The Democratic Republic of the","Language":"Luba"},{"Country":"Congo, The Democratic Republic of the","Language":"Mongo"},{"Country":"Congo, The Democratic Republic of the","Language":"Ngala and Bangi"},{"Country":"Congo, The Democratic Republic of the","Language":"Rundi"},{"Country":"Congo, The Democratic Republic of the","Language":"Rwanda"},{"Country":"Congo, The Democratic Republic of the","Language":"Teke"},{"Country":"Congo, The Democratic Republic of the","Language":"Zande"},{"Country":"Congo","Language":"Kongo"},{"Country":"Congo","Language":"Mbete"},{"Country":"Congo","Language":"Mboshi"},{"Country":"Congo","Language":"Punu"},{"Country":"Congo","Language":"Sango"},{"Country":"Congo","Language":"Teke"},{"Country":"Cook Islands","Language":"English"},{"Country":"Cook Islands","Language":"Maori"},{"Country":"Colombia","Language":"Arawakan"},{"Country":"Colombia","Language":"Caribbean"},{"Country":"Colombia","Language":"Chibcha"},{"Country":"Colombia","Language":"Creole English"},{"Country":"Colombia","Language":"Spanish"},{"Country":"Comoros","Language":"Comorian"},{"Country":"Comoros","Language":"Comorian-Arabic"},{"Country":"Comoros","Language":"Comorian-French"},{"Country":"Comoros","Language":"Comorian-madagassi"},{"Country":"Comoros","Language":"Comorian-Swahili"},{"Country":"Cape Verde","Language":"Crioulo"},{"Country":"Cape Verde","Language":"Portuguese"},{"Country":"Costa Rica","Language":"Chibcha"},{"Country":"Costa Rica","Language":"Chinese"},{"Country":"Costa Rica","Language":"Creole English"},{"Country":"Costa Rica","Language":"Spanish"},{"Country":"Cuba","Language":"Spanish"},{"Country":"Christmas Island","Language":"Chinese"},{"Country":"Christmas Island","Language":"English"},{"Country":"Cayman Islands","Language":"English"},{"Country":"Cyprus","Language":"Greek"},{"Country":"Cyprus","Language":"Turkish"},{"Country":"Czech Republic","Language":"Czech"},{"Country":"Czech Republic","Language":"German"},{"Country":"Czech Republic","Language":"Hungarian"},{"Country":"Czech Republic","Language":"Moravian"},{"Country":"Czech Republic","Language":"Polish"},{"Country":"Czech Republic","Language":"Romani"},{"Country":"Czech Republic","Language":"Silesiana"},{"Country":"Czech Republic","Language":"Slovak"},{"Country":"Germany","Language":"German"},{"Country":"Germany","Language":"Greek"},{"Country":"Germany","Language":"Italian"},{"Country":"Germany","Language":"Polish"},{"Country":"Germany","Language":"Southern Slavic Languages"},{"Country":"Germany","Language":"Turkish"},{"Country":"Djibouti","Language":"Afar"},{"Country":"Djibouti","Language":"Arabic"},{"Country":"Djibouti","Language":"Somali"},{"Country":"Dominica","Language":"Creole English"},{"Country":"Dominica","Language":"Creole French"},{"Country":"Denmark","Language":"Arabic"},{"Country":"Denmark","Language":"Danish"},{"Country":"Denmark","Language":"English"},{"Country":"Denmark","Language":"German"},{"Country":"Denmark","Language":"Norwegian"},{"Country":"Denmark","Language":"Swedish"},{"Country":"Denmark","Language":"Turkish"},{"Country":"Dominican Republic","Language":"Creole French"},{"Country":"Dominican Republic","Language":"Spanish"},{"Country":"Algeria","Language":"Arabic"},{"Country":"Algeria","Language":"Berberi"},{"Country":"Ecuador","Language":"Ketua"},{"Country":"Ecuador","Language":"Spanish"},{"Country":"Egypt","Language":"Arabic"},{"Country":"Egypt","Language":"Sinaberberi"},{"Country":"Eritrea","Language":"Afar"},{"Country":"Eritrea","Language":"Bilin"},{"Country":"Eritrea","Language":"Hadareb"},{"Country":"Eritrea","Language":"Saho"},{"Country":"Eritrea","Language":"Tigre"},{"Country":"Eritrea","Language":"Tigrigna"},{"Country":"Western Sahara","Language":"Arabic"},{"Country":"Spain","Language":"Basque"},{"Country":"Spain","Language":"Catalan"},{"Country":"Spain","Language":"Galecian"},{"Country":"Spain","Language":"Spanish"},{"Country":"Estonia","Language":"Belorussian"},{"Country":"Estonia","Language":"Estonian"},{"Country":"Estonia","Language":"Finnish"},{"Country":"Estonia","Language":"Russian"},{"Country":"Estonia","Language":"Ukrainian"},{"Country":"Ethiopia","Language":"Amharic"},{"Country":"Ethiopia","Language":"Gurage"},{"Country":"Ethiopia","Language":"Oromo"},{"Country":"Ethiopia","Language":"Sidamo"},{"Country":"Ethiopia","Language":"Somali"},{"Country":"Ethiopia","Language":"Tigrigna"},{"Country":"Ethiopia","Language":"Walaita"},{"Country":"Finland","Language":"Estonian"},{"Country":"Finland","Language":"Finnish"},{"Country":"Finland","Language":"Russian"},{"Country":"Finland","Language":"Saame"},{"Country":"Finland","Language":"Swedish"},{"Country":"Fiji Islands","Language":"Fijian"},{"Country":"Fiji Islands","Language":"Hindi"},{"Country":"Falkland Islands","Language":"English"},{"Country":"France","Language":"Arabic"},{"Country":"France","Language":"French"},{"Country":"France","Language":"Italian"},{"Country":"France","Language":"Portuguese"},{"Country":"France","Language":"Spanish"},{"Country":"France","Language":"Turkish"},{"Country":"Faroe Islands","Language":"Danish"},{"Country":"Faroe Islands","Language":"Faroese"},{"Country":"Micronesia, Federated States of","Language":"Kosrean"},{"Country":"Micronesia, Federated States of","Language":"Mortlock"},{"Country":"Micronesia, Federated States of","Language":"Pohnpei"},{"Country":"Micronesia, Federated States of","Language":"Trukese"},{"Country":"Micronesia, Federated States of","Language":"Wolea"},{"Country":"Micronesia, Federated States of","Language":"Yap"},{"Country":"Gabon","Language":"Fang"},{"Country":"Gabon","Language":"Mbete"},{"Country":"Gabon","Language":"Mpongwe"},{"Country":"Gabon","Language":"Punu-sira-nzebi"},{"Country":"United Kingdom","Language":"English"},{"Country":"United Kingdom","Language":"Gaeli"},{"Country":"United Kingdom","Language":"Kymri"},{"Country":"Georgia","Language":"Abhyasi"},{"Country":"Georgia","Language":"Armenian"},{"Country":"Georgia","Language":"Azerbaijani"},{"Country":"Georgia","Language":"Georgiana"},{"Country":"Georgia","Language":"Osseetti"},{"Country":"Georgia","Language":"Russian"},{"Country":"Ghana","Language":"Akan"},{"Country":"Ghana","Language":"Ewe"},{"Country":"Ghana","Language":"Ga-adangme"},{"Country":"Ghana","Language":"Gurma"},{"Country":"Ghana","Language":"Joruba"},{"Country":"Ghana","Language":"Mossi"},{"Country":"Gibraltar","Language":"Arabic"},{"Country":"Gibraltar","Language":"English"},{"Country":"Guinea","Language":"Ful"},{"Country":"Guinea","Language":"Kissi"},{"Country":"Guinea","Language":"Kpelle"},{"Country":"Guinea","Language":"Loma"},{"Country":"Guinea","Language":"Malinke"},{"Country":"Guinea","Language":"Susu"},{"Country":"Guinea","Language":"Yalunka"},{"Country":"Guadeloupe","Language":"Creole French"},{"Country":"Guadeloupe","Language":"French"},{"Country":"Gambia","Language":"Diola"},{"Country":"Gambia","Language":"Ful"},{"Country":"Gambia","Language":"Malinke"},{"Country":"Gambia","Language":"Soninke"},{"Country":"Gambia","Language":"Wolof"},{"Country":"Guinea-Bissau","Language":"Balante"},{"Country":"Guinea-Bissau","Language":"Crioulo"},{"Country":"Guinea-Bissau","Language":"Ful"},{"Country":"Guinea-Bissau","Language":"Malinke"},{"Country":"Guinea-Bissau","Language":"Mandyako"},{"Country":"Guinea-Bissau","Language":"Portuguese"},{"Country":"Equatorial Guinea","Language":"Bubi"},{"Country":"Equatorial Guinea","Language":"Fang"},{"Country":"Greece","Language":"Greek"},{"Country":"Greece","Language":"Turkish"},{"Country":"Grenada","Language":"Creole English"},{"Country":"Greenland","Language":"Danish"},{"Country":"Greenland","Language":"Greenlandic"},{"Country":"Guatemala","Language":"Cakchiquel"},{"Country":"Guatemala","Language":"Kekchí"},{"Country":"Guatemala","Language":"Mam"},{"Country":"Guatemala","Language":"Quiché"},{"Country":"Guatemala","Language":"Spanish"},{"Country":"French Guiana","Language":"Creole French"},{"Country":"French Guiana","Language":"Indian Languages"},{"Country":"Guam","Language":"Chamorro"},{"Country":"Guam","Language":"English"},{"Country":"Guam","Language":"Japanese"},{"Country":"Guam","Language":"Korean"},{"Country":"Guam","Language":"Philippene Languages"},{"Country":"Guyana","Language":"Arawakan"},{"Country":"Guyana","Language":"Caribbean"},{"Country":"Guyana","Language":"Creole English"},{"Country":"Hong Kong","Language":"Canton Chinese"},{"Country":"Hong Kong","Language":"Chiu chau"},{"Country":"Hong Kong","Language":"English"},{"Country":"Hong Kong","Language":"Fukien"},{"Country":"Hong Kong","Language":"Hakka"},{"Country":"Honduras","Language":"Creole English"},{"Country":"Honduras","Language":"Garifuna"},{"Country":"Honduras","Language":"Miskito"},{"Country":"Honduras","Language":"Spanish"},{"Country":"Croatia","Language":"Serbo-Croatian"},{"Country":"Croatia","Language":"Slovene"},{"Country":"Haiti","Language":"French"},{"Country":"Haiti","Language":"Haiti Creole"},{"Country":"Hungary","Language":"German"},{"Country":"Hungary","Language":"Hungarian"},{"Country":"Hungary","Language":"Romani"},{"Country":"Hungary","Language":"Romanian"},{"Country":"Hungary","Language":"Serbo-Croatian"},{"Country":"Hungary","Language":"Slovak"},{"Country":"Indonesia","Language":"Bali"},{"Country":"Indonesia","Language":"Banja"},{"Country":"Indonesia","Language":"Batakki"},{"Country":"Indonesia","Language":"Bugi"},{"Country":"Indonesia","Language":"Javanese"},{"Country":"Indonesia","Language":"Madura"},{"Country":"Indonesia","Language":"Malay"},{"Country":"Indonesia","Language":"Minangkabau"},{"Country":"Indonesia","Language":"Sunda"},{"Country":"India","Language":"Asami"},{"Country":"India","Language":"Bengali"},{"Country":"India","Language":"Gujarati"},{"Country":"India","Language":"Hindi"},{"Country":"India","Language":"Kannada"},{"Country":"India","Language":"Malajalam"},{"Country":"India","Language":"Marathi"},{"Country":"India","Language":"Orija"},{"Country":"India","Language":"Punjabi"},{"Country":"India","Language":"Tamil"},{"Country":"India","Language":"Telugu"},{"Country":"India","Language":"Urdu"},{"Country":"Ireland","Language":"English"},{"Country":"Ireland","Language":"Irish"},{"Country":"Iran","Language":"Arabic"},{"Country":"Iran","Language":"Azerbaijani"},{"Country":"Iran","Language":"Bakhtyari"},{"Country":"Iran","Language":"Balochi"},{"Country":"Iran","Language":"Gilaki"},{"Country":"Iran","Language":"Kurdish"},{"Country":"Iran","Language":"Luri"},{"Country":"Iran","Language":"Mazandarani"},{"Country":"Iran","Language":"Persian"},{"Country":"Iran","Language":"Turkmenian"},{"Country":"Iraq","Language":"Arabic"},{"Country":"Iraq","Language":"Assyrian"},{"Country":"Iraq","Language":"Azerbaijani"},{"Country":"Iraq","Language":"Kurdish"},{"Country":"Iraq","Language":"Persian"},{"Country":"Iceland","Language":"English"},{"Country":"Iceland","Language":"Icelandic"},{"Country":"Israel","Language":"Arabic"},{"Country":"Israel","Language":"Hebrew"},{"Country":"Israel","Language":"Russian"},{"Country":"Italy","Language":"Albaniana"},{"Country":"Italy","Language":"French"},{"Country":"Italy","Language":"Friuli"},{"Country":"Italy","Language":"German"},{"Country":"Italy","Language":"Italian"},{"Country":"Italy","Language":"Romani"},{"Country":"Italy","Language":"Sardinian"},{"Country":"Italy","Language":"Slovene"},{"Country":"Jamaica","Language":"Creole English"},{"Country":"Jamaica","Language":"Hindi"},{"Country":"Jordan","Language":"Arabic"},{"Country":"Jordan","Language":"Armenian"},{"Country":"Jordan","Language":"Circassian"},{"Country":"Japan","Language":"Ainu"},{"Country":"Japan","Language":"Chinese"},{"Country":"Japan","Language":"English"},{"Country":"Japan","Language":"Japanese"},{"Country":"Japan","Language":"Korean"},{"Country":"Japan","Language":"Philippene Languages"},{"Country":"Kazakstan","Language":"German"},{"Country":"Kazakstan","Language":"Kazakh"},{"Country":"Kazakstan","Language":"Russian"},{"Country":"Kazakstan","Language":"Tatar"},{"Country":"Kazakstan","Language":"Ukrainian"},{"Country":"Kazakstan","Language":"Uzbek"},{"Country":"Kenya","Language":"Gusii"},{"Country":"Kenya","Language":"Kalenjin"},{"Country":"Kenya","Language":"Kamba"},{"Country":"Kenya","Language":"Kikuyu"},{"Country":"Kenya","Language":"Luhya"},{"Country":"Kenya","Language":"Luo"},{"Country":"Kenya","Language":"Masai"},{"Country":"Kenya","Language":"Meru"},{"Country":"Kenya","Language":"Nyika"},{"Country":"Kenya","Language":"Turkana"},{"Country":"Kyrgyzstan","Language":"Kazakh"},{"Country":"Kyrgyzstan","Language":"Kirgiz"},{"Country":"Kyrgyzstan","Language":"Russian"},{"Country":"Kyrgyzstan","Language":"Tadzhik"},{"Country":"Kyrgyzstan","Language":"Tatar"},{"Country":"Kyrgyzstan","Language":"Ukrainian"},{"Country":"Kyrgyzstan","Language":"Uzbek"},{"Country":"Cambodia","Language":"Chinese"},{"Country":"Cambodia","Language":"Khmer"},{"Country":"Cambodia","Language":"Tam"},{"Country":"Cambodia","Language":"Vietnamese"},{"Country":"Kiribati","Language":"Kiribati"},{"Country":"Kiribati","Language":"Tuvalu"},{"Country":"Saint Kitts and Nevis","Language":"Creole English"},{"Country":"Saint Kitts and Nevis","Language":"English"},{"Country":"South Korea","Language":"Chinese"},{"Country":"South Korea","Language":"Korean"},{"Country":"Kuwait","Language":"Arabic"},{"Country":"Kuwait","Language":"English"},{"Country":"Laos","Language":"Lao"},{"Country":"Laos","Language":"Lao-Soung"},{"Country":"Laos","Language":"Mon-khmer"},{"Country":"Laos","Language":"Thai"},{"Country":"Lebanon","Language":"Arabic"},{"Country":"Lebanon","Language":"Armenian"},{"Country":"Lebanon","Language":"French"},{"Country":"Liberia","Language":"Bassa"},{"Country":"Liberia","Language":"Gio"},{"Country":"Liberia","Language":"Grebo"},{"Country":"Liberia","Language":"Kpelle"},{"Country":"Liberia","Language":"Kru"},{"Country":"Liberia","Language":"Loma"},{"Country":"Liberia","Language":"Malinke"},{"Country":"Liberia","Language":"Mano"},{"Country":"Libyan Arab Jamahiriya","Language":"Arabic"},{"Country":"Libyan Arab Jamahiriya","Language":"Berberi"},{"Country":"Saint Lucia","Language":"Creole French"},{"Country":"Saint Lucia","Language":"English"},{"Country":"Liechtenstein","Language":"German"},{"Country":"Liechtenstein","Language":"Italian"},{"Country":"Liechtenstein","Language":"Turkish"},{"Country":"Sri Lanka","Language":"Mixed Languages"},{"Country":"Sri Lanka","Language":"Singali"},{"Country":"Sri Lanka","Language":"Tamil"},{"Country":"Lesotho","Language":"English"},{"Country":"Lesotho","Language":"Sotho"},{"Country":"Lesotho","Language":"Zulu"},{"Country":"Lithuania","Language":"Belorussian"},{"Country":"Lithuania","Language":"Lithuanian"},{"Country":"Lithuania","Language":"Polish"},{"Country":"Lithuania","Language":"Russian"},{"Country":"Lithuania","Language":"Ukrainian"},{"Country":"Luxembourg","Language":"French"},{"Country":"Luxembourg","Language":"German"},{"Country":"Luxembourg","Language":"Italian"},{"Country":"Luxembourg","Language":"Luxembourgish"},{"Country":"Luxembourg","Language":"Portuguese"},{"Country":"Latvia","Language":"Belorussian"},{"Country":"Latvia","Language":"Latvian"},{"Country":"Latvia","Language":"Lithuanian"},{"Country":"Latvia","Language":"Polish"},{"Country":"Latvia","Language":"Russian"},{"Country":"Latvia","Language":"Ukrainian"},{"Country":"Macao","Language":"Canton Chinese"},{"Country":"Macao","Language":"English"},{"Country":"Macao","Language":"Mandarin Chinese"},{"Country":"Macao","Language":"Portuguese"},{"Country":"Morocco","Language":"Arabic"},{"Country":"Morocco","Language":"Berberi"},{"Country":"Monaco","Language":"English"},{"Country":"Monaco","Language":"French"},{"Country":"Monaco","Language":"Italian"},{"Country":"Monaco","Language":"Monegasque"},{"Country":"Moldova","Language":"Bulgariana"},{"Country":"Moldova","Language":"Gagauzi"},{"Country":"Moldova","Language":"Romanian"},{"Country":"Moldova","Language":"Russian"},{"Country":"Moldova","Language":"Ukrainian"},{"Country":"Madagascar","Language":"French"},{"Country":"Madagascar","Language":"Malagasy"},{"Country":"Maldives","Language":"Dhivehi"},{"Country":"Maldives","Language":"English"},{"Country":"Mexico","Language":"Mixtec"},{"Country":"Mexico","Language":"Náhuatl"},{"Country":"Mexico","Language":"Otomí"},{"Country":"Mexico","Language":"Spanish"},{"Country":"Mexico","Language":"Yucatec"},{"Country":"Mexico","Language":"Zapotec"},{"Country":"Marshall Islands","Language":"English"},{"Country":"Marshall Islands","Language":"Marshallese"},{"Country":"Macedonia","Language":"Albaniana"},{"Country":"Macedonia","Language":"Macedonian"},{"Country":"Macedonia","Language":"Romani"},{"Country":"Macedonia","Language":"Serbo-Croatian"},{"Country":"Macedonia","Language":"Turkish"},{"Country":"Mali","Language":"Bambara"},{"Country":"Mali","Language":"Ful"},{"Country":"Mali","Language":"Senufo and Minianka"},{"Country":"Mali","Language":"Songhai"},{"Country":"Mali","Language":"Soninke"},{"Country":"Mali","Language":"Tamashek"},{"Country":"Malta","Language":"English"},{"Country":"Malta","Language":"Maltese"},{"Country":"Myanmar","Language":"Burmese"},{"Country":"Myanmar","Language":"Chin"},{"Country":"Myanmar","Language":"Kachin"},{"Country":"Myanmar","Language":"Karen"},{"Country":"Myanmar","Language":"Kayah"},{"Country":"Myanmar","Language":"Mon"},{"Country":"Myanmar","Language":"Rakhine"},{"Country":"Myanmar","Language":"Shan"},{"Country":"Mongolia","Language":"Bajad"},{"Country":"Mongolia","Language":"Buryat"},{"Country":"Mongolia","Language":"Dariganga"},{"Country":"Mongolia","Language":"Dorbet"},{"Country":"Mongolia","Language":"Kazakh"},{"Country":"Mongolia","Language":"Mongolian"},{"Country":"Northern Mariana Islands","Language":"Carolinian"},{"Country":"Northern Mariana Islands","Language":"Chamorro"},{"Country":"Northern Mariana Islands","Language":"Chinese"},{"Country":"Northern Mariana Islands","Language":"English"},{"Country":"Northern Mariana Islands","Language":"Korean"},{"Country":"Northern Mariana Islands","Language":"Philippene Languages"},{"Country":"Mozambique","Language":"Chuabo"},{"Country":"Mozambique","Language":"Lomwe"},{"Country":"Mozambique","Language":"Makua"},{"Country":"Mozambique","Language":"Marendje"},{"Country":"Mozambique","Language":"Nyanja"},{"Country":"Mozambique","Language":"Ronga"},{"Country":"Mozambique","Language":"Sena"},{"Country":"Mozambique","Language":"Shona"},{"Country":"Mozambique","Language":"Tsonga"},{"Country":"Mozambique","Language":"Tswa"},{"Country":"Mauritania","Language":"Ful"},{"Country":"Mauritania","Language":"Hassaniya"},{"Country":"Mauritania","Language":"Soninke"},{"Country":"Mauritania","Language":"Tukulor"},{"Country":"Mauritania","Language":"Wolof"},{"Country":"Mauritania","Language":"Zenaga"},{"Country":"Montserrat","Language":"English"},{"Country":"Martinique","Language":"Creole French"},{"Country":"Martinique","Language":"French"},{"Country":"Mauritius","Language":"Bhojpuri"},{"Country":"Mauritius","Language":"Creole French"},{"Country":"Mauritius","Language":"French"},{"Country":"Mauritius","Language":"Hindi"},{"Country":"Mauritius","Language":"Marathi"},{"Country":"Mauritius","Language":"Tamil"},{"Country":"Malawi","Language":"Chichewa"},{"Country":"Malawi","Language":"Lomwe"},{"Country":"Malawi","Language":"Ngoni"},{"Country":"Malawi","Language":"Yao"},{"Country":"Malaysia","Language":"Chinese"},{"Country":"Malaysia","Language":"Dusun"},{"Country":"Malaysia","Language":"English"},{"Country":"Malaysia","Language":"Iban"},{"Country":"Malaysia","Language":"Malay"},{"Country":"Malaysia","Language":"Tamil"},{"Country":"Mayotte","Language":"French"},{"Country":"Mayotte","Language":"Mahoré"},{"Country":"Mayotte","Language":"Malagasy"},{"Country":"Namibia","Language":"Afrikaans"},{"Country":"Namibia","Language":"Caprivi"},{"Country":"Namibia","Language":"German"},{"Country":"Namibia","Language":"Herero"},{"Country":"Namibia","Language":"Kavango"},{"Country":"Namibia","Language":"Nama"},{"Country":"Namibia","Language":"Ovambo"},{"Country":"Namibia","Language":"San"},{"Country":"New Caledonia","Language":"French"},{"Country":"New Caledonia","Language":"Malenasian Languages"},{"Country":"New Caledonia","Language":"Polynesian Languages"},{"Country":"Niger","Language":"Ful"},{"Country":"Niger","Language":"Hausa"},{"Country":"Niger","Language":"Kanuri"},{"Country":"Niger","Language":"Songhai-zerma"},{"Country":"Niger","Language":"Tamashek"},{"Country":"Norfolk Island","Language":"English"},{"Country":"Nigeria","Language":"Bura"},{"Country":"Nigeria","Language":"Edo"},{"Country":"Nigeria","Language":"Ful"},{"Country":"Nigeria","Language":"Hausa"},{"Country":"Nigeria","Language":"Ibibio"},{"Country":"Nigeria","Language":"Ibo"},{"Country":"Nigeria","Language":"Ijo"},{"Country":"Nigeria","Language":"Joruba"},{"Country":"Nigeria","Language":"Kanuri"},{"Country":"Nigeria","Language":"Tiv"},{"Country":"Nicaragua","Language":"Creole English"},{"Country":"Nicaragua","Language":"Miskito"},{"Country":"Nicaragua","Language":"Spanish"},{"Country":"Nicaragua","Language":"Sumo"},{"Country":"Niue","Language":"English"},{"Country":"Niue","Language":"Niue"},{"Country":"Netherlands","Language":"Arabic"},{"Country":"Netherlands","Language":"Dutch"},{"Country":"Netherlands","Language":"Fries"},{"Country":"Netherlands","Language":"Turkish"},{"Country":"Norway","Language":"Danish"},{"Country":"Norway","Language":"English"},{"Country":"Norway","Language":"Norwegian"},{"Country":"Norway","Language":"Saame"},{"Country":"Norway","Language":"Swedish"},{"Country":"Nepal","Language":"Bhojpuri"},{"Country":"Nepal","Language":"Hindi"},{"Country":"Nepal","Language":"Maithili"},{"Country":"Nepal","Language":"Nepali"},{"Country":"Nepal","Language":"Newari"},{"Country":"Nepal","Language":"Tamang"},{"Country":"Nepal","Language":"Tharu"},{"Country":"Nauru","Language":"Chinese"},{"Country":"Nauru","Language":"English"},{"Country":"Nauru","Language":"Kiribati"},{"Country":"Nauru","Language":"Nauru"},{"Country":"Nauru","Language":"Tuvalu"},{"Country":"New Zealand","Language":"English"},{"Country":"New Zealand","Language":"Maori"},{"Country":"Oman","Language":"Arabic"},{"Country":"Oman","Language":"Balochi"},{"Country":"Pakistan","Language":"Balochi"},{"Country":"Pakistan","Language":"Brahui"},{"Country":"Pakistan","Language":"Hindko"},{"Country":"Pakistan","Language":"Pashto"},{"Country":"Pakistan","Language":"Punjabi"},{"Country":"Pakistan","Language":"Saraiki"},{"Country":"Pakistan","Language":"Sindhi"},{"Country":"Pakistan","Language":"Urdu"},{"Country":"Panama","Language":"Arabic"},{"Country":"Panama","Language":"Creole English"},{"Country":"Panama","Language":"Cuna"},{"Country":"Panama","Language":"Embera"},{"Country":"Panama","Language":"Guaymí"},{"Country":"Panama","Language":"Spanish"},{"Country":"Pitcairn","Language":"Pitcairnese"},{"Country":"Peru","Language":"Aimará"},{"Country":"Peru","Language":"Ketua"},{"Country":"Peru","Language":"Spanish"},{"Country":"Philippines","Language":"Bicol"},{"Country":"Philippines","Language":"Cebuano"},{"Country":"Philippines","Language":"Hiligaynon"},{"Country":"Philippines","Language":"Ilocano"},{"Country":"Philippines","Language":"Maguindanao"},{"Country":"Philippines","Language":"Maranao"},{"Country":"Philippines","Language":"Pampango"},{"Country":"Philippines","Language":"Pangasinan"},{"Country":"Philippines","Language":"Pilipino"},{"Country":"Philippines","Language":"Waray-waray"},{"Country":"Palau","Language":"Chinese"},{"Country":"Palau","Language":"English"},{"Country":"Palau","Language":"Palau"},{"Country":"Palau","Language":"Philippene Languages"},{"Country":"Papua New Guinea","Language":"Malenasian Languages"},{"Country":"Papua New Guinea","Language":"Papuan Languages"},{"Country":"Poland","Language":"Belorussian"},{"Country":"Poland","Language":"German"},{"Country":"Poland","Language":"Polish"},{"Country":"Poland","Language":"Ukrainian"},{"Country":"Puerto Rico","Language":"English"},{"Country":"Puerto Rico","Language":"Spanish"},{"Country":"North Korea","Language":"Chinese"},{"Country":"North Korea","Language":"Korean"},{"Country":"Portugal","Language":"Portuguese"},{"Country":"Paraguay","Language":"German"},{"Country":"Paraguay","Language":"Guaraní"},{"Country":"Paraguay","Language":"Portuguese"},{"Country":"Paraguay","Language":"Spanish"},{"Country":"Palestine","Language":"Arabic"},{"Country":"Palestine","Language":"Hebrew"},{"Country":"French Polynesia","Language":"Chinese"},{"Country":"French Polynesia","Language":"French"},{"Country":"French Polynesia","Language":"Tahitian"},{"Country":"Qatar","Language":"Arabic"},{"Country":"Qatar","Language":"Urdu"},{"Country":"Reunion","Language":"Chinese"},{"Country":"Reunion","Language":"Comorian"},{"Country":"Reunion","Language":"Creole French"},{"Country":"Reunion","Language":"Malagasy"},{"Country":"Reunion","Language":"Tamil"},{"Country":"Romania","Language":"German"},{"Country":"Romania","Language":"Hungarian"},{"Country":"Romania","Language":"Romani"},{"Country":"Romania","Language":"Romanian"},{"Country":"Romania","Language":"Serbo-Croatian"},{"Country":"Romania","Language":"Ukrainian"},{"Country":"Russian Federation","Language":"Avarian"},{"Country":"Russian Federation","Language":"Bashkir"},{"Country":"Russian Federation","Language":"Belorussian"},{"Country":"Russian Federation","Language":"Chechen"},{"Country":"Russian Federation","Language":"Chuvash"},{"Country":"Russian Federation","Language":"Kazakh"},{"Country":"Russian Federation","Language":"Mari"},{"Country":"Russian Federation","Language":"Mordva"},{"Country":"Russian Federation","Language":"Russian"},{"Country":"Russian Federation","Language":"Tatar"},{"Country":"Russian Federation","Language":"Udmur"},{"Country":"Russian Federation","Language":"Ukrainian"},{"Country":"Rwanda","Language":"French"},{"Country":"Rwanda","Language":"Rwanda"},{"Country":"Saudi Arabia","Language":"Arabic"},{"Country":"Sudan","Language":"Arabic"},{"Country":"Sudan","Language":"Bari"},{"Country":"Sudan","Language":"Beja"},{"Country":"Sudan","Language":"Chilluk"},{"Country":"Sudan","Language":"Dinka"},{"Country":"Sudan","Language":"Fur"},{"Country":"Sudan","Language":"Lotuko"},{"Country":"Sudan","Language":"Nubian Languages"},{"Country":"Sudan","Language":"Nuer"},{"Country":"Sudan","Language":"Zande"},{"Country":"Senegal","Language":"Diola"},{"Country":"Senegal","Language":"Ful"},{"Country":"Senegal","Language":"Malinke"},{"Country":"Senegal","Language":"Serer"},{"Country":"Senegal","Language":"Soninke"},{"Country":"Senegal","Language":"Wolof"},{"Country":"Singapore","Language":"Chinese"},{"Country":"Singapore","Language":"Malay"},{"Country":"Singapore","Language":"Tamil"},{"Country":"Saint Helena","Language":"English"},{"Country":"Svalbard and Jan Mayen","Language":"Norwegian"},{"Country":"Svalbard and Jan Mayen","Language":"Russian"},{"Country":"Solomon Islands","Language":"Malenasian Languages"},{"Country":"Solomon Islands","Language":"Papuan Languages"},{"Country":"Solomon Islands","Language":"Polynesian Languages"},{"Country":"Sierra Leone","Language":"Bullom-sherbro"},{"Country":"Sierra Leone","Language":"Ful"},{"Country":"Sierra Leone","Language":"Kono-vai"},{"Country":"Sierra Leone","Language":"Kuranko"},{"Country":"Sierra Leone","Language":"Limba"},{"Country":"Sierra Leone","Language":"Mende"},{"Country":"Sierra Leone","Language":"Temne"},{"Country":"Sierra Leone","Language":"Yalunka"},{"Country":"El Salvador","Language":"Nahua"},{"Country":"El Salvador","Language":"Spanish"},{"Country":"San Marino","Language":"Italian"},{"Country":"Somalia","Language":"Arabic"},{"Country":"Somalia","Language":"Somali"},{"Country":"Saint Pierre and Miquelon","Language":"French"},{"Country":"Sao Tome and Principe","Language":"Crioulo"},{"Country":"Sao Tome and Principe","Language":"French"},{"Country":"Suriname","Language":"Hindi"},{"Country":"Suriname","Language":"Sranantonga"},{"Country":"Slovakia","Language":"Czech and Moravian"},{"Country":"Slovakia","Language":"Hungarian"},{"Country":"Slovakia","Language":"Romani"},{"Country":"Slovakia","Language":"Slovak"},{"Country":"Slovakia","Language":"Ukrainian and Russian"},{"Country":"Slovenia","Language":"Hungarian"},{"Country":"Slovenia","Language":"Serbo-Croatian"},{"Country":"Slovenia","Language":"Slovene"},{"Country":"Sweden","Language":"Arabic"},{"Country":"Sweden","Language":"Finnish"},{"Country":"Sweden","Language":"Norwegian"},{"Country":"Sweden","Language":"Southern Slavic Languages"},{"Country":"Sweden","Language":"Spanish"},{"Country":"Sweden","Language":"Swedish"},{"Country":"Swaziland","Language":"Swazi"},{"Country":"Swaziland","Language":"Zulu"},{"Country":"Seychelles","Language":"English"},{"Country":"Seychelles","Language":"French"},{"Country":"Seychelles","Language":"Seselwa"},{"Country":"Syria","Language":"Arabic"},{"Country":"Syria","Language":"Kurdish"},{"Country":"Turks and Caicos Islands","Language":"English"},{"Country":"Chad","Language":"Arabic"},{"Country":"Chad","Language":"Gorane"},{"Country":"Chad","Language":"Hadjarai"},{"Country":"Chad","Language":"Kanem-bornu"},{"Country":"Chad","Language":"Mayo-kebbi"},{"Country":"Chad","Language":"Ouaddai"},{"Country":"Chad","Language":"Sara"},{"Country":"Chad","Language":"Tandjile"},{"Country":"Togo","Language":"Ane"},{"Country":"Togo","Language":"Ewe"},{"Country":"Togo","Language":"Gurma"},{"Country":"Togo","Language":"Kabyé"},{"Country":"Togo","Language":"Kotokoli"},{"Country":"Togo","Language":"Moba"},{"Country":"Togo","Language":"Naudemba"},{"Country":"Togo","Language":"Watyi"},{"Country":"Thailand","Language":"Chinese"},{"Country":"Thailand","Language":"Khmer"},{"Country":"Thailand","Language":"Kuy"},{"Country":"Thailand","Language":"Lao"},{"Country":"Thailand","Language":"Malay"},{"Country":"Thailand","Language":"Thai"},{"Country":"Tajikistan","Language":"Russian"},{"Country":"Tajikistan","Language":"Tadzhik"},{"Country":"Tajikistan","Language":"Uzbek"},{"Country":"Tokelau","Language":"English"},{"Country":"Tokelau","Language":"Tokelau"},{"Country":"Turkmenistan","Language":"Kazakh"},{"Country":"Turkmenistan","Language":"Russian"},{"Country":"Turkmenistan","Language":"Turkmenian"},{"Country":"Turkmenistan","Language":"Uzbek"},{"Country":"East Timor","Language":"Portuguese"},{"Country":"East Timor","Language":"Sunda"},{"Country":"Tonga","Language":"English"},{"Country":"Tonga","Language":"Tongan"},{"Country":"Trinidad and Tobago","Language":"Creole English"},{"Country":"Trinidad and Tobago","Language":"English"},{"Country":"Trinidad and Tobago","Language":"Hindi"},{"Country":"Tunisia","Language":"Arabic"},{"Country":"Tunisia","Language":"Arabic-French"},{"Country":"Tunisia","Language":"Arabic-French-English"},{"Country":"Turkey","Language":"Arabic"},{"Country":"Turkey","Language":"Kurdish"},{"Country":"Turkey","Language":"Turkish"},{"Country":"Tuvalu","Language":"English"},{"Country":"Tuvalu","Language":"Kiribati"},{"Country":"Tuvalu","Language":"Tuvalu"},{"Country":"Taiwan","Language":"Ami"},{"Country":"Taiwan","Language":"Atayal"},{"Country":"Taiwan","Language":"Hakka"},{"Country":"Taiwan","Language":"Mandarin Chinese"},{"Country":"Taiwan","Language":"Min"},{"Country":"Taiwan","Language":"Paiwan"},{"Country":"Tanzania","Language":"Chaga and Pare"},{"Country":"Tanzania","Language":"Gogo"},{"Country":"Tanzania","Language":"Ha"},{"Country":"Tanzania","Language":"Haya"},{"Country":"Tanzania","Language":"Hehet"},{"Country":"Tanzania","Language":"Luguru"},{"Country":"Tanzania","Language":"Makonde"},{"Country":"Tanzania","Language":"Nyakusa"},{"Country":"Tanzania","Language":"Nyamwesi"},{"Country":"Tanzania","Language":"Shambala"},{"Country":"Tanzania","Language":"Swahili"},{"Country":"Uganda","Language":"Acholi"},{"Country":"Uganda","Language":"Ganda"},{"Country":"Uganda","Language":"Gisu"},{"Country":"Uganda","Language":"Kiga"},{"Country":"Uganda","Language":"Lango"},{"Country":"Uganda","Language":"Lugbara"},{"Country":"Uganda","Language":"Nkole"},{"Country":"Uganda","Language":"Rwanda"},{"Country":"Uganda","Language":"Soga"},{"Country":"Uganda","Language":"Teso"},{"Country":"Ukraine","Language":"Belorussian"},{"Country":"Ukraine","Language":"Bulgariana"},{"Country":"Ukraine","Language":"Hungarian"},{"Country":"Ukraine","Language":"Polish"},{"Country":"Ukraine","Language":"Romanian"},{"Country":"Ukraine","Language":"Russian"},{"Country":"Ukraine","Language":"Ukrainian"},{"Country":"United States Minor Outlying Islands","Language":"English"},{"Country":"Uruguay","Language":"Spanish"},{"Country":"United States","Language":"Chinese"},{"Country":"United States","Language":"English"},{"Country":"United States","Language":"French"},{"Country":"United States","Language":"German"},{"Country":"United States","Language":"Italian"},{"Country":"United States","Language":"Japanese"},{"Country":"United States","Language":"Korean"},{"Country":"United States","Language":"Polish"},{"Country":"United States","Language":"Portuguese"},{"Country":"United States","Language":"Spanish"},{"Country":"United States","Language":"Tagalog"},{"Country":"United States","Language":"Vietnamese"},{"Country":"Uzbekistan","Language":"Karakalpak"},{"Country":"Uzbekistan","Language":"Kazakh"},{"Country":"Uzbekistan","Language":"Russian"},{"Country":"Uzbekistan","Language":"Tadzhik"},{"Country":"Uzbekistan","Language":"Tatar"},{"Country":"Uzbekistan","Language":"Uzbek"},{"Country":"Holy See (Vatican City State)","Language":"Italian"},{"Country":"Saint Vincent and the Grenadines","Language":"Creole English"},{"Country":"Saint Vincent and the Grenadines","Language":"English"},{"Country":"Venezuela","Language":"Goajiro"},{"Country":"Venezuela","Language":"Spanish"},{"Country":"Venezuela","Language":"Warrau"},{"Country":"Virgin Islands, British","Language":"English"},{"Country":"Virgin Islands, U.S.","Language":"English"},{"Country":"Virgin Islands, U.S.","Language":"French"},{"Country":"Virgin Islands, U.S.","Language":"Spanish"},{"Country":"Vietnam","Language":"Chinese"},{"Country":"Vietnam","Language":"Khmer"},{"Country":"Vietnam","Language":"Man"},{"Country":"Vietnam","Language":"Miao"},{"Country":"Vietnam","Language":"Muong"},{"Country":"Vietnam","Language":"Nung"},{"Country":"Vietnam","Language":"Thai"},{"Country":"Vietnam","Language":"Tho"},{"Country":"Vietnam","Language":"Vietnamese"},{"Country":"Vanuatu","Language":"Bislama"},{"Country":"Vanuatu","Language":"English"},{"Country":"Vanuatu","Language":"French"},{"Country":"Wallis and Futuna","Language":"Futuna"},{"Country":"Wallis and Futuna","Language":"Wallis"},{"Country":"Samoa","Language":"English"},{"Country":"Samoa","Language":"Samoan"},{"Country":"Samoa","Language":"Samoan-English"},{"Country":"Yemen","Language":"Arabic"},{"Country":"Yemen","Language":"Soqutri"},{"Country":"Yugoslavia","Language":"Albaniana"},{"Country":"Yugoslavia","Language":"Hungarian"},{"Country":"Yugoslavia","Language":"Macedonian"},{"Country":"Yugoslavia","Language":"Romani"},{"Country":"Yugoslavia","Language":"Serbo-Croatian"},{"Country":"Yugoslavia","Language":"Slovak"},{"Country":"South Africa","Language":"Afrikaans"},{"Country":"South Africa","Language":"English"},{"Country":"South Africa","Language":"Ndebele"},{"Country":"South Africa","Language":"Northsotho"},{"Country":"South Africa","Language":"Southsotho"},{"Country":"South Africa","Language":"Swazi"},{"Country":"South Africa","Language":"Tsonga"},{"Country":"South Africa","Language":"Tswana"},{"Country":"South Africa","Language":"Venda"},{"Country":"South Africa","Language":"Xhosa"},{"Country":"South Africa","Language":"Zulu"},{"Country":"Zambia","Language":"Bemba"},{"Country":"Zambia","Language":"Chewa"},{"Country":"Zambia","Language":"Lozi"},{"Country":"Zambia","Language":"Nsenga"},{"Country":"Zambia","Language":"Nyanja"},{"Country":"Zambia","Language":"Tongan"},{"Country":"Zimbabwe","Language":"English"},{"Country":"Zimbabwe","Language":"Ndebele"},{"Country":"Zimbabwe","Language":"Nyanja"},{"Country":"Zimbabwe","Language":"Shona"}];
  var optionHtml = "";
  // $.get("../../assets/js/bidcruit-scripts/language-list.json", function(data){
  //   languageList = data;
  // });
 

//console.log("languages>>",languageList)
$(".langMegaList .language-list").remove();
 $.each(languageList,function(countKey){
    optionHtml += "<option class='language-list' value='"+languageList[countKey]['Language']+"'>"+languageList[countKey]['Language']+"&nbsp;&nbsp;("+languageList[countKey]['Country']+")</option>";
    //optionHtml += "<li class='language-list' value='"+languageList[countKey]['Language']+"'>"+languageList[countKey]['Country']+"&nbsp;&nbsp;"+languageList[countKey]['Language']+"</li>"
  })
  //console.log(optionHtml)
  $(".langMegaList option:first-child").after(optionHtml)
}

/*function resetStartYearList(){
    var getYearInfo = $('#basicFormDatePicker').val();
    getYearInfo = getYearInfo.split('/');
    getYearInfo = getYearInfo[2];
    
    $(document).find('.edu-from-year').removeAttr('disabled');
     if(!getYearInfo == "" || !getYearInfo == "undefined"){
      $(document).find('.edu-from-year *option').remove()
      let currentYear = new Date().getFullYear();
      let yearRange = new Date().getFullYear() - parseInt(getYearInfo);
      for (var y = 0; y < yearRange; y++) {
        let yearElem = document.createElement("option");
        yearElem.value = currentYear
        yearElem.textContent = currentYear;
        console.log(yearElem)
        $(document).find('.edu-from-year').append(yearElem);
        currentYear--;
      }
     }else{
       alert("Your DOB is required...")
     }
}*/