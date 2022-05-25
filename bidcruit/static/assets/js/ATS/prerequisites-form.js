var demo_data = `[
    {
      "finishKey": 1,
      "template-name": "lolwa",
      "template-data": [
        {
          "question_label": "Question 1",
          "option_list": [
            {
              "option_label": "q1 option 1",
              "option_value": "next",
              "questions": []
            },
            {
              "option_label": "q1 option 2",
              "option_value": "add-question",
              "questions": [
                {
                  "question_label": "Sub Question 1",
                  "option_list": [
                    {
                      "option_label": "sbq1 option 1",
                      "option_value": "next",
                      "questions": []
                    },
                    {
                      "option_label": "sbq1 option 2",
                      "option_value": "exit",
                      "questions": []
                    }
                  ]
                }
              ]
            },
            {
              "option_label": "q1 option 3",
              "option_value": "next",
              "questions": []
            }
          ]
        },
        {
          "question_label": "Question 2 ",
          "option_list": [
            {
              "option_label": "q2 option 1",
              "option_value": "next",
              "questions": []
            },
            {
              "option_label": "q2 option 2",
              "option_value": "exit",
              "questions": []
            }
          ]
        },
        {
          "question_label": "Question 3",
          "option_list": [
            {
              "option_label": "q3 option 1",
              "option_value": "exit",
              "questions": []
            },
            {
              "option_label": "q3 option 2",
              "option_value": "next",
              "questions": []
            }
          ]
        }
      ]
    }
  ]`




$(document).ready(function(){
    var FormInputFieldValidFlag = false
    console.log("page loaded");
    init();

    $(document).on('click','#addMoreQueList',function(){ // Add more Parent Question List
        
        var getMainQueLength = $(this).closest('.xs-form_layout').find(".question_main-layer").length;
        if(getMainQueLength == 0){
            getDataItem = 1;
        }
        else{
            var getDataItem = $(this).closest('.xs-form_layout').find(".question_main-layer").last().attr('data-item');
            getDataItem = parseInt(getDataItem.split('-')[1])+1;
            //console.log(getDataItem)
        }
        var newQueListClone = "";
        newQueListClone += `<div class="question_main-layer" data-item="lavel-`+getDataItem+`">
                                <div class="row fxs-row bd rounded-20 question-section">
                                    <div class="col-12 queue-col pd-t-0 pd-b-0 pd-r-20 mg-b-10">
                                        <div class="fx-left fx-col que-text">
                                            <div class="count-of-que"> 
                                                <span class="text-lap act">Question</span>
                                            </div>
                                        </div>
                                        <div class="field-ls ques_text-area mg-t-5 mg-b-5 bd bd-10 pd-5 rounded-10">
                                            <div class="que-count__number bg-primary">1</div>
                                            <input type="text" class="que-text__input pd-l-10" data-item="ques-text-`+getDataItem+`" placeholder="add new query..." name="query-text" value="">
                                        </div>
                                        <div class="fx-right fx-col">
                                            <p class="show-btn delete-btn question-tab-delete"><i class="fas fa-trash-alt"></i></p>
                                        </div>
                                    </div>
                                    <div class="col-12 que_table pd-l-20 pd-r-20 mg-t-20 mg-b-20" data-item="queContainer-`+getDataItem+`">
                                        <div class="field-ls show-option_ls" data-item="OptWrapper-`+getDataItem+`">
                                            
                                        <div class="select-input__field" data-item="option-`+getDataItem+`">
                                            <div class="pd-t-10 pd-b-0 mg-b-0">
                                                <div class="opt-list__view optSectionContainer-`+getDataItem+`">
                                                    <span class="point_bule"></span>
                                                    <input class="queOptionTitle" type="text" name="option-text" value="" placeholder="add option text here.." data-item="optionText-`+getDataItem+`-`+getDataItem+`">
                                                    <div class="align-right_selector pd-r-40">
                                                    <select class="queOptionSelector form-select form-select-lg mb-3" name="option-select" data-item="optionSelector-`+getDataItem+`-`+getDataItem+`">
                                                        <option label="Choose one"></option>
                                                        <option value="next">Next</option>
                                                        <option value="exit">Exit</option>
                                                        <option value="add-question">Question</option>
                                                    </select>
                                                   
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="select-input__field" data-item="option-`+getDataItem+`">
                                            <div class="pd-t-10 pd-b-0 mg-b-0">
                                                <div class="opt-list__view optSectionContainer-`+getDataItem+`">
                                                    <span class="point_bule"></span>
                                                    <input class="queOptionTitle" type="text" name="option-text" value="" placeholder="add option text here.." data-item="optionText-`+getDataItem+`-`+getDataItem+`">
                                                    <div class="align-right_selector pd-r-40">
                                                    <select class="queOptionSelector form-select form-select-lg mb-3" name="option-select" data-item="optionSelector-`+getDataItem+`-`+getDataItem+`">
                                                        <option label="Choose one"></option>
                                                        <option value="next">Next</option>
                                                        <option value="exit">Exit</option>
                                                        <option value="add-question">Question</option>
                                                    </select>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        </div>
                                        <div class="add-more__option-section mg-b-10">
                                            <div class="addMoreOptLs"> <i class="fas fa-plus-circle"></i>Add New Option</div>
                                        </div>
                                    </div>
                                </div>
                            </div>`;

            $(this).closest('.add-new-que__tab').before(newQueListClone);

    })

    $(document).on('click','.question-tab-delete',function(){
        $(this).closest('.question_main-layer').remove();
    })
    $(document).on('change','.que-text__input', function(){// Question Text value set in value-attr
        $(this).attr('value',$(this).val())
    })
    $(document).on('change','.queOptionTitle', function(){ //Option Text value set in value-attr
        $(this).attr('value',$(this).val())
    })

    $(document).on('click','.addMoreOptLs',function(){ // Add More Option inside the Question List
        var addOptionTab = "";
        var lavelText = "";
        var getMainQueLength = $(this).closest('.question_main-layer').length;
        var optListLength =  $(this).parent().prev('.show-option_ls').find('.select-input__field').length;
        //console.log('option ls lenght'+optListLength);
        if(optListLength == 0){
            optQueueIndexOf = 1;
            console.log("IniCount---",optQueueIndexOf)
        }
        else{
            var mainListIndexOf = $(this).closest('.xs-form_layout').find(".question_main-layer").last().attr('data-item');
            //var optQueueIndexOf = $(this).closest('.que_table').attr('data-item');
            var getSelectorList = $(this).parent().prev('.show-option_ls').find(".select-input__field").last().attr('data-item');
            console.log(getSelectorList)
            optQueueIndexOf = parseInt(getSelectorList.split('-')[1]) + 1;
            console.log(optQueueIndexOf)
        }

        addOptionTab += `<div class="select-input__field" data-item="option-`+optQueueIndexOf+`">
                            <div class="pd-t-10 pd-b-0 mg-b-0">
                                <div class="opt-list__view optSectionContainer-`+optQueueIndexOf+`">
                                    <span class="point_bule"></span>
                                    <input class="queOptionTitle" type="text" name="option-text" value="" placeholder="add option text here.." data-item="optionText-`+mainListIndexOf+`-`+optQueueIndexOf+`">
                                    <div class="align-right_selector">
                                    <select class="queOptionSelector form-select form-select-lg mb-3" name="option-select" data-item="optionSelector-`+mainListIndexOf+`-`+optQueueIndexOf+`">
                                        <option label="Choose one"></option>
                                        <option value="next">Next</option>
                                        <option value="exit">Exit</option>
                                        <option value="add-question">Question</option>
                                    </select>
                                    <div class="delete_option-ls"> <i class="fas fa-times-circle"></i></div>
                                    </div>
                                </div>
                            </div>
                        </div>`;
        // console.log($(this).parent().find('.show-option_ls'))
        console.log("add more option ",$(this).closest('.que_table').children(".show-option_ls"))
        $(this).closest('.que_table').children(".show-option_ls").append(addOptionTab);
        // $(this)
        // .closest('.que_table')
        // .find('.show-option_ls')
        // .append(addOptionTab);
    })

    $(document).on('click','.delete_option-ls',function(){ //remove option selector list
        $(this).closest('.select-input__field').remove();
    })

    $(document).on('change','.queOptionSelector',function(){ //add child Question form onchange to Select dropdown
        var childForm = "";
        var getOptionVal = $(this).find("option:selected").val();
        $(this).closest('.opt-list__view').find('.queOptionMarkOpt').val(getOptionVal);
        switch (getOptionVal){
            case "add-question":
                getQueId = parseInt($(this).closest('.question_main-layer').attr('data-item').split('-')[1]);
                childForm =`<div class="question_main-layer quesize" data-item="child-lavel-`+getQueId+`">
                                <div class="row fxs-row bd rounded-20 question-section">
                                <div class="col-12 queue-col pd-t-0 pd-b-0 pd-r-20 mg-b-10 rounded-20">
                                    <div class="fx-left fx-col que-text">
                                        <div class="count-of-que"> 
                                            <span class="text-lap act">Question</span>
                                        </div>
                                    </div>
                                    <div class="field-ls ques_text-area mg-t-5 mg-b-5 bd bd-10 pd-5 rounded-10">
                                        <div class="que-count__number bg-primary">1</div>
                                        <input type="text" class="que-text__input pd-l-10" name="child-query-text" placeholder="add new query..." value="">
                                    </div>
                                    <div class="fx-right fx-col">
                                        <p class="show-btn delete-btn question-tab-delete"><i class="fas fa-trash-alt"></i></p>
                                    </div>
                                </div>
                                <div class="col-12 que_table pd-l-20 pd-r-20 mg-t-20 mg-b-20">
                                    <div class="field-ls show-option_ls">   
                                        <div class="select-input__field" data-item="option-1">
                                            <div class="pd-t-10 pd-b-0 mg-b-0">
                                            <div class="opt-list__view optSectionContainer-1">
                                                <span class="point_bule"></span>
                                                <input class="queOptionTitle" type="text" name="option-text" value="" placeholder="add option text here.." data-item="optionText-undefined-1">
                                                <div class="align-right_selector">
                                                    <select class="queOptionSelector form-select form-select-lg mb-3" name="option-select" data-item="optionSelector-undefined-1">
                                                        <option label="Choose one"></option>
                                                        <option value="next">Next</option>
                                                        <option value="exit">Exit</option>
                                                        <option value="add-question">Question</option>
                                                    </select>
                                                </div>
                                            </div>
                                            </div>
                                        </div>
                                        <div class="select-input__field" data-item="option-2">
                                            <div class="pd-t-10 pd-b-0 mg-b-0">
                                            <div class="opt-list__view optSectionContainer-2">
                                                <span class="point_bule"></span>
                                                <input class="queOptionTitle" type="text" name="option-text" value="" placeholder="add option text here.." data-item="optionText-undefined-2">
                                                <div class="align-right_selector">
                                                    <select class="queOptionSelector form-select form-select-lg mb-3" name="option-select" data-item="optionSelector-undefined-2">
                                                        <option label="Choose one"></option>
                                                        <option value="next">Next</option>
                                                        <option value="exit">Exit</option>
                                                        <option value="add-question">Question</option>
                                                    </select>
                                                </div>
                                            </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="add-more__option-section mg-b-10">
                                        <div class="addMoreOptLs"> <i class="fas fa-plus-circle"></i>Add New Option</div>
                                    </div>
                                </div>
                                </div>
                            </div>`;

                $(this).closest('.opt-list__view').after(childForm);
                break;
            case "next":
                    $(this).closest('.opt-list__view').next().remove();
                    //$(this).prop('selectedIndex',0)
                break;
            case "exit":
                    $(this).closest('.opt-list__view').next().remove();
                    //$(this).prop('selectedIndex',0)
                break;
            default:
        }
        $(this).find("option").removeAttr('selected')
        $(this).find("option:selected").attr('selected','')
    });

    $(document).on('click','.submitForm', function(){ //form submit and save form items
        $("#previewFormLayout").html('');
        let allAreFilled = true;
        let maxSizeOfOptions = 0;
        var AllTextElements =  document.getElementById("mcqForm").querySelectorAll(".que-text__input,.queOptionTitle,.queOptionSelector")
        var inputOptionsSize = document.getElementById("mcqForm").querySelectorAll(".select-input__field")
        // $(AllTextElements).parent().css("border","0px")
        AllTextElements.forEach(function(i) {
            //console.log("the vlaue is",i.value)
            if (!i.value){
                allAreFilled = false;
                if($(i).hasClass('form-select')){ $(i).addClass("actValidFiled") }else{ $(i).parent().addClass("actValidFiled") }
            }else{
                if($(i).hasClass('form-select')){ $(i).removeClass("actValidFiled")}else{ $(i).parent().removeClass("actValidFiled")  }
            }
        })
        inputOptionsSize.forEach(function(countVal){maxSizeOfOptions = $(countVal).closest('.show-option_ls').find('.select-input__field').length}) // atleast 2 option is required to each questions

        if($('#finishFormKey').is(':checked') && allAreFilled && maxSizeOfOptions > "1"){ //final form submit action (question verify by form checked button action)
            $("#triggerModelBtn").trigger('click');
            // console.log("preview html",$(document).find(".xs-form_layout").clone());
            // $(document).find(".xs-form_layout").clone().appendTo("#previewFormLayout");
        }
        FormInputFieldValidFlag = allAreFilled
    })

    $(document).on('click','#finishFormKey',function(){
        if($(this).is(':checked')){
           $('.submitForm').attr('data-item','submitform-true').addClass('enable')
        }else{
            $('.submitForm').attr('data-item','submitform-false').removeClass('enable')
        }
    })

    $(document).on('click','#formSubmit',function(){
    //    var getTempName = $("#conformFormSubmitModel").find('.template-name').val();
       
        formDataCollection = [];
        var getLengthOfQueTabs = $(".xs-form_layout .question_main-layer").length;
        var currentSuperElement = $(".xs-form_layout");
        if(getLengthOfQueTabs){
            var getAllQuesDataItems = collectFormData(currentSuperElement);
            console.log("the the function returned",getAllQuesDataItems)
            var htmlData = $("#mcqForm").html()
            formDataCollection.push({"finishKey":1,"template-data":getAllQuesDataItems,"html-data":htmlData})
            //add ajax request here
            console.log("the josn data isssss",JSON.stringify(formDataCollection))
            
            //this should be added after the preview!!!!!!!
           if(FormInputFieldValidFlag == true){
                $.ajax({
                    url:"/company/save_pre_requisites/",
                    headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                    type:'POST',
                    contentType: 'application/json; charset=UTF-8',
                    data: JSON.stringify(formDataCollection),
                    error: function (request, status, error) {
                        alert(error);
                    }
                }).done(function(response){
                    response= JSON.parse(response);
                        if(response['status']==true){
                            window.location.replace('/company/template_listing/');
                            //window.location.href=response['url']
                        }
                })
           }
            

        }
       
    })

   $(document).on('change',".queOptionSelector",function(){
    var saveValidationInputs = [];
    var getinputValidItem = "";
    var getEleOfLs = $(this).closest('.show-option_ls')
    console.log("childreeeeeennnn",getEleOfLs.children())
    var AllOptions = getEleOfLs.children('.select-input__field')
    count = 0;
    $.each(AllOptions,function(key){
        SelectedOption =AllOptions.eq(key).children().children().children().find('.queOptionSelector').val()
        console.log("the selected texts are",AllOptions.eq(key).children().children().children().find('.queOptionSelector').val())
        if(SelectedOption == "exit")
        {
            count +=1
        }
    })
    if(count == AllOptions.length )
    {   
        alert("All options cannot be exit")
        $(this).prop('selectedIndex',0);
        //$(this).closest('.opt-list__view').find('.queOptionMarkOpt').val('')
    }
   })

});

/****
add all functions
***/

function checkInputValidation(getOptCount){
    var setIntputFlag = [];
    var validStatusKey = false;
    if(getOptCount > 1){
        var updateValidData = [{"flag":false,"check_fields":count}]
        localStorage.setItem('formreq_valid', JSON.stringify(updateValidData));
    }
    var getinputValidItem = JSON.parse(localStorage.getItem('formreq_valid'));
   // console.log(getinputValidItem[0]['check_fields'])
    if(getinputValidItem[0]['check_fields'] > 1){
        setIntputFlag = [{"flag":false,"check_fields":1}]
        localStorage.setItem('formreq_valid', JSON.stringify(setIntputFlag));
        validStatusKey = true;
    }
    console.log("check flag of selected option >>>",validStatusKey)
    return validStatusKey;
}

dbConnection = false;
function init(){
    console.log("init-> default function loaded here");
    setInterval(function(){ //local-storage sync within 700ms
        storageVisible();
    }, 700);
}

function storageVisible(){
    var preReqiestFormData = localStorage.getItem('prerequisites_data');
    var formValidationItems =  localStorage.getItem('formreq_valid');
    if (preReqiestFormData!== null && formValidationItems !== null) {
       dbConnection = true;
    } else {
        storeFormData = [];
        validations = [{"flag":false,"check_fields":0}]
        localStorage.setItem("prerequisites_data",JSON.stringify(storeFormData));
        localStorage.setItem("formreq_valid",JSON.stringify(validations));
    }
}


function collectFormData(sizeOfQueLs){
   var addParentFormData = [];
    console.log("sizeof quels is",sizeOfQueLs)
    var getElementOfParentQueLs = sizeOfQueLs.children('.question_main-layer');
    $.each(getElementOfParentQueLs, function(index){
        var getQueText = $(this).find('.queue-col .que-text__input').val();
        //console.log("Question Text>>>>>>>",getElementOfParentQueLs.children().children()[0].find('.ques_text-area').val())
        //console.log("Question By Index Div>>",$($($(getElementOfParentQueLs.eq(index).children()).children()[1])).children()[0])

        //var newQuestionObj = getElementOfParentQueLs.eq(index)
        var newQuestionObj = $($($(getElementOfParentQueLs.eq(index).children()).children()[1])).children()[0]
        var fetchAllOptions = optionListView(newQuestionObj);
        var tempOptionList = [];
        // console.log(fetchAllOptions[0]+''+fetchAllOptions[1]+''+fetchAllOptions[2])
        console.log("all options of thos question are",fetchAllOptions)
      $.each(fetchAllOptions,function(k){
            console.log('optionsss>>>>>---',$(fetchAllOptions).eq(k).find('.queOptionTitle').val())
            var getAllQuestion = collectFormData($(fetchAllOptions).eq(k).children());
            var getOptionInputText = $(fetchAllOptions).eq(k).find('.queOptionTitle').val()
            var getSelectedOptionAction = $(fetchAllOptions).eq(k).find('.queOptionSelector option:selected').val()
            var option = new Option(getOptionInputText,getSelectedOptionAction,getAllQuestion)
            tempOptionList.push(option)
            console.log(tempOptionList);
        })
        //console.log("getAllObjList",tempOptionList)
        // var question_label =$($(question).children("input")[0]).val()
        var final_question = new Question(getQueText,tempOptionList)
        console.log("question is",final_question)
        addParentFormData.push(final_question)
    })
    return addParentFormData
}

function optionListView(getListDomEle){ //option list items collect
    //var tempOptionObjctList = [];
    //var optionDiv = $($($(getListDomEle.children()[0]).children()[1]).children()[1]).children('.select-input__field');
    var optionDiv = $(getListDomEle).children('.select-input__field');
    return optionDiv;
    /*$.each(optionDiv,function(k){
        var getOptionInputText = optionDiv.eq(k).find('.queOptionTitle').val()
        var getSelectedOptionActionV = optionDiv.eq(k).find('.queOptionSelector option:selected').val()
        //var textOfOption = $($($($(optionDiv.children()[0]).children()[0]).children()[0])).find('.queOptionTitle').val();
        //var selectedOption =  $($($($(optionDiv.children()[0]).children()[0]).children()[0]).children()[0]).find('.queOptionSelector
    })*/
}

class Option{
    constructor(option_label,option_value,questions=[])
    {
        this.option_label = option_label
        this.option_value=  option_value
        //this.option_action = option_action
        this.questions = questions
    }
}
class Question{
    constructor(question_label,option_list=[])
    {
        this.question_label = question_label
        this.option_list = option_list
    }
}
