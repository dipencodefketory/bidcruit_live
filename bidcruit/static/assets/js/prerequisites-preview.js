$(document).ready(function(){
    // var getQuesListItems = [{"finishKey":1,"template-name":"MCQ's","template-data":[{"question_label":"Several computers linked to a server to share programs and storage space?","option_list":[{"option_label":"Library","option_value":"next","questions":[]},{"option_label":"Network","option_value":"add-question","questions":[{"question_label":"A term related sending data to a satellite is?","option_list":[{"option_label":"Uplink","option_value":"next","questions":[]},{"option_label":"Modulate","option_value":"exit","questions":[]}]}]},{"option_label":"Grouping","option_value":"exit","questions":[]}]},{"question_label":"Which of the following device is used to connect two systems especially if the systems use different protocols?","option_list":[{"option_label":"Gateway","option_value":"next","questions":[]},{"option_label":"Bridge","option_value":"exit","questions":[]}]},{"question_label":"What is a benefit of networking your computer with other computers?","option_list":[{"option_label":"Sharing of cables to cut down on expenses and clutter","option_value":"exit","questions":[]},{"option_label":"Sharing of resources to cut down on the amount of equipment needed","option_value":"add-question","questions":[{"question_label":"Bluetooth is an example of?","option_list":[{"option_label":"Personal area network","option_value":"next","questions":[]},{"option_label":"Virtual private network","option_value":"exit","questions":[]}]}]},{"option_label":"Sharing amount of equipment needed?","option_value":"add-question","questions":[{"question_label":"The vast network of computers that connects millions of people all over the world is called?","option_list":[{"option_label":"LAN","option_value":"exit","questions":[]},{"option_label":"Internet","option_value":"add-question","questions":[{"question_label":"To connect networks of similar protocols are used?","option_list":[{"option_label":"Routers","option_value":"exit","questions":[]},{"option_label":"Bridges","option_value":"next","questions":[]}]}]}]}]}]}]}];
    var getQuesListItems = get_pre_requisite_data()
    var newObj = getQuesListItems[0]['template-data'];
    var qurNum ='';
    // var getListingItems = getAllQuestionsListItem(newObj,qurNum);
    // $(".listing_container").append(getListingItems)
    getAllQuestions(newObj)
})




function getOptionAction(value)
{
   
    if(value == "next")
    {
        return "Move to next question"
    }
    else if (value == "exit")
    {
        return "Terminate Prerequisites"
    }
    else
    {
        return "Move to subquestion"
    }
}

function getQuestionDiv(question,question_index,option_number="")
{
    var childListClass = "";
    var question_label = ""
    if(option_number)
    {
        question_label = (question_index)+"."+ option_number
    }
    else
    {
        question_label = (question_index+1)
    }
    var question_div = `<div class="list-column"><div class="question-upper_section"><div class="question"><span class="question-number">`+question_label+`</span><h5 class="question-title h6 text-capitalize">`+question["question_label"]+`</h5></div></div><div class="question-lower_section">`;
    var optionList = question['option_list'];
    $.each(optionList,function(opt_index){
        console.log('child list>>>'+optionList[opt_index]['option_value'])
         if(optionList[opt_index]['option_value'] == 'add-question'){
            childListClass = "subQuestionView";
         }else{
            childListClass = "optionSection";
         }
        question_div += `<div class="fx-option_setion `+childListClass+`">`;
        question_div += `<div class="left-option_tab">
            <input type="radio" value="`+optionList[opt_index]['option_value']+`" name="option-mark" disabled>
            <label class="option-type">`+optionList[opt_index]['option_label']+`</label>
        </div>
        <div class="right-option_tab">
            <lable class="captionOfOptionMark">`+getOptionAction(optionList[opt_index]['option_value'])+`</lable>
        </div>`
        question_div +="</div>"

        if(optionList[opt_index]['questions'].length)
        {

            question_div+=`<div class="sub-que">`
            var sub_que_div = getQuestionDiv(optionList[opt_index]['questions'][0],question_label,option_number=opt_index)
            question_div +=sub_que_div
            question_div+=`</div>`
        }
    })
    // question_div +="</div>"
    question_div += `</div></div>`;
    return question_div
}
function getAllQuestions(getListItem)
{

    //console.log("first values",getListItem)
    var listView=""
    $.each(getListItem,function(que_index){

        listView += getQuestionDiv(getListItem[que_index],que_index)


    })
    $(".listing_container").append(listView)

}
function getAllQuestionsListItem(getListItem,question_no){``
    //Add Ajax request for question Listing
    // console.log('count>>>'+question_no)
    // if(question_no)
    // {
    //     question_no += "."
    // }
    var listView = "";
    $.each(getListItem, function(keyId){

 
    // {
    //     question_no += "."   
    // }
        countQue = keyId + 1;
        // var question_label = ""
  
        // console.log(question_no+'--'+countQue)

        // console.log("question label ",question_label)
        listView += `<div class="list-column"><div class="question-upper_section"><div class="question"><span class="question-number">`+question_no+"."+(keyId+1)+`</span><h5 class="question-title h6 text-capitalize">`+getListItem[keyId]['question_label']+`</h5></div></div><div class="question-lower_section">`;
        var optionList = getListItem[keyId]['option_list'];
        if(optionList.length){
            var newItem = '';
            $.each(optionList, function(optKey){
                listView += `<div class="fx-option_setion">`;
                if(optionList[optKey]['option_value'] == 'next'){
                    listView += `<div class="left-option_tab">
                                    <input type="radio" value="`+optionList[optKey]['option_value']+`" name="option-mark" disabled>
                                    <label class="option-type">`+optionList[optKey]['option_label']+`</label>
                                </div>
                                <div class="right-option_tab">
                                    <lable class="captionOfOptionMark">Move To Next Quetion</lable>
                                </div>`;
                    }else if(optionList[optKey]['option_value'] == 'exit'){
                        listView += `<div class="left-option_tab">
                                    <input type="radio" value="`+optionList[optKey]['option_value']+`" name="option-mark" disabled>
                                    <label class="option-type">`+optionList[optKey]['option_label']+`</label>
                                </div>
                                <div class="right-option_tab">
                                    <lable class="captionOfOptionMark">Termination Prerequisite</lable>
                                </div>`;
                    }else if(optionList[optKey]['option_value'] == 'add-question'){
                        listView += `<div class="left-option_tab">
                                        <input type="radio" value="`+optionList[optKey]['option_value']+`" name="option-mark" checked disabled>
                                        <label class="option-type">`+optionList[optKey]['option_label']+`</label>
                                    </div>
                                    <div class="right-option_tab">
                                        <lable class="captionOfOptionMark">Move to sub question</lable>
                                    </div>
                                    <div class="sub-que">`;

                        console.log("subQuestion",countQue+"."+optKey)
                            if(question_no)
                            {
                                question_label =  question_no
                            }
                            else
                            {
                                question_label = keyId+1
                            }
                        var sublistItem = getAllQuestionsListItem(optionList[optKey]['questions'],question_label);
                        listView += sublistItem;
                        listView += `</div>`;
                    }
                     listView += `</div>`;
                                
            })
        }
        listView += `</div></div>`;
        // countQue ++
    })
    //$(".listing_container").append(listView)
    return listView;
}