$ = jQuery;

//vue
var chart = new Vue({
    el:"#vue-app",
    delimiters: ['${', '}'],
    data:{
       'name':'Book Listing',
       items:[],
       loader:true
    },
    methods:{
        yearlyChart:function(data){
            Highcharts.chart('container', {
                chart: {
                    type: 'line'
                },
                title: {
                    text: 'Monthly report'
                },

                xAxis: {
                    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                },
                yAxis: {
                    title: {
                        text: 'Total Visits(s)'
                    }
                },
                plotOptions: {
                    line: {
                        dataLabels: {
                            enabled: true
                        },
                        enableMouseTracking: false
                    }
                },
                series: [
                    {
                        name: 'Room Booking',
                        data: data
                    },


                ]
            });

            $('.container').css('display', 'none');

        },
        lastTenChart: function(data){
            $('#last-ten').highcharts({
                title: {
                  text: 'Everything seems fine',
                },
                xAxis: {
                  type: 'datetime'
                },
                series: [{
                  name: 'A fine series',
                  data: data
                }]
              });
        }
    },
    mounted:function(){
    /* initailize chart */
        this.$http.get($('.pageUrls').data('listurl'))
            .then(function(data){
                data = JSON.parse(data.bodyText);
                this.items = data.results.yearly;
                this.yearlyChart(this.items);
                var obj = data.results.last_booking;
                var temp = [];
                 Object.keys(obj).forEach(function(key) {
                    //console.log(key, obj[key]);
                    temp.push(moment( obj['date']).valueOf(),key);
                });
                console.log(temp);
                this.lastTenChart(temp);

                this.loader = false;
            }, function(error){
                console.log(error.statusText);
        });

    },
});