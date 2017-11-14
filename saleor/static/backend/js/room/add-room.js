/* ------------------------------------------------------------------------------
*
*  # addproduct js scripts
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
function addRoomDetails(dynamicData,url,method){
  dynamicData["csrfmiddlewaretoken"]  = jQuery("[name=csrfmiddlewaretoken]").val();
  return $.ajax({
      url: url,
      type: method,
      data: dynamicData
    });

}
var dynamicData = {};

$(function() {
    //  urls
    var pageUrls = $('.pageUrls');
    var roomUrl = pageUrls.data('roomdata');
    var getAmentiesurl = pageUrls.data('amenitiesurl');
    var addAmenitiesUrl = pageUrls.data('addamenitiesurl');
    var roomListUrl = pageUrls.data('roomurl');

    // refresh dom elements
    var newAmenitiesDiv = $('#add_new_amenities');
    var addNewAmBtn = $('#add_new_amenities_btn');

    // delete room
    var deleteBtn = $('#delete');
    var confirmDeleteBtn = $('#confirm-delete');

    // form data
    var name = $('#name');
    var roomId = $('#room_id');
    var description = $('#description');
    var price  = $('#price');
    var addRoomBtn = $('#add-room-btn');
    var amenities = $('.amenities');
    var new_amenities = $('.new_amenities');
    var new_amenities_btn = $('#new_amenities_btn');

    // handle deleting a room
    deleteBtn.on('click',function(e){
        $(this).nextAll('.confirm-delete:first').html('sdfe').toggle('slow');
    });



    //  toggle new amenities division
    addNewAmBtn.on('click',function(){
        newAmenitiesDiv.toggle('slow');
    });

    //    add list of new amenities
    new_amenities_btn.on('click',function(){
        if(!new_amenities.val())
        {
            new_amenities.nextAll('.help-block:first').addClass('text-warning').html('Please Hit <span class="label label-warning">Enter</span> Key. This field is required.');
            return false;
        }
        dynamicData = {};
        dynamicData['track'] = 'add amenities';
        dynamicData['amenities'] = JSON.stringify(new_amenities.val());

        addRoomDetails(dynamicData, addAmenitiesUrl, 'POST')
        .done(function(data){
            // clear select field
            alertUser('Amenities added successfully');
            newAmenitiesDiv.toggle('slow');
            new_amenities.parents('div').find('li.token').remove();
            new_amenities.val('');
        })
        .fail(function(error){
            console.log(error);
        });

    });

    //    ./new amenities

    //    remove help block
    name.on('focusin',function(){
          $(this).nextAll('.help-block:first').html('');
    });
    price.on('focusin',function(){
          $(this).nextAll('.help-block:first').html('');
    });
    amenities.on('focusin',function(){
          $(this).nextAll('.help-block:first').html('');
    });
    new_amenities.on('focusin',function(){
          $(this).nextAll('.help-block:first').html('');
    });

    addRoomBtn.on('click',function(){
        dynamicData = {}; //clear dynamic data
        //    validation
        if(!name.val()){
            name.nextAll('.help-block:first').addClass('text-warning').html('This field is required');
            return false;
        }
        if(description.val()){
            dynamicData['description'] = description.val();
        }
        if(roomId.val()){
            dynamicData['pk'] = roomId.val();
        }
        if(!price.val()){
            price.nextAll('.help-block:first').addClass('text-warning').html('This field is required. Please enter a number');
            return false;
        }
        if(!amenities.val())
        {
            amenities.nextAll('.help-block:first').addClass('text-warning').html('This field is required');
            return false;
        }

        // add dynamic post data
        dynamicData['name'] = name.val();
        dynamicData['price'] = price.val();
        dynamicData['track'] = 'add room';
        dynamicData['amenities'] = JSON.stringify(amenities.val());

        // post form data
        addRoomDetails(dynamicData,roomUrl,'post')
        .done(function(data){
            console.log(data);
            amenities.parents('div').find('li.token').remove();
            amenities.val('');
            window.location.href = roomListUrl;
        })
        .fail(function(error){
            console.log('error');
        });
    });

     //    take care of tokenized select field

      amenities.on('tokenize:select', function(container){
      $(this).tokenize2().trigger('tokenize:search', [$(this).tokenize2().input.val()]);
       });
      // get amenities
      amenities.tokenize2({
        placeholder: 'Select Amenities(s)',
        displayNoResultsMessage:true,
        //searchMinLength:3,
        sortable: true,
        dataSource: function(search, object){
            $.ajax(getAmentiesurl, {
                data: { search: search, start: 1, group:'users' },
                dataType: 'json',
                success: function(data){
                    var $items = [];
                    $.each(data, function(k, v){
                        $items.push(v);
                    });
                    object.trigger('tokenize:dropdown:fill', [$items]);
                }
            });
        }
    });

    //    create new amenities
     new_amenities.tokenize2({
        placeholder: 'Add Amenities(s)',
        tokensAllowCustom: true
        });
    //./tokenize


});