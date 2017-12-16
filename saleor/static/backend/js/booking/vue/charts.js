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
        yearlyVisitsChart:function(data){
            Highcharts.chart('yearly-visits-chart', {
                chart: {
                    type: 'line'
                },
                title: {
                    text: 'Number of Visitors Monthly report'
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

            $('.yearly-visits-chart').css('display', 'none');

        },
        yearlyAmountChart:function(data){
            Highcharts.chart('yearly-amount-chart', {
                chart: {
                    type: 'line'
                },
                title: {
                    text: 'Amount Earned Monthly report'
                },

                xAxis: {
                    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                },
                yAxis: {
                    title: {
                        text: 'Total Amount(s)'
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
        lastVisitsChart: function(data){
            $('#last-visits-chart').highcharts({
                title: {
                  text: 'Last Room Booking Report',
                },
                xAxis: {
                  type: 'datetime'
                },
                yAxis: {
                    title: {
                        text: 'Total Visits(s)'
                    }
                },
                series: [{
                  name: 'Visits',
                  data:  data
                  }]
            });
        },
        lastAmountChart: function(data){
            $('#last-amount-chart').highcharts({
                title: {
                  text: 'Latest Booking Report',
                },
                subtitle: {
                    text: 'Total Amount Generated on Last Visits Report'
                },
                xAxis: {
                  type: 'datetime'
                },
                yAxis: {
                    title: {
                        text: 'Total Amount(s)'
                    }
                },
                series: [{
                  name: 'Total',
                  data:  data
                  }]
            });
        }
    },
    mounted:function(){
    /* initailize chart */
        this.$http.get($('.pageUrls').data('listurl'))
            .then(function(data){
                /* decode json response */
                data = JSON.parse(data.bodyText);

                /* 1.1 get yearly visits */
                this.items = data.results.yearly_visits;
                /* render chart */
                this.yearlyVisitsChart(this.items);

                /* 1.2 get yearly visits */
                this.items = data.results.yearly_amount;
                /* render chart */
                this.yearlyAmountChart(this.items);

                /* 2. get last visits */
                var obj = data.results.last_visits;
                var temp = [];
                 Object.keys(obj).forEach(function(key) {
                    var temp2 = [moment.utc(obj[key].date).valueOf(),parseInt(obj[key].total)];
                    temp.push(temp2);
                });
                /* render chart */
                this.lastVisitsChart(temp);

                /* 3. get last booking total prices */
                var obj = data.results.last_amount;
                var temp = [];
                 Object.keys(obj).forEach(function(key) {
                    var temp2 = [moment.utc(obj[key].date).valueOf(),parseInt(obj[key].total)];
                    temp.push(temp2);
                });
                /* render chart */
                this.lastAmountChart(temp);

                this.loader = false;
            }, function(error){
                console.log(error.statusText);
        });

    },
});