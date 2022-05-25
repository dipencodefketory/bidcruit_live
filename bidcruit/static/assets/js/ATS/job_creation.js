/***job_creation.js****/
$(document).ready(function() {
	
	$("#as_per_market").on("click", function(){
		check = $("#as_per_market").is(":checked");
		if(check) {
			$("#salary").addClass('salary');
		} else {
			$("#salary").removeClass('salary');
		}
	});
	tinymce.init({
		selector: '.job-description',
		menubar: false,
		plugins: [
			'advlist autolink lists link image charmap print preview',
			'searchreplace visualblocks code fullscreen',
			'insertdatetime media table paste code '
		],
		onchange_callback: function(editor) {
			tinyMCE.triggerSave();
			$("#" + editor.id).valid();
		},
		toolbar:'size bold italic backcolor underline  | bullist numlist | ' + 'link table insertdatetime charmap preview',
		content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px }',
	});
	tinymce.init({
		selector: '.job-benefit',
		menubar: false,
		handle_event_callback  : "myCustomInitInstance",
		plugins: [
			'advlist autolink lists link image charmap print preview',
			'searchreplace visualblocks code fullscreen',
			'insertdatetime media table paste code '
		],
		toolbar:'size bold italic backcolor underline  | bullist numlist | ' + 'link table insertdatetime charmap preview',
		content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px }',
	});
	tinymce.init({
		selector: '.job-requirement',
		menubar: false,
		plugins: [
			'advlist autolink lists link image charmap print preview',
			'searchreplace visualblocks code fullscreen',
			'insertdatetime media table paste code'
		],
		toolbar:'size bold italic backcolor underline  | bullist numlist | ' + 'link table insertdatetime charmap preview',
		content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px }',
	});
	
	$(".recruiter__selector").on('change',function(e){
		if($(this).val() == 'internal'){
			$('#internal-recruiter-modal').modal('show');
		}
		if($(this).val() == 'external'){
			$('#external-recruiter-modal').modal('show');
		}
	});
	checkEmtyRecruiterList();

});

$(function () {
	//Assign Click event to Button.
	$("#assignErInfo").click(function () { // External
		var externalMsg = "";
		var listKey = "";
		var exernalListObjectItems = [];
		//Loop through all checked CheckBoxes in GridView.
		$(".table-bordered input[type=checkbox]:checked").each(function () {
			var row = $(this).closest("tr")[0];
			externalMsg +="\n"+ row.cells[1].innerHTML;
			externalMsg += "   " + row.cells[2].innerHTML;
			externalMsg += "   " + row.cells[3].innerHTML;
			externalMsg += "  external\n";
		});
		
		$(".table-bordered input[type=checkbox]:checked").each(function () {
			var row = $(this).closest("tr")[0];
			var userId = row.cells[1].innerHTML;
			var userName = row.cells[2].innerHTML;
			var userEmail = row.cells[3].innerHTML;
			var userType = "External";
			exernalListObjectItems.push({"user_id":userId,"user_name":userName,"user_email":userEmail,"user_type":userType})
		});
		console.log(exernalListObjectItems);
		if(exernalListObjectItems.length == "0"){
			$(".fxdExteralValid-msg").html("<span>External Recruiters Selection Required.</span>");
			setTimeout(function(){
				$(".fxdExteralValid-msg").find('span').remove();
			},2500);
		}else{
			listKey = "External";
			assignCloneList(exernalListObjectItems,listKey);
			$(this).closest("#external-recruiter-modal").find("#popUpModelClose").trigger('click');
			return false;
		}
		checkEmtyRecruiterList();
		//assignCloneList(listObjectItems)
		//return false;
	});
                
	$("#assignIrInfo").click(function () { // internal
		var message = "";
		var listKey = "";
		var listObjectItems = [];
		//Loop through all checked CheckBoxes in GridView.
		$(".internal input[type=checkbox]:checked").each(function () {
			var row = $(this).closest("tr")[0];
			message +="\n"+ row.cells[1].innerHTML;
			message += "   " + row.cells[2].innerHTML;
			message += "   " + row.cells[3].innerHTML;
			message += "  internal\n";
		});
		
		$(".internal input[type=checkbox]:checked").each(function () {
			var row = $(this).closest("tr")[0];
			var userId = row.cells[1].innerHTML;
			var userName = row.cells[2].innerHTML;
			var userEmail = row.cells[3].innerHTML;
			var userType = "Internal";
			listObjectItems.push({"user_id":userId,"user_name":userName,"user_email":userEmail,"user_type":userType})
		});

		if(listObjectItems.length == "0"){
			$(".fxdInteralValid-msg").html("<span>Internal Recruiters Selection Required.</span>");
			setTimeout(function(){
				$(".fxdInteralValid-msg").find('span').remove();
			},2500);
		}else{
			listKey = "Internal";
			assignCloneList(listObjectItems,listKey);
			$("#popUpModelClose").trigger('click');
			return false;
		}
		checkEmtyRecruiterList();
	});

	$(document).on('click','.removeAssignList',function(){
		var getUserId = $(this).parent().prev('.col-3').find('input[name=user-id]').val()
		var getUsertype = $(this).parent().prev('.col-3').find('input[name=user-type]').val();
		$(".table-bordered input[type=checkbox]").each(function () {
			console.log((this))
			var getCheckMarkId = $(this).attr('id');
			if(getCheckMarkId === getUserId){
				if($(this).is(":checked")){
					$(this).prop('checked',false)
				}
				console.log(getCheckMarkId,getUserId)
			}
		});
		$(this).closest('.details-section__row').remove()
		checkEmtyRecruiterList();
	})

	$(document).on('click','.remove',function(){
		var getUserId = $(this).data('id');
		var jobid='{{get_job_template.id}}';

		console.log(getUserId)
		console.log($("input[name=csrfmiddlewaretoken]").val());
		$.ajax({
			url:"{% url 'company:unassign_recruiter' %}",
			type:'POST',
			headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val()},
			data:{getUserId:getUserId,job_id:jobid,getUsertype: $(this).parent().prev('.col-3').find('input[name=user-type]').val()}
			})
			.done(function(response){
				if(response=="True"){
					$(this).closest('.details-section__row').remove()
				}

			}).fail(function(){
				console.log("failed");
			})
	})
});

function assignCloneList(listItem,lsKey){
	assignRowList = "";
	if(listItem.length > 0){
		$.each(listItem,function(idx){
			assignRowList += `<div class="row details-section__row">
								<div class="col-3">
									<label class="super-title text-capitalize">`+listItem[idx].user_name+`</label>
									</div>
								<div class="col-3">
									<label class="super-title text-capitalize">`+listItem[idx].user_email+`</label>
								</div>
								<div class="col-3">
									<span class="badge badge-light text-capitalize">`+listItem[idx].user_type+`</span>
									<input type="hidden" value="`+listItem[idx].user_type+`" name="user-type">
									<input type="hidden" value="`+listItem[idx].user_id+`" name="user-id">
								</div>
								<div class="col-3">
									<button type="button" class="removeAssignList btn btn-sm btn-outline-danger rounded-20 text-capitalize">Unassign</button>
								</div>
							</div>`;
		});
		if(lsKey == 'Internal'){
			$("#internalDataListItems").nextAll('.details-section__row').remove();
			$('#internalDataListItems').after(assignRowList);
			$('.recruiter__selector').prop('selectedIndex',0);
			checkEmtyRecruiterList();
			assignRowList = "";
		}
		if(lsKey == 'External'){
			$("#externalDataListItems").nextAll('.details-section__row').remove();
			$('#externalDataListItems').after(assignRowList);
			$('.recruiter__selector').prop('selectedIndex',0);
			checkEmtyRecruiterList();
			assignRowList = "";
		}
		
	}
	// if(listItem.length){
		
	// 	$.each(listItem,function(idx){
	// 		assignRowList += `<div class="row details-section__row">
	// 							<div class="col-3">
	// 								<label class="super-title text-capitalize">`+listItem[idx].user_name+`</label>
	// 								</div>
	// 							<div class="col-3">
	// 								<label class="super-title text-capitalize">`+listItem[idx].user_email+`</label>
	// 							</div>
	// 							<div class="col-3">
	// 								<span class="badge badge-light text-capitalize">`+listItem[idx].user_type+`</span>
	// 								<input type="hidden" value="`+listItem[idx].user_type+`" name="user-type">
	// 								<input type="hidden" value="`+listItem[idx].user_id+`" name="user-id">
	// 							</div>
	// 							<div class="col-3">
	// 								<button type="button" class="removeAssignList btn btn-sm btn-outline-danger rounded-20 text-capitalize">Unassign</button>
	// 							</div>
	// 						</div>`;
	// 	})
	// 	console.log("assignRowList",assignRowList)
	// 	console.log("$('.details-section__row:last-child')",$('.details-section__row:last-child'))
	// 	$('.details-section__row').after(assignRowList);
	// }
	
}

$("#category").change(function (e) {
	$('.template').empty();
	var category=$(this).val();
	if(category!=""){
		$.ajax({
		  url:"/company/get_job_template",
		  type:'POST',
		  headers: {'X-CSRFToken':$("input[name=csrfmiddlewaretoken]").val()},
		  data: JSON.stringify({'category':category})
		 
		})
		.done(function(response){
			response=JSON.parse(response)
			console.log(response.get_job_template)
			if(response.status==true){
				$('.template').append(`<option label="Template Select"></option>`)
				for( template in response.get_job_template){
					console.log(response.get_job_template[template])
					$('.template').append(`<option value="`+response.get_job_template[template].template_id+`">`+response.get_job_template[template].template_name+`</option>`)
				}
			}
			
		}).fail(function(){
			  console.log("failed");
		})
	}
});
$('.professionSkills').select2({
	 placeholder: "Select Skill",
	 ajax:{
		   url:"/company/get_skills",
		   dataType: 'json',
		   processResults: function (data) {
			   return {
				   results: $.map(data, function (item) {
					   return {id: item.id, text: item.name};
				   })
			   };
		   }
	 },
	 tags:true,
	 createTag: function (params) {
		return {
			id: params.term,
			text: params.term,
			newOption: true,
		}
	 },
	templateResult: function (data) {
		var $result = $("<span></span>");
		$result.text(data.text);
		if (data.newOption) {
			$result.append(" <em>(new)</em>");
		}
		return $result;
	},
	minimumInputLength: 1
});
        
$(".template").change(function (e) {
	var category=$('#category').val();
	var template=$(this).val();
		if(category!=""){
			$.ajax({
			  url:"/company/job_creation_select_template",
			  type:'POST',
			  headers:  {'X-CSRFToken':$("input[name=csrfmiddlewaretoken]").val()},
			  data: JSON.stringify({'category':category,'template':template})
			 
			})
			.done(function(response){
				// response=JSON.parse(response)
				if(response.status=true){
					window.location.href=response.url;
				}
				
			}).fail(function(){
				  console.log("failed");
			})
		}
});

function checkEmtyRecruiterList(){
	if($("#internalDataListItems").nextAll().length == 0){
		$(".interListEmptyMsg").html("No Internal Recruiters Selected")
	}else{
		$(".interListEmptyMsg").html("")	
	}
	if($("#externalDataListItems").nextAll().length == 0){
		$(".exterListEmptyMsg").html("No External Recruiters Selected")
	}else{
		$(".exterListEmptyMsg").html("");
	}
}

/****
 * Call Back Tiny Editior Text Limit
 */
 function myCustomInitInstance(e) {
  console.log("event:" + e.type);

}
 function getTinyEditTextCounter(id) {
	console.log('Editor Id',id)
    var body = tinymce.get(id).getBody(), text = tinymce.trim(body.innerText || body.textContent);
	var setTextLimitData = {chars: text.length, words: text.split(/[\w\u2019\'-]+/).length};
	console.log('Editor Data',setTextLimitData)
    // return {
    //     chars: text.length,
    //     words: text.split(/[\w\u2019\'-]+/).length
    // };
}
