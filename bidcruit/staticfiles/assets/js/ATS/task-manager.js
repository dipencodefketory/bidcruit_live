$(document).ready(function(){
   $('.delete-btn').on('click',function(){
       //ajax requrest
       $(this).closest('.task-list').remove();
   })

//    $(document).on('focus','.txtDate_target_Date',function(){
//     $(this).datepicker({
//         showOtherMonths: true,
//         selectOtherMonths: true,
//         minDate: 0,
//     });
//    })
  

var dtToday = new Date();
var month = dtToday.getMonth() + 1;
var day = dtToday.getDate();
var year = dtToday.getFullYear();
if(month < 10)
    month = '0' + month.toString();
if(day < 10)
    day = '0' + day.toString();
var minDate= year + '-' + month + '-' + day;
$('.txtDate_target_Date').attr('min', minDate);



   $('.edit-btn').on('click',function(){
      var formHtml = "";
      var editFormData = {"title":"asdasdsdasdasd","priority":"low","task_description":"asdasddasddasddsa sd asd asdas dasd","category":"c1","job":"job1","candidate":"candidate1","owner":["asdds","sadasddd"],"assignee":["asasdds","2qssadasddd"],"due_date":"12/04/2022","status":"active"};

      $("#editTaskManager-form").html("");
     


      formHtml += `<div class="col-12 form-group">
                        <label class="form-label">Title:</label>
                        <input type="text" class="form-control" required="" name="edit-title" value="`+editFormData.title+`">
                    </div>

                    <div class="col-12 checkmark-ls form-group">
                        <label class="form-label">Preority:</label>
                        <div class="checkmark-ls req-msg-poz">
                            <div class="check-element">
                                <input type="radio" class="form-control-sm" name="select_preority" required="" checked> 
                                <label class="check-label">Low</label>
                            </div>
                            <div class="check-element">
                                <input type="radio" class="form-control-sm" name="select_preority" required="">
                                <label class="check-label">Medium</label>
                            </div>
                            <div class="check-element">
                                <input type="radio" class="form-control-sm" name="select_preority" required="">
                                <label class="check-label">High</label>
                            </div>
                        </div>
                    </div>

                    <div class="col-12 form-group">
                        <label class="form-label">Task Description:</label>
                        <textarea class="form-control" required="" placeholder="enter the task description...." required="" rows="3">`+editFormData.task_description+`</textarea>
                    </div>

                    <div class="col-12">
                        <div class="row row-sm selector-view mg-t-10">
                            <div class="col-4 select-input form-group valid-third-last">
                                <label class="form-label">Category :</label>
                                <select class="form-control" required="">
                                    <option label="Choose one"></option>
                                    <option value="c-1" selected>Category-1</option>
                                    <option value="c-2">Category-2</option>
                                    <option value="c-3">Category-3</option>
                                    <option value="c-4">Category-4</option>
                                </select>
                            </div>
                            <div class="col-4 select-input form-group valid-third-last">
                                <label class="form-label">Select Job :</label>
                                <select class="form-control" required="">
                                    <option label="Choose one"></option>
                                    <option value="job1" selected>React JS</option>
                                    <option value="job2">Node JS</option>
                                    <option value="job3">Angular</option>
                                    <option value="job4">Php</option>
                                </select>
                            </div>
                            <div class="col-4 select-input form-group valid-third-last">
                                <label class="form-label">Select Candidate :</label>
                                <select class="form-control"  required="">
                                    <option label="Choose one"></option>
                                    <option value="candidate1" selected>Frontend developer</option>
                                    <option value="candidate2">full stack developer</option>
                                    <option value="candidate3">software tester</option>
                                    <option value="candidate4">cyber security</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div class="col-12">
                        <div class="row row-sm mg-t-20 search-selector">
                            <div class="col-6 form-group valid-sec-last">
                                <label class="form-label">Select Owner :</label>
                                <select class="form-control select2 multi-selector" multiple="multiple" required="">
                                    <option value="rishabh">rishabh</option>
                                    <option value="abhinav" selected>abhinav</option>
                                    <option value="sachin">sachin</option>
                                    <option value="keshavdas">keshavdas</option>
                                </select>
                            </div>
                            <div class="col-6 form-group valid-sec-last">
                                <label class="form-label">Assignee :</label>
                                <select class="form-control select2 multi-selector" multiple="multiple" required="">
                                    <option value="rishabh">rishabh</option>
                                    <option value="abhinav">abhinav</option>
                                    <option value="sachin">sachin</option>
                                    <option value="keshavdas" selected>keshavdas</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div class="col-12">
                        <div class="row row-sm mg-t-20 datepicker-selector">
                            <div class="col-6 form-group valid-last">
                                <label class="form-label">Select Due Date :</label>
                                <input class="form-control input-feild txtDate_target_Date" required=""  name="target_date" type="date">
                            </div>
                            <div class="col-6 status-tab form-group valid-last">
                                <label class="form-label">Status :</label>
                                <select class="form-control" required="">
                                    <option label="Choose one"></option>
                                    <option value="status1" selected>Active</option>
                                    <option value="status2">Disable</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div class="col-12 submit-btn mg-t-20">
                        <button class="btn btn-primary" type="submit" name="submit">submit</button>
                    </div>`;
            $("#editTaskManager-form").append(formHtml);
            $('.multi-selector').select2();
            $("#editTaskManager").modal('show');
   })

})
$(window).ready(function(){
    $('.select2').select2({
        tags: true
    });
})