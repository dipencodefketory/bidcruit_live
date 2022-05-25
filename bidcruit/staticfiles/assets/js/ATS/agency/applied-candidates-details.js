$(document).ready(function(){

	kindleTextBox();

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
		var formData = $('#collabChatForm').serializeArray();
		var getSampleMsg = $(document).find('#hiddenTextMsgBox').val()
		if(file){
			result = file.split('\\');
			var fileName = result[result.length - 1];

			showMsg += `<div class="col-12 fxc-chatview__Section">
							<div class="fxc-left fx-col-block">
							<div class="chat-filterbytag prq-color">
								<label class="text-capitalize">#prerequisites</label>
							</div>
							</div>
							<div class="fxc-right fx-col-block">
							<div class="post-status">
								<label class="text-capitalize">jone lare (hr department)</label>
								<label class="text-capitalize">09:48 PM</label>
							</div>
							<div class="post-details">
								<div class="file-view"><a href="`+file+`">`+fileName+`</a></div>`;
								if(getSampleMsg !== ''){
									showMsg +=	`<div class="msg-view pd-10"><p>`+getSampleMsg+`</p></div>`
								}else{
									showMsg +=	`<div class="msg-view pd-10" style="display:none"><p>`+getSampleMsg+`</p></div>`
								}
								
								showMsg += `</div></div></div>`;
		}else{
			showMsg += `<div class="col-12 fxc-chatview__Section">
							<div class="fxc-left fx-col-block">
							<div class="chat-filterbytag prq-color">
								<label class="text-capitalize">#prerequisites</label>
							</div>
							</div>
							<div class="fxc-right fx-col-block">
							<div class="post-status">
								<label class="text-capitalize">jone lare (hr department)</label>
								<label class="text-capitalize">09:48 PM</label>
							</div>
							<div class="post-details">
								<div class="msg-view pd-10">
									<p>`+getSampleMsg+`</p>
								</div>
							</div>
							</div>
						</div>`
		}
		console.log(getSampleMsg,file)
		if(getSampleMsg !== "" || file !== ""){
			$(document).find('.mentions-kinder-singleline.chat-msgbox').trigger('keypress')
			$('.chatconunter-container .fxc-chatbox__Section').before(showMsg);
			$('.chat-msgbox,.uploadDocs').val('');
			$('.chat-msgbox').empty();
		}else{
			$('.mentions-kinder-singleline').css('border-color','#ff0000')
			setTimeout(function(){
				$('.mentions-kinder-singleline').css('border-color','#e2e8f5')
			},1500)
		}
	})
	
	$('.slideClose').on('click', function(){ //slide close btn event
		slidePreviewPanel();
	});

	$('.show-details-btn').on('click',function(){
		//ajax request
		var flag = true;

		if(flag == true){
			$(this).closest('.category__list').hide()
			$(this).closest('.category__list').next().css('display','flex')
		}
	})

	/**quick view slider**/
	$(document).on('click','.view-btn',function(){
		var getListId = $(this).data('item');
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
		$('.fxc-chatview__Section').css('display','block');
	})

})



/***function list****/



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
			$(this).show()
		}else{
			$(this).hide()
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
function kindleTextBox(){
	// configure autocompleter
    var simpsonAutocompleter = $.MentionsKinder.Autocompleter.Select2Autocompleter.extend({
        select2Options: {
            data: [
                {id:'101',text:'Rajdeep'},
                {id:'102',text:'Robert'},
                {id:'103',text:'Michael'},
                {id:'104',text:'William'},
                {id:'105',text:'Richard'}
            ]
        }
    });
	var simpsonAutocompleter1 = $.MentionsKinder.Autocompleter.Select2Autocompleter.extend({
        select2Options: {
            data: [
                {id:'11',text:'JCR'},
                {id:'12',text:'Prerequisites'},
                {id:'13',text:'MCQ Test'},
                {id:'14',text:'Paragraph MCQ Test'},
                {id:'15',text:'Image Based Test'},
				{id:'16',text:'Descriptive Test'},
				{id:'17',text:'Interview'}
            ]
        }
    });

    // var tagAutocompleter = $.MentionsKinder.Autocompleter.Select2Autocompleter.extend({
    //     select2Options: {
    //         tags: ["JCR", "Prerequisites", "MCQ Test","Paragraph MCQ Test","Image Based Test","Descriptive Test","Interview"]
    //     }
    // });

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

