$(document).ready(function(){
    $('.company_logo').dropify({
        messages: {
            'default': 'Click here to upload file',
            'replace': 'Drag and drop or click to replace',
            'remove': 'Remove',
            'error': 'Ooops, something wrong appended.'
        },
        error: {
            'fileSize': 'The file size is too big (2M max).'
        }
    });
})