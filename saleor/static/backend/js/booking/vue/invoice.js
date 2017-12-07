/* ************************************
 *
 *  invoicing app
 *
 * ************************************
*/
$ = jQuery;
var modal = $('#payment-modal');
var dynamicData = {};

// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

var parent = new Vue({
    el:"#printme",
    delimiters: ['${', '}'],
    data:{
       'name':'Invoicing',
       'date': null,
       'amount_paid':null,
       'payment_option':null,
       'description':null,
       'book':null,
       'invoice_number':null,
       paymentListUrl:null,
       total_paid:null,
       balance:null,
       payments: []
    },
    methods:{
        openModal:function(){
            /* open modal */
            $('#payment-modal').modal();
            this.date = $('#date').val();
            this.invoice_number = $('#invoice_number').val();
            this.book = $('#bookId').val();
            console.warn(this.data);
        },
        addPayment:function(){
            var addPaymentUrl = $('.pageUrls').data('payurl');
            var form = document.getElementById('pay-form');
            var f = new FormData(form);

            this.$http.post(addPaymentUrl,f)
            .then(function(data){
                $('#payment-modal').modal('hide');
                this.populatePayment();
                data = JSON.parse(data.bodyText);
                this.balance = data.balance;
                this.total_paid = data.total_paid;
            }, function(error){
                console.log(error.statusText);
            });
        },
        populatePayment:function(){
            this.$http.get(this.paymentListUrl)
            .then(function(data){
                this.payments = JSON.parse(data.bodyText);
            }, function(error){
                console.log(error.statusText);
            });
        }
    },
    created:function(){
        $('.daterange-single').datepicker();
        $('#date').val(moment().format('YYYY-MM-DD'));
        this.date = moment().format('YYYY-MM-DD');
        this.paymentListUrl = $('.pageUrls').data('paylisturl');
        this.balance = $('#balance').val();
        this.total_paid = $('#total_paid').val();
        this.populatePayment();

    }
});