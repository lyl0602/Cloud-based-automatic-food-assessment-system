var options = {
		 chart: {
		        type: 'scatter',
		        zoomType: 'xy'
		    },
		    title: {
		        text: 'UPMC Insurance Evaluation'
		    },
		    subtitle: {
		        text: 'Source: UPMC  2017'
		    },
		    xAxis: {
		        title: {
		            enabled: true,
		            text: 'Image ID'
		        },
		        startOnTick: true,
		        endOnTick: true,
		        showLastLabel: true
		    },
		    yAxis: {
		        title: {
		            text: 'Score'
		        }
		    },
		    legend: {
		        layout: 'vertical',
		        align: 'left',
		        verticalAlign: 'top',
		        x: 100,
		        y: 70,
		        floating: true,
		        backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
		        borderWidth: 1
		    },
		    plotOptions: {
		        scatter: {
		            marker: {
		                radius: 5,
		                states: {
		                    hover: {
		                        enabled: true,
		                        lineColor: 'rgb(100,100,100)'
		                    }
		                }
		            },
		            states: {
		                hover: {
		                    marker: {
		                        enabled: false
		                    }
		                }
		            },
		            tooltip: {
		                headerFormat: '<b>{series.name}</b><br>',
		                pointFormat: 'ID: {point.x}, Score: {point.y} '
		            }
		        }
		    },
		    series: []
		
};

$(document).ready(function() {
	console.log("start");
	get_score();

	
	
	
	
	

});

function get_score() {
	
	$.ajax({
		type : "GET",
		contentType : "application/json",
		url : "/get_score",
		dataType : 'json',
		cache : false,
		timeout : 9000000,
		success : function(data) {
			console.log("SUCCESS : ", data);
			var obj = JSON.parse(data);
			var len = 0;
			tmp = [];
			for ( var x in obj) {
				if (obj.hasOwnProperty(x)) {
					console.log(x);
					console.log(obj[x]);
					tmp.push(x);
					tmp.push(obj[x]);
					len++;
					
				}
			}
			console.log("arr in success: " + tmp);
			console.log("len in success: " + len);
			
			var myarray=new Array(len);
			
			for (var i=0; i < len; i++) {
				myarray[i] = new Array(2);
			}
			
			for (var i = 0; i < len; i++) {
				myarray[i][0] = tmp[i * 2];
				myarray[i][1] = tmp[i * 2 + 1];
			}
			
			console.log("arr in success: " + myarray[0]); 
			draw_chart(myarray);
			
		},
		error : function(e) {
			console.log("ERROR : ", e);
		}
	});
	

}

function draw_chart(arr) {
	console.log("arr call back: " + arr);
	var len = arr.length;
	console.log("len call back: " + len);
	
	var newarr = new Array(len);
	for (var i=0; i < len; i++) {
		newarr[i] = new Array(2);
	}
	var sum = 0.0;
	for (var i = 0; i < len; i++) {
		newarr[i][0] = parseFloat(arr[i][0]);
		newarr[i][1] = parseFloat(arr[i][1]);
		console.log(newarr[i][1]);
		sum += newarr[i][1];
	}
	var test = [[1,-3.4], [2,4.5]];
	console.log("test call back: " + test);
	console.log("newarr call back: " + newarr);
	console.log("sum call back: " + sum);
	document.getElementById('total').innerHTML += '<b>Total Score: '+ sum + '</b>';
	options.series.push({
		name : 'Score',
		color : 'rgba(223, 83, 83, .5)',
		data : newarr
	})
	
	var chart = new Highcharts.Chart('container', options);
}






