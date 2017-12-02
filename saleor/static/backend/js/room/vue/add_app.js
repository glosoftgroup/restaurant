$ = jQuery;

var parent = new Vue({
    el:"#vue-app",
    delimiters: ['${', '}'],
    data:{
       'name': 'Add room',
       'autoComplete': true,
       'nightly': null,
       'daytime': null,
       'weekly' : null,
       'daily'  : null,
       'monthly': null
    },
    created:function(){
       console.log('vue running in parent');
       if($('#room_id').val()){
           this.daily = $('#daily').val();
           this.nightly = $('#nightly').val();
           this.daytime = $('#daytime').val();
           this.weekly = $('#weekly').val();
           this.monthly = $('#monthly').val();
       }

       //console.log(today);
    },
    methods:{
        computeFullDay: function(){
          /* check if field auto complete is enabled */
          if(this.autoComplete){
            this.nightly = this.daily / 2;
            this.daytime = this.daily / 2;
            this.weekly = (parseInt(this.daytime) + parseInt(this.nightly)) * 7;
            this.monthly = (parseInt(this.daytime) + parseInt(this.nightly)) * 30;
          }
        },
        computeHalfDay:function(){
            /* check if field auto complete is enabled */
            if(this.autoComplete){
                this.monthly = (parseInt(this.daytime) + parseInt(this.nightly)) * 30
                this.weekly  = (parseInt(this.daytime) + parseInt(this.nightly)) * 7
            }
        }
    }
});