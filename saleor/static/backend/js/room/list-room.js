/* ------------------------------------------------------------------------------
*
*  # add room js scripts
*
*  Specific JS code additions for G-POS backend pages
*
*  Version: 1.0
*  Latest update: Aug 19, 2017
*
* ---------------------------------------------------------------------------- */
// alertUser
function alertUser(msg,status='bg-success',header='Well done!')
{ $.jGrowl(msg,{header: header,theme: status}); }
//add productDetails
function ajaxSky(dynamicData,url,method){
  dynamicData["csrfmiddlewaretoken"]  = jQuery("[name=csrfmiddlewaretoken]").val();
  return $.ajax({
      url: url,
      type: method,
      data: dynamicData
    });

}

//default data
var dynamicData = {};
var roomId = null;
var roomName = null;

$(function() {
    //  urls
    var pageUrls = $('.pageUrls');
    var bookUrl = pageUrls.data('bookurl')

    // dom selectors
    var bookBtn = $('.book-room-btn');
    var modal = $('#booking-modal');
    var modalContent = modal.find('#form-content');

    bookBtn.on('click',function(){
        roomId = $(this).data('pk');
        roomName = $(this).data('name');
        console.log('I want to book '+roomName);

        /* initialize GET parameters */
        dynamicData = {};
        dynamicData['room_pk'] = roomId;
        dynamicData['room_name'] = roomName;
        dynamicData['track'] = 'loading booking form';

        /* launch modal */
        modal.modal();

        /* block modal content */
        modalContent.block({
            message: '<i class="icon-spinner4 spinner"></i>',
            overlayCSS: {
                backgroundColor: '#fff',
                opacity: 0.8,
                cursor: 'wait'
            },
            css: {
            	width: 16,
                border: 0,
                padding: 0,
                backgroundColor: 'transparent'
            }
        });

        /* remotely fetch form detail */
        ajaxSky(dynamicData,bookUrl,'get')
        .done(function(response){
            modalContent.html(response);
        })
        .fail(function(){
            console.log('failed fetching booking form');
            modalContent.html('Error fetching form');
        });
    });
});