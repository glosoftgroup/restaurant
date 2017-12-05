/* ------------------------------------------------------------------------------
*
*  # book room js scripts
*
*  Specific JS code additions for G-POS backend pages
*
*  Version: 1.0
*  Latest update: Nov 30, 2017
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


/* global variables */
var dynamicData = {};
var today = moment().format('YYYY-MM-DD HH:mm:ss');
var tomorrow = moment().add(1, 'days').format('YYYY-MM-DD HH:mm:ss');

$(function() {
    //  urls
    var pageUrls = $('.pageUrls');
    var roomUrl = pageUrls.data('roomdata');
    var getRoomsUrl = pageUrls.data('getroomsurl');
    var getCustomerUrl = pageUrls.data('getcustomerurl');
    var roomListUrl = pageUrls.data('bookingurl');
    var computeTotalPriceUrl = pageUrls.data('computetotal');
    var createBookingUrl = pageUrls.data('instancedata');

    // refresh dom elements
    var newAmenitiesDiv = $('#add_new_amenities');
    var addNewAmBtn = $('#add_new_amenities_btn');
    var boolRedirect = $('#redirect');

    // delete room
    var deleteBtn = $('#delete');
    var confirmDeleteBtn = $('#confirm-delete');

    // form data
    var bookingForm = $('#create-booking-form');
    var name = bookingForm.find('#name');
    var roomId = bookingForm.find('#room_id');
    var description = bookingForm.find('#description');
    var price  = bookingForm.find('#price');
    var priceType = bookingForm.find('#price_type');
    var totalPrice = bookingForm.find('#total_price');
    var addRoomBtn = bookingForm.find('#add-room-btn');
    var rooms = bookingForm.find('.rooms');
    var room  = bookingForm.find('#room');
    var customer = bookingForm.find('.customer');
    var daysId = bookingForm.find('#days');
    var stayDays = 0;
    var totalCost = 0;
    var pk = 0;
    var customerName = bookingForm.find('#c_name');
    var mobile = bookingForm.find('#mobile');
    var checkInDate = bookingForm.find('#check_in');
    var checkOutDate = bookingForm.find('#check_out');

    //    remove help block
    name.on('focusin',function(){
          $(this).nextAll('.help-block:first').html('');
    });
    price.on('focusin',function(){
          $(this).nextAll('.help-block:first').html('');
    });
    rooms.on('focusin',function(){
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
        if(!rooms.val())
        {
            rooms.nextAll('.help-block:first').addClass('text-warning').html('This field is required');
            return false;
        }

        // add dynamic post data
        dynamicData['name'] = name.val();
        dynamicData['price'] = price.val();
        dynamicData['track'] = 'add room';
        dynamicData['amenities'] = JSON.stringify(rooms.val());

        // post form data
        ajaxSky(dynamicData,roomUrl,'post')
        .done(function(data){
            rooms.parents('div').find('li.token').remove();
            rooms.val('');
            window.location.href = roomListUrl;
        })
        .fail(function(error){
            console.log('error');
        });
    });

      //sends rooms id: response total cost of selected rooms
      function computeTotalPrice(roomsArr,days=null){
        dynamicData = {};
        dynamicData['rooms'] = JSON.stringify(roomsArr);
        dynamicData['price_type'] = priceType.val();
        room.val(roomsArr[0]);
        if(!days){
            dynamicData['days'] = daysId.val();
        }else{
            dynamicData['days'] = days;
        }

        ajaxSky(dynamicData,computeTotalPriceUrl,'post')
        .done(function(response){
            totalCost = response.price;
            price.val(response.price);
            totalPrice.val(response.price)
            return response.price;
        })
        .fail(function(){
         return 0;
        });
      }

      /* compute price on price type change */
      priceType.on('change',function(){
        computeTotalPrice(rooms.val());
      });

      //  take care of tokenized select field
      //  show rooms on focusin
      rooms.on('tokenize:select', function(container){
         $(this).tokenize2().trigger('tokenize:search', [$(this).tokenize2().input.val()]);
      });

      rooms.on('tokenize:dropdown:hide', function(e, value){
            computeTotalPrice(rooms.val());
      });
      rooms.on('tokenize:tokens:remove',function(e, value){
            var arr = rooms.val();
            var index = arr.indexOf(value);

            if (index > -1) {
               arr.splice(index, 1);
            }
            computeTotalPrice(arr);
      });

      // get amenities
      rooms.tokenize2({
        placeholder: 'Select Room(s)',
        displayNoResultsMessage:true,
        tokensMaxItems:1,
        sortable: true,
        dataSource: function(search, object){
            $.ajax(getRoomsUrl, {
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
    //    ./amenities

    /* *******************************
     *
     * customer token events handler
     *
     *********************************/

    /* change customer field detail functions */
     function setCustomer(pk){
        dynamicData = {};
        dynamicData['customer'] = pk;
        dynamicData['track'] = 'Set Customer';
        ajaxSky(dynamicData,getCustomerUrl,'get')
        .done(function(response){
            customerName.val(response.results.text);
            mobile.val(response.results.mobile);
        })
        .fail(function(err){
            console.log(err);
        });
     }
    /* focusin event */
    customer.on('tokenize:select', function(container){
         $(this).tokenize2().trigger('tokenize:search', [$(this).tokenize2().input.val()]);
    });

    /* on add customer */
    customer.on('tokenize:dropdown:hide', function(e, value){
            pk = customer.val()[0];
            setCustomer(pk);
    });

    /* on remove customer */
    customer.on('tokenize:tokens:remove',function(e, value){
            /* clear customer details */
            customerName.val('');
            mobile.val('');
    });

    /* customer search token */
    customer.tokenize2({
        placeholder: 'Select Customer',
        displayNoResultsMessage:true,
        tokensMaxItems:1,
        //sortable: true,
        dataSource: function(search, object){
            $.ajax(getCustomerUrl, {
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

    /* *****************************
     *
     * datetimepicker functions
     *
     * ******************************/

    var checkIn = $('.check-in');
    var checkOut = $('.check-out');


    function getDays(start,end){
        var oneDay = 24*60*60*1000; // hours*minutes*seconds*milliseconds

        if(moment(end).isAfter(moment(start))){
            var firstDate = new Date(moment(start));
            var secondDate = new Date(moment(end));

            var diffDays = Math.round(Math.abs((firstDate.getTime() - secondDate.getTime())/(oneDay)));
            return diffDays;
        }else{
            return 0;
        }


    }

    /****************************************************************
     *
     * Compute checkout date based on check-in date and days to stay
     * return checkout date
     *
     ****************************************************************/
    function addDays(start, days)
    {
        return moment(start).add(parseInt(days), 'days').format('YYYY-MM-DD HH:mm:ss');
    }

    $('.days').on('keyup', function(){
        computeTotalPrice(rooms.val(),daysId.val());
        checkOut.val(addDays(checkIn.val(),daysId.val()));
    });

    checkIn.datetimepicker({format:'YYYY-MM-DD HH:mm:ss' }).on('dp.change', function(e) {
        stayDays = getDays(checkIn.val(),checkOut.val());
        daysId.val(stayDays);
        computeTotalPrice(rooms.val());
    });

    checkOut.datetimepicker({format:'YYYY-MM-DD HH:mm:ss' }).on('dp.change', function(e) {
        stayDays = getDays(checkIn.val(),checkOut.val());
        daysId.val(stayDays);
        computeTotalPrice(rooms.val());
    });

    /* if not editing booking info, set default dates */
    console.log(checkInDate.val());
    if(!checkInDate.val()){ checkInDate.val(today); }
    if(!checkOutDate.val()){ checkOutDate.val(tomorrow); }



    /****************************************
     *
     * create a booking script
     *
     ****************************************/
     bookingForm.validate({
        onkeyup: function(element) {$(element).valid()},
        rules:{
            name: {
              required:true,
              minlength:3
            },
            c_name: {
              required:true,
              minlength:2
            },
            price: {
              required:true,
              minlength:3
            },

          },
          submitHandler: function() {
              var f = document.getElementById('create-booking-form');
              var formData = new FormData(f);
              //formData.append(name, inputValue);
              $.ajax({
                  url: createBookingUrl,
                  type: "POST",
                  data: formData,
                  processData: false,
                  contentType: false,
                  success:function(data){
                    console.log(data);
                    console.log(typeof data);
                    $.jGrowl('Data sent successfully', {
                      header: 'Well done!',
                      theme: 'bg-success'
                    });
                    if(!boolRedirect.val()){
                       window.location.href = roomListUrl;
                    }else{
                       $('#ribbon'+boolRedirect.data('pk')).removeClass('hidden');
                       $('#available'+boolRedirect.data('pk')).html('Available on '+data.check_out);
                       $('#bookbtn'+boolRedirect.data('pk')).html('');
                       $('#bookbtn'+boolRedirect.data('pk')).removeClass('label-success');
                       $('#booking-modal').modal('hide');
                    }
                  },
                  error:function(error){
                    console.log(error);
                    $.jGrowl('Error adding', {
                        header: 'Oh snap!',
                        theme: 'bg-danger'
                    });
                  }
              });
        }
    });

    /* end */


});