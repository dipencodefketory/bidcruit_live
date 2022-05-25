// Additional code for adding placeholder in search box of select2
// (function($) {
//     var Defaults = $.fn.select2.amd.require('select2/defaults');
//     $.extend(Defaults.defaults, {
//         searchInputPlaceholder: ''
//     });
//     var SearchDropdown = $.fn.select2.amd.require('select2/dropdown/search');
//     var _renderSearchDropdown = SearchDropdown.prototype.render;
//     SearchDropdown.prototype.render = function(decorated) {
//         // invoke parent method
//         var $rendered = _renderSearchDropdown.apply(this, Array.prototype.slice.apply(arguments));
//         this.$search.attr('placeholder', this.options.get('searchInputPlaceholder'));
//         return $rendered;
//     };
// })(window.jQuery);
$(function() {
    'use strict'
    // Toggle Switches
    $('.main-toggle').on('click', function() {
        $(this).toggleClass('on');
    })
    // // Input Masks
    // $(document).ready(function() {
    //     $('.select2').select2({
    //         placeholder: 'Choose one',
    //         searchInputPlaceholder: 'Search'
    //     });
    //     $('.select2-no-search').select2({
    //         minimumResultsForSearch: Infinity,
    //         placeholder: 'Choose one'
    //     });
    // });
    $(document).on('change', ':file', function() {
    var input = $(this),
        numFiles = input.get(0).files ? input.get(0).files.length : 1,
        label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
    input.trigger('fileselect', [numFiles, label]);
    });
    // We can watch for our custom `fileselect` event like this
    $(document).ready( function() {
      $(':file').on('fileselect', function(event, numFiles, label) {
          var input = $(this).parents('.input-group').find(':text'),
              log = numFiles > 1 ? numFiles + ' files selected' : label;
          if( input.length ) {
              input.val(log);
          } else {
              if( log );
          }
      });
    });
});


$(function() {
    'use strict'
    // Toggle Switches
    $('.main-toggle').on('click', function() {
        $(this).toggleClass('on');
    })
    // Input Masks

    $(document).on('change', ':file', function() {
    var input = $(this),
        numFiles = input.get(0).files ? input.get(0).files.length : 1,
        label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
    input.trigger('fileselect', [numFiles, label]);
    });
    // We can watch for our custom `fileselect` event like this
    $(document).ready( function() {
      $(':file').on('fileselect', function(event, numFiles, label) {
          var input = $(this).parents('.input-group').find(':text'),
              log = numFiles > 1 ? numFiles + ' files selected' : label;
          if( input.length ) {
              input.val(log);
          } else {
              if( log ) ;
          }
      });
    });
});
