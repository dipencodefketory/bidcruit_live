$(document).ready(async function(){

    var get_stages = await getStages();
	var get_users = await getUsers();
	kindleTextBox(get_stages,get_users);

	async function getWorkflowData(){
        var return_data = await $.ajax({
            url:"/agency/get_workflow_data/",
            headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
            type:'POST',
            contentType: 'application/json; charset=UTF-8',
            error: function (request, status, error) {
            }
        }).done(function(response){
            console.log('response>>>>>',response)
        });
        return return_data
    }

    var data = await getWorkflowData();

    var stageList = data['stages_data'];
    var categoryList = data['category_data'];
    var tempList = data['template_data'];

    stageListPopulate(stageList);

    $('#stageSelectorList').on('change',function(){ //stage selector event
        var getStageId = $(this).find('option:selected').val();
        if(getStageId !== ''){
            var cateListData = {'id':getStageId,'data':categoryList};
            cateListPopulate(cateListData);
            $('#templateSelectorList option').remove();
            $('#templateSelectorList').append(`<option label="Select Template"></option>`);
            $('#templateSelectorList').attr('disabled','');
        }else{
            $('#categorySelectorList option,#templateSelectorList option').remove();
            $('#categorySelectorList,#templateSelectorList').attr('disabled','');
            $('#categorySelectorList').append(`<option label="Select Category"></option>`);
            $('#templateSelectorList').append(`<option label="Select Template"></option>`);
        }
    })

    $('#categorySelectorList').on('change',function(){ //category selector event
        var getCatId = $(this).find('option:selected').val();
        if(getCatId !== ''){
            var templistData = {'id':getCatId,'data':tempList}
            tempListPopulate(templistData);
        }else{
            $('#templateSelectorList option').remove();
            $('#templateSelectorList').append(`<option label="Select Template"></option>`);
            $('#templateSelectorList').attr('disabled','')
        }
    })

$("#interviewerList").select2({
    closeOnSelect : false,
    placeholder : "Placeholder"
    // allowHtml: true,
    // allowClear: true,
    // tags: true
});

async function getStages(){
    let job_id = $('.job_id').val();
    var return_data = await $.ajax({
        url:"/agency/get_job_stages/",
        type:'GET',
        data: {'job_id':job_id},
        error: function (request, status, error) {
			alert(error);
		}
    }).done(function(response){
            console.log('parse stages >>>>>>>>', JSON.parse(response))
    })
    return return_data
}
async function getUsers(){
    let job_id = $('.job_id').val();
    var return_data = await $.ajax({
        url:"/agency/get_job_users/",
        type:'GET',
        data: {'job_id':job_id},
        error: function (request, status, error) {
			alert(error);
		}
    }).done(function(response){
            console.log('parse users >>>>>>>>', response)
    })
    return return_data
}
var	dbConnection = false;
	$(document).on('click','.colapse-btn',function() {
		if($(this).hasClass('active')){
			$(this).removeClass('active')   
			$(this).closest('.collpase-container').find('.colapse-content').slideUp();
		}else{
			$(this).addClass('active')
			$(this).closest('.collpase-container').find('.colapse-content').slideDown()
		}
	})
	$(document).on('click','.colapse-btn__component',function() {
		if($(this).hasClass('active')){
			$(this).removeClass('active');
			$(this).find('.plus-icon').hide();
			$(this).find('.minus-icon').show();
			$(this).closest('.child-list_details').find('.detail-info__content').slideUp();
		}else{
			$(this).addClass('active')
			$(this).find('.plus-icon').show();
			$(this).find('.minus-icon').hide();
			$(this).closest('.child-list_details').find('.detail-info__content').slideDown();
		}
	})

	$('.attach-btn').on('click',function(){ //collabprate attach-btn action
		$('.uploadDocs').trigger('click')
	})

	$('.send-btn').on('click',function(){ //collabprate send msg action
		var showMsg = "";
		var msg = $('.chat-msgbox').val();
		var file = $('.uploadDocs').val();
		var getSampleMsg = $(document).find('#hiddenTextMsgBox').val()

		if(getSampleMsg !== "" || file !== ""){
		    var collabChatForm = document.getElementById("collabChatForm");
            var formData = new FormData(collabChatForm);
            formData.append('comment_html',showMsg);
            formData.append('candidate_id',$('.candidate_id').val());
            formData.append('job_id',$('.job_id').val());
            $.ajax({
                    url:"/agency/collaboration/",
                    headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                    type:'POST',
                    contentType: false,
                    processData: false,
                    data: formData
            }).done(function(response){
               console.log('response >>>>>>',JSON.parse(response))
               response_data = JSON.parse(response);
               if(response_data.attachment){
                    result = file.split('\\');
			        var fileName = result[result.length - 1];
                    showMsg += `<div class="col-12 fxc-chatview__Section">
							<div class="fxc-right fx-col-block">
							<div class="post-status">
								<label class="text-capitalize">`+response_data.user+`</label>
								<label class="text-capitalize">`+response_data.time+`</label>
							</div>
							<div class="post-details">
								<div class="file-view"><a target="_blank" href="`+response_data.attachment+`">`+fileName+`</a></div>`;
								if(getSampleMsg !== ''){
									showMsg +=	`<div class="msg-view pd-10"><p>`+response_data.comment+`</p></div>`
								}else{
									showMsg +=	`<div class="msg-view pd-10" style="display:none"><p>`+response_data.comment+`</p></div>`
								}
                    showMsg += `</div></div>`;
               }else{
                    showMsg += `<div class="col-12 fxc-chatview__Section">
							<div class="fxc-right fx-col-block">
                                <div class="post-status">
                                    <label class="text-capitalize">`+response_data.user+`</label>
                                    <label class="text-capitalize">`+response_data.time+`</label>
                                </div>
                                <div class="post-details">
                                    <div class="msg-view pd-10">
                                        <p>`+response_data.comment+`</p>
                                    </div>
                                </div>
							</div>
                    </div>`
               }
                $(document).find('.mentions-kinder-singleline.chat-msgbox').trigger('keypress')
                $('.chatconunter-container .fxc-chatbox__Section').before(showMsg);
                $('.chat-msgbox,.uploadDocs').val('');
                $('.chat-msgbox').empty();
            })
		}else{
			$('.mentions-kinder-singleline').css('border-color','#ff0000')
			setTimeout(function(){
				$('.mentions-kinder-singleline').css('border-color','#e2e8f5')
			},1500)
		}
	})
	
	$('.slideClose').on('click', function(){ //slide close btn event
		  
	    var mainLayoutVisible = $('.acv-main-continer');
		var slideContainerWidth = $('.side-barContainer').width();
		if(mainLayoutVisible.hasClass('actPanel')){
			mainLayoutVisible.removeClass('actPanel')
			mainLayoutVisible.find('.side-barContainer').css('right', '-'+slideContainerWidth+'px')
		}else{
			mainLayoutVisible.addClass('actPanel')
			mainLayoutVisible.find('.side-barContainer').css('right','0px')
		}

		var data_key = $('.side_bar_panal_view').data('info');
		console.log(data_key);
		$('.side_bar_panal_view').removeClass(data_key);
		$('.side_bar_panal_view').css('display','none');
		$('.side_bar_panal_view').removeAttr('data-info');
		$('.side_bar_panal_view').removeData('info')
	});

//	$('.show-details-btn').on('click',function(){
//		//ajax request
//		var flag = true;
//
//		if(flag == true){
//			$(this).closest('.category__list').hide()
//			$(this).closest('.category__list').next().css('display','flex')
//		}
//	})

	/**quick view slider**/
	$(document).on('click','.view-btn',function(){
		var getListId = $(this).data('item');
		console.log("=============",getListId)
		quickSlideView(getListId);
	})

	$(document).on('click','.sidebar-preview',function(e){ //sidebar container slider
		slidePreviewPanel();
		/*var container = $(".side-barContainer");
		if (!container.is(e.target) && container.has(e.target).length === 0) 
		{
			$('.sidebar-preview').css({'width':'0%','visibility':'hidden'});
        	$('.slideClose').addClass('inside');
		}*/
	});
	
	// $('.upload-input-file').each(function() { //file upload function
	// 	var dirPathName = $('#path-input').val();
	// 	dirPathName = dirPathName.split('/');
	// 	console.log('aaaa>>>'+dirPathName[1])
	// 	var $input = $(this),
	// 		$label = $input.next('.js-labelFile'),
	// 		labelVal = $label.html();
	// 	$input.on('change', function(element) {
	// 		    var setFileItems = '';
	// 			var filePathUrl = element.target.value;
	// 			var fileName = filePathUrl.split('\\').pop();
	// 			var checkFileExt = fileName.split('.');
	// 		/*if (element.target.value) fileName = element.target.value.split('\\').pop();
	// 			fileName ? $label.addClass('has-file').find('.js-fileName').html(fileName) : $label.removeClass('has-file').html(labelVal);
	// 			$('.fmuf-fullpath').attr('data-path',element.target.value);*/

	// 			if(
	// 				checkFileExt[1] == 'pdf' || checkFileExt[1] == 'docx' || checkFileExt[1] == 'doc' || checkFileExt[1] == 'jpg' || checkFileExt[1] == 'png' || checkFileExt[1] == 'jpeg' ||checkFileExt[1] == 'mp4' || checkFileExt[1] == 'mp3' || checkFileExt[1] == 'webm' || checkFileExt[1] == 'mpeg'
	// 			  ){
	// 				setFileItems = {'dir-name':dirPathName[1],'file-name':fileName,'file-path':filePathUrl};
	// 				fileUpload(setFileItems)
	// 			  }else{
	// 				alert('sorry! this file is not a document.')
	// 			  }
	// 	});

	// });


	$(document).on('change','.upload-input-file',function(element) {
		var dirPathName = $('#path-input').val();
		dirPathName = dirPathName.split('/');
		console.log('aaaa>>>'+dirPathName[1])
		var form = document.getElementById('fileUploader')
		let formData = new FormData(form);
		console.log('formData >>>>>>>>>>>',formData)
		var setFileItems = '';
		var filePathUrl = element.target.value;
		var fileName = filePathUrl.split('\\').pop();
		var checkFileExt = fileName.split('.');
		if(
			checkFileExt[1] == 'pdf' || checkFileExt[1] == 'docx' || checkFileExt[1] == 'doc' || checkFileExt[1] == 'jpg' || checkFileExt[1] == 'png' || checkFileExt[1] == 'jpeg' ||checkFileExt[1] == 'mp4' || checkFileExt[1] == 'mp3' || checkFileExt[1] == 'webm' || checkFileExt[1] == 'mpeg'
		  ){
			setFileItems = {'dir-name':dirPathName[1],'file-name':fileName,'file-path':filePathUrl,'formData':formData};
			fileUpload(setFileItems)
		  }else{
			alert('sorry! this file is not a document.')
		  }
	});


	$('#browsefile-container').on('mouseenter',function(){ //handle upload button action on root dir
		var curretnFileLocation = $('#path-input').val();
		var getPathName = curretnFileLocation.split('/');
		console.log(getPathName)
		if(getPathName[1] !== undefined){
			$(this).find('.upload-input-file').removeAttr('disabled')
		}else{
			$(this).find('.upload-input-file').attr('disabled','disabled')
		}
	})

	$('#btn-upload-file').click(()=>{//file upload trigger function
		var curretnFileLocation = $('#path-input').val();
		var getPathName = curretnFileLocation.split('/');

		/*if(getPathName[1] !== undefined){
			console.log(getPathName[1])
		    $('.upload-input-file').trigger('click');
			$('#browsefile-container').on('change',function(){
				var filePathUrl = $(this).find('.fmuf-fullpath').data('path');
				var fileName = filePathUrl.split('\\').pop();
				var checkFileExt = fileName.split('.');
				console.log(checkFileExt[1])
				if(
					checkFileExt[1] == 'pdf' || checkFileExt[1] == 'docx' || checkFileExt[1] == 'doc' || checkFileExt[1] == 'jpg' || checkFileExt[1] == 'png' || checkFileExt[1] == 'jpeg' ||checkFileExt[1] == 'mp4' || checkFileExt[1] == 'mp3' || checkFileExt[1] == 'webm' || checkFileExt[1] == 'mpeg'
				  ){
					var setFileItems = {'dir-name':getPathName[1],'file-name':fileName,'file-path':filePathUrl};
					fileUpload(setFileItems)
				  }else{
					alert('sorry! this file is not a document.')
				  }
			})
		}else{
			console.log(getPathName[1])	
		}*/

	});

	var domEleOfFile = '';
	$(document).on('click','.editFile',function(){ //edit file event 
		domEleOfFile = $(this).closest('.file');
		var getFileName = $(this).closest('.file').find('.file-type').text();
		var filterEditFileName = getFileName.split('.');
		$('#editFileModelView').find('.editFileInputBox').val(filterEditFileName[0])
		$('#editFileModelView').find('.orgFileName').val(getFileName)
		$('#editFileModelView').modal();
	})

	$(document).on('click','.deleteFile',function(){ //delete file event 
		// domEleOfFile = $(this).closest('.file');
		$(this).closest('.file').attr('data-delete','selected');
		var EleOfFile = $(this).closest('.file').find('.file-type').text();
		 console.log('remove file>>'+EleOfFile)
		// var filterEditFileName = getFileName.split('.');
		// $('#editFileModelView').find('.editFileInputBox').val(filterEditFileName[0])
		// $('#editFileModelView').find('.orgFileName').val(getFileName)
		$('#deleteFileModelView').find('.delete-msg-text').attr('data-fileremove',EleOfFile)
		$('#deleteFileModelView').modal();
	})

	$('.editFileSaveAction').on('click',function(){ //edit file modal
		var editFileInput = $('.editFileInputBox').val();
		if(editFileInput !== ''){
			//save file via ajax request
			console.log(domEleOfFile)
			var newEditFileName = $('#editFileModelView').find('.editFileInputBox').val();
			var oldFileName = $('#editFileModelView').find('.orgFileName').val();
			var getExtOfFile = oldFileName.split('.')
			var replaceName = newEditFileName+'.'+getExtOfFile[1]
			console.log(oldFileName+'---'+replaceName)
			domEleOfFile.find('.file-type').text(replaceName)
			setTimeout(function(){
				$('#editFileModelView .close').trigger('click')
			},1100)
		}else{
			/*$('.editFileInputBox').css('border-color','#ff0000')
			setTimeout(function(){
				$('.editFileInputBox').css('boder-color','#e2e8f5')
			},250)*/
		}
	})

	/**mcq comment form submit**/
	$('#cmt-submit').on('click',function(){
		var getTitle = $('input[name=cmt-title]').val();
		var ratingVal = $('.rating-point').find('#rating-stars-value').val();
		var cmtTextMsg = $('.commentTextMsg').val();
		var cmtHtml = '';
		
		if(getTitle !== '' && cmtTextMsg !== ''){
			cmtHtml += `<div class="colapse-content show">
							<div class="child-list_details">
							<div class="detail-head__colapser">
							<label class="h6 colpase-info-title">`+getTitle+`</label>
							<div class="fx-right__component">
								<label class="rate-text">(`+ratingVal+`.0)</label>
								<div class="rate-icon">`;
					for(let step = 1; step < 6; step++) {
						if(step <= ratingVal){
							cmtHtml +=`<i class="fa fa-star active"></i>`;
						}else{
							cmtHtml +=`<i class="fa fa-star"></i>`;
						}	
					}
				cmtHtml +=	`</div>
								<div class="colapse-btn__component">
									<div class="plus-icon" style="display: none;"><i class="fa fa-chevron-circle-down"></i></div>
									<div class="minus-icon" style="display: block;"><i class="fa fa-chevron-circle-up"></i></div>
								</div>
							</div>
							</div>
							<div class="detail-info__content" style="display: none;">
							<p>`+cmtTextMsg+`</p>
							</div>
						</div>
					</div>`;
			$('.mcqCommentPreview .colapse-content.show:last-child').after(cmtHtml);
			$('.slideClose').trigger('click');
			$('.mcqTestCmtForm').trigger("reset");
		}
	})


	$(".stage-ls li").on('click',function() { // filter button action by stages
		$(this).toggleClass('activeFilterAction');
		var activefilterList = collectionOfFilterList()
		// $('.fxc-chatview__Section').css('display','none');
		// if($('.stage-ls .activeFilterAction').length == '0'){
		// 	$('.fxc-chatview__Section').css('display','block');
		// }else{
		// 	$(".stage-ls li").each(function(){
		// 		if($(this).hasClass('activeFilterAction')){
		// 			var getTagKey = $(this).find('label').data('tagid');
		// 			//filterChatByTags(getTagKey);
		// 		}
		// 	})
		// }
		
		filterChatByTags(activefilterList);
	})

	$(".user-ls li").on('click',function() { // filter button action by user
		$(this).toggleClass('activeFilterAction');
		var activefilterList = collectionOfFilterList();
		// $('.fxc-chatview__Section').css('display','none');
		// if($('.user-ls .activeFilterAction').length == '0'){
		// 	$('.fxc-chatview__Section').css('display','block');
		// }else{
		// 	$(".user-ls li").each(function(){
		// 		if($(this).hasClass('activeFilterAction')){
		// 			var getUserKey = $(this).find('label').data('userid');
		// 			 filterChatByTags(getUserKey);
		// 		}
		// 	})
		// }
		filterChatByTags(activefilterList);
	})

	$('.resetChatBtn').on('click',function(){ //reset chat list
		$('.stage-ls li').removeClass('activeFilterAction');
		$('.user-ls li').removeClass('activeFilterAction');
		$('.fxc-chatview__Section').css('display','block');
	})

})



/***function list****/


function stageListPopulate(getStageList){
    optHtml = '';
    if(getStageList.length){
        $.each(getStageList, function(i){
            optHtml += `<option class="text-capitalize" value="`+getStageList[i].key+`">`+getStageList[i].stage_name+`</option>`;
        })
        $('#stageSelectorList').append(optHtml);
    }
}


function cateListPopulate(getListingItems){
    var optCateHtml = '';
    var getSelectedStageId = getListingItems.id;
    var getCateItemList = getListingItems.data;
    if(getCateItemList.length){
        $('#categorySelectorList option').remove()
        $.each(getCateItemList,function(cKey){
            if(getCateItemList[cKey].stageKey == getSelectedStageId){
                var cateDataItems  = getCateItemList[cKey].cate_list;
                if(cateDataItems.length){
                    optCateHtml +=`<option label="Select Category"></option>`;
                    $.each(cateDataItems,function(keyId){
                        optCateHtml += `<option value="`+cateDataItems[keyId].key+`">`+cateDataItems[keyId].cate_name+`</option>`;
                    })
                }
                $('#categorySelectorList').append(optCateHtml);
            }
        })
        $('#categorySelectorList').removeAttr('disabled')
    }
}

function tempListPopulate(getTempListItems){
    var optCateHtml = '';
    var getSelectedCateId = getTempListItems.id;
    var getTempItemList = getTempListItems.data;
    //console.log(getSelectedCateId)
    //console.log(getTempItemList)
    if(getTempItemList.length){
        $('#templateSelectorList option').remove()
        $.each(getTempItemList,function(cKey){
            if(getTempItemList[cKey].cateKey == getSelectedCateId){
                var tempDataItems  = getTempItemList[cKey].temp_list;
                if(tempDataItems.length){
                    optCateHtml +=`<option label="Select Template"></option>`;
                    $.each(tempDataItems,function(keyId){
                        optCateHtml += `<option value="`+tempDataItems[keyId].key+`">`+tempDataItems[keyId].temp_name+`</option>`;
                    })
                }
                $('#templateSelectorList').append(optCateHtml);
            }
        })
        $('#templateSelectorList').removeAttr('disabled')
    }
}

function fileUpload(getFileDetails){ //Ajax update edited file
	console.log(getFileDetails)
}

function slidePreviewPanel(){
		var mainLayoutVisible = $('.acv-main-continer');
		var slideContainerWidth = $('.side-barContainer').width();
		if(mainLayoutVisible.hasClass('actPanel')){
			mainLayoutVisible.removeClass('actPanel')
			mainLayoutVisible.find('.side-barContainer').css('right', '-'+slideContainerWidth+'px')
		}else{
			mainLayoutVisible.addClass('actPanel')
			mainLayoutVisible.find('.side-barContainer').css('right','0px')
		}
		
}

function collectionOfFilterList(){
	var fatchAllFilterItems = []
	var userActiveList = [];
	var tagActiveList = [];
	$(".user-ls li").each(function(){
		if($(this).hasClass('activeFilterAction')){
			var getUserKey = $(this).find('label').data('userid');
			userActiveList.push(getUserKey)
		}
	})
	$(".stage-ls li").each(function(){
		if($(this).hasClass('activeFilterAction')){
			var getTagKey = $(this).find('label').data('tagid');
			tagActiveList.push(getTagKey)
		}
	})
	var fatchAllFilterItems = $.merge( $.merge( [], userActiveList ), tagActiveList );
	return fatchAllFilterItems;
	
}

function filterChatByTags(filterListQueue){ //all chat list fiter by tag & user name
	 console.log(filterListQueue)
	$('.chatconunter-container .fxc-chatview__Section').each(function(i) { 
		var flag = true
		var currentMessage = $(this)
		// $(this).find('.msg-view p .ckinda-item').each(function(){
		// 	if($(this).data('key') == getTahKey){
		// 		$(this).closest('.fxc-chatview__Section').css('display','block');
		// 	}
		// })
		$.each(filterListQueue,function(j){
		var tag = filterListQueue[j];
		console.log(currentMessage.find('[data-key="'+tag+'"]').length)
		if (currentMessage.find('[data-key="'+tag+'"]').length == 0)
		{ flag =false }
		})
		if(flag == true)
		{ currentMessage.css('display','block'); } else { currentMessage.css('display','none'); }
	})
	// $('.chatconunter-container .fxc-chatview__Section').each(function() {
	// 	$(this).find('.msg-view p .ckinda-item').each(function(){
	// 		if($(this).data('key') == getTahKey){
	// 			$(this).closest('.fxc-chatview__Section').css('display','block');
	// 		}
	// 	})
	// })
}



function deleteSelectedFile(){ //Ajax for delete file
	$(this).remove();
}

function quickSlideView(slideKey){
	
	$(".tb-slider-container").each(function(){
		if($(this).data('preview') == slideKey){
		    $(this).css('display','block');
			$('.side_bar_panal_view').css('display','block');
			$('.side_bar_panal_view').attr("data-info",slideKey);
            console.log($(this).data('preview'));
            console.log(slideKey);
//			$(this).show();

		}else{
			$(this).hide();
		}
	})
	//$('.slideClose').removeClass('inside');
	
	slidePreviewPanel();

	// $('.sidebar-preview').css({
	// 	'width': '100%',
	// 	'visibility': 'visible'
	// });
}


/**kindle plugin***/
function kindleTextBox(stages,users){
    var stages = JSON.parse(stages);
	var users =  JSON.parse(users);
	// configure autocompleter
    var simpsonAutocompleter = $.MentionsKinder.Autocompleter.Select2Autocompleter.extend({
        select2Options: {
            data: users
        }
    });
    console.log('stages in auto',stages)
	var simpsonAutocompleter1 = $.MentionsKinder.Autocompleter.Select2Autocompleter.extend({
        select2Options: {
            data: stages
        }
    });


    // if no options are provided, use @ with simpsonsAutocompleter only
    $.MentionsKinder.defaultOptions.trigger['@'].autocompleter = simpsonAutocompleter;
//    $.MentionsKinder.triggerDefaultOptions.autocompleter = $.MentionsKinder.Autocompleter.DummyAutocompleter;

    simple = $('.simple').mentionsKinder().enableMyDebug().data('mentionsKinder');
    $('.tags').mentionsKinder({
        trigger: {
            '#': {
                triggerName: 'tag',
                autocompleter: simpsonAutocompleter1
            }
        }
    }).enableMyDebug();
    $('.chat-msgbox').mentionsKinder({
        trigger: {
            '#': {
                triggerName: 'tag',
                autocompleter: simpsonAutocompleter1
            },
            '@': {
                triggerName: 'user',
                autocompleter: simpsonAutocompleter
            }
        }
    }).enableMyDebug();

    // bind "change" event
    $('#event_test').on('change', function(event) { $('#event_timestamp').text(new Date) });


    $(document.body).on('click', '[data-action=set-flag]', function(e){
        var $button = $(e.currentTarget),
            $target = $($button.data('target')),
            flag = $button.text(),
            regex = /(?:^|\s+)!(\w+)/i,
            val = $target.val();
        if(val.match(regex))
            val = val.replace(regex, ' ' + flag);
        else
            val = val + ' ' + flag;
        $target.val(val).change()
    });
}

