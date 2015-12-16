queue()
  .defer(d3.json, "data/go_lb/topics")
  .defer(d3.json, "data/go_lb/measures")
  .await(makeGraphs);

function getMonthName(d) {
	var monthNames = ["January", "February", "March", "April", "May", "June",
  	"July", "August", "September", "October", "November", "December"
	];
	var d = new Date(d);
	return monthNames[d.getMonth()];
}

function makeGoLBTopicsChart(data) {

	// Pluck values
	var topics = _.pluck(data, 'topic');
	var topicCountValues = _.pluck(data, 'count');

	// Convert counts into percentages
	var total = _.reduce(topicCountValues, function(memo, num) { return memo + num; }, 0);
	var topicPercentageValues = [];
	topicCountValues.forEach(function(t) {
		topicPercentageValues.push((t / total) * 100);
	});

	// Prepare chart data format
	var chartData = {
    labels: topics,
    datasets: [
      {
        label: "Topics Distribution",
        fillColor: "#1ca8dd",
        strokeColor: "rgba(28,168,221,0.8)",
        highlightFill: "rgba(28,168,221,0.5)",
        highlightStroke: "rgba(28,168,221,1)",
        data: topicPercentageValues
      }
    ]
	}

	// Render chart
	var ctx = document.getElementById("go-lb-topics").getContext("2d");
	var chart = new Chart(ctx).HorizontalBar(chartData, {
		barValueSpacing : 1,
		scaleShowGridLines: false,
	});

}

function makeGoLBStatusGraph(goLBStatus) {

	// Get a unique array of reporting dates
	var reportingDates = _.uniq(_.pluck(goLBStatus, 'reporting_date'));

	// Sort reporting dates
	reportingDates.sort(function(a, b) {
	  // Turn your strings into dates, and then subtract them
	  // to get a value that is either negative, positive, or zero.
	  return new Date(a) - new Date(b);
	});

	var monthNames = [];
	reportingDates.forEach(function (d) {
		monthNames.push(getMonthName(d));
	});

	var openRequests = [];
	var closedRequests = [];

	goLBStatus.forEach(function (r) {
		switch(r.status) {
			case 'Open':
				openRequests.push(r.record_count);
				break;
			case 'Closed':
				closedRequests.push(r.record_count);
				break;
		}
	});

	var chartData = {
	  labels: monthNames,
	  datasets: [
      {
        label: "Open",
        fillColor: "rgba(23,185,217,0.2)",
        strokeColor: "rgba(23,185,217,1.0)",
        pointColor: "rgba(23,185,217,1.0)",
        pointStrokeColor: "#fff",
        pointHighlightFill: "#fff",
        pointHighlightStroke: "rgba(23,185,217,1.0)",
        data: openRequests
      },
      {
        label: "Closed",
        fillColor: "rgba(10,50,76,0.2)",
        strokeColor: "rgba(10,50,76,1.0)",
        pointColor: "rgba(10,50,76,1.0)",
        pointStrokeColor: "#fff",
        pointHighlightFill: "#fff",
        pointHighlightStroke: "rgba(10,50,76,1.0)",
        data: closedRequests
      }
	  ]
	};

	var ctx = document.getElementById("go-lb-rolling-requests").getContext("2d");
	var chart = new Chart(ctx).Line(chartData, {
	  bezierCurve : false,
	  datasetFill : false,
		scaleShowGridLines : false,
	});

} // END makeGoLBStatusGraph

function populateMeasures(data) {

	var measures = data.measures;
	var measuresChartData = data.measures_charts;

	var openRequests = measures.openRequests[0].toLocaleString();
	$("#open-requests-metric").text(openRequests);

	var pendingRequests = measures.pendingRequests[0].toLocaleString();
	$("#pending-requests-metric").text(pendingRequests);

	var closedRequests = measures.closedRequests[0].toLocaleString();
	$("#closed-requests-metric").text(closedRequests);

	var avgDaysToClose = measures.avgDaysToClose[0].toLocaleString();
	$("#avg-days-to-close-metric").text(avgDaysToClose);

	// Options apply to all of our sparklines
  var sparklineOptions = {
    animation: false,
    responsive: true,
    bezierCurve : true,
    bezierCurveTension : 0.25,
    showScale: false,
    pointDotRadius: 0,
    pointDotStrokeWidth: 0,
    pointDot: false,
    showTooltips: false
  };

  var chartData = {
    labels   : _.pluck(measuresChartData.openRequests, 'reporting_month'),
    datasets : [
    	{
    		fillColor:'rgba(28,168,221,.03)',
    		strokeColor: '#1ca8dd',
    		pointStrokeColor: '#fff',
    		data: _.pluck(measuresChartData.openRequests, 'request_count')
    	}
    ]
  };
	var ctx = document.getElementById("open-requests-sparkline").getContext("2d");
	var chart = new Chart(ctx).Line(chartData, sparklineOptions);

  var chartData = {
    labels   : _.pluck(measuresChartData.pendingRequests, 'reporting_month'),
    datasets : [
    	{
    		fillColor:'rgba(28,168,221,.03)',
    		strokeColor: '#1ca8dd',
    		pointStrokeColor: '#fff',
    		data: _.pluck(measuresChartData.pendingRequests, 'request_count')
    	}
    ]
  };
	var ctx = document.getElementById("pending-requests-sparkline").getContext("2d");
	var chart = new Chart(ctx).Line(chartData, sparklineOptions);

  var chartData = {
    labels   : _.pluck(measuresChartData.closedRequests, 'reporting_month'),
    datasets : [
    	{
    		fillColor:'rgba(28,168,221,.03)',
    		strokeColor: '#1ca8dd',
    		pointStrokeColor: '#fff',
    		data: _.pluck(measuresChartData.closedRequests, 'request_count')
    	}
    ]
  };
	var ctx = document.getElementById("closed-requests-sparkline").getContext("2d");
	var chart = new Chart(ctx).Line(chartData, sparklineOptions);

  var chartData = {
    labels   : _.pluck(measuresChartData.averageRequests, 'reporting_month'),
    datasets : [
    	{
    		fillColor:'rgba(28,168,221,.03)',
    		strokeColor: '#1ca8dd',
    		pointStrokeColor: '#fff',
    		data: _.pluck(measuresChartData.averageRequests, 'avg_days_to_close')
    	}
    ]
  };
	var ctx = document.getElementById("average-requests-sparkline").getContext("2d");
	var chart = new Chart(ctx).Line(chartData, sparklineOptions);

}

function makeGraphs(error, topicsData, statsData) {
	// Chart.defaults.global.responsive = true;
	// Chart.defaults.global.maintainAspectRatio = false;
	Chart.defaults.global.scaleLineColor = "#a9aebd";
	Chart.defaults.global.scaleFontColor = "#a9aebd";

	makeGoLBTopicsChart(topicsData);
	populateMeasures(statsData);
};