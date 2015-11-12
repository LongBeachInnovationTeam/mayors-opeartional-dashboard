queue()
  .defer(d3.json, "/data/go_lb/topics")
  .defer(d3.json, "/data/go_lb/measures")
  .defer(d3.json, "/data/go_lb/status_ytd")
  .await(makeGraphs);

function getMonthName(d) {
	var monthNames = ["January", "February", "March", "April", "May", "June",
  	"July", "August", "September", "October", "November", "December"
	];
	var d = new Date(d);
	return monthNames[d.getMonth()];
}

// var cells = [
// 	'go-lb-topics',
// 	'go-lb-map-canvas',
// 	'go-lb-rolling-requests',
// 	'duplicate-requests-table'
// ];

// function getTallestCellHeight() {
// 	var tallestHeight = 0;
// 	cells.forEach(function(c) {
// 		var h = $("#" + c).height();
// 		if (h > tallestHeight) {
// 			tallestHeight = h;
// 		}
// 	});
// 	return tallestHeight;
// }

// function resizeCells() {
// 	var h = getTallestCellHeight();
// 	$(".chart-stage").height(h);

// 	//$("#go-lb-topics").height(h - 20);
// 	$("#go-lb-topics").css({
// 		'margin-top': '50px'
// 	});

// }

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
        fillColor: "rgba(23,185,217,1)",
        strokeColor: "rgba(23,185,217,0.8)",
        highlightFill: "rgba(23,185,217,0.75)",
        highlightStroke: "rgba(23,185,217,1)",
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

function populateMeasures(measures) {
	var openRequests = measures.openRequests[0].toLocaleString();
	$("#open-requests-metric span").text(openRequests);

	var pendingRequests = measures.pendingRequests[0].toLocaleString();
	$("#pending-requests-metric span").text(pendingRequests);

	var closedRequests = measures.closedRequests[0].toLocaleString();
	$("#closed-requests-metric span").text(closedRequests);

	var avgDaysToClose = measures.avgDaysToClose[0].toLocaleString();
	$("#avg-days-to-close-metric span").text(avgDaysToClose);
}

function makeGraphs(error, goLBTopics, measures, goLBStatus) {
	Chart.defaults.global.responsive = true;
	Chart.defaults.global.maintainAspectRatio = false;

	makeGoLBTopicsChart(goLBTopics);
	populateMeasures(measures);
	makeGoLBStatusGraph(goLBStatus);
	resizeCells();
};