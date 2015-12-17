queue()
  .defer(d3.json, "data/go_lb/topics")
  .defer(d3.json, "data/go_lb/measures")
  .await(makeGraphs);

$('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
  var target = $(e.target).attr("href");
  if ((target == '#locations')) {
		renderRequestsMap();
  }
});

function getMonthName(d) {
	var monthNames = ["January", "February", "March", "April", "May", "June",
  	"July", "August", "September", "October", "November", "December"
	];
	var d = new Date(d);
	return monthNames[d.getMonth()];
}

function renderRequestsMap() {
	// Select the div which holds our map content
	var mapCanvas = $('#go-lb-map-canvas');

	// Make sure the map canvas isn't already rendered
	// i.e. see if there is content inside the div
	if (mapCanvas.html().length == 0)
	{
		cartodb.createVis('go-lb-map-canvas', 'https://alchave.cartodb.com/api/v2/viz/226e9248-8780-11e5-bc45-0ea31932ec1d/viz.json');
	}
}

function renderTopicsChart(data) {

	// Pluck values
	var topics = _.pluck(data, 'topic');
	var topicCountValues = _.pluck(data, 'count');

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
        data: topicCountValues
      }
    ]
	}

	// Render chart
	var ctx = document.getElementById("go-lb-topics").getContext("2d");
	var chart = new Chart(ctx).HorizontalBar(chartData, {
		animation: false,
		barValueSpacing : 1,
		responsive: true,
		scaleFontColor: "#a9aebd",
		scaleLineColor: "#a9aebd",
		scaleShowGridLines: false
	});

}

function renderStatCardValue(elemId, measure, data) {
	var t = data[measure][0].toLocaleString();
	$(elemId).text(t);
}

function renderStatCardSparkline(elemId, measure, labelName, valueName, data) {

	// Options apply to all of our sparklines
  var sparklineOptions = {
    animation: false,
    responsive: true,
    bezierCurve: true,
    bezierCurveTension: 0.25,
    showScale: false,
    pointDotRadius: 0,
    pointDotStrokeWidth: 0,
    pointDot: false,
    scaleFontColor: "#a9aebd",
    scaleShowGridLines: false,
    scaleShowLabels: false,
    showTooltips: false
  };

  // Get month value name for the first and last
  // label names only. Put blank strings for
  // all the other labels.
  // var labels = _.pluck(data[measure], labelName);
  // labels.forEach(function (l, i) {
  // 	if (i == 0 || i == labels.length - 1) {
  // 		labels[i] = getMonthName(l);
  // 	}
  // 	else {
  // 		labels[i] = "";
  // 	}
  // });

  // Prepare chart data
  var chartData = {
    labels   : _.pluck(data[measure], labelName),
    datasets : [
    	{
    		fillColor:'rgba(28,168,221,.03)',
    		strokeColor: '#1ca8dd',
    		pointStrokeColor: '#fff',
    		data: _.pluck(data[measure], valueName)
    	}
    ]
  };

  // Get canvas context and render sparkline chart
	var ctx = document.getElementById(elemId).getContext("2d");
	var chart = new Chart(ctx).Line(chartData, sparklineOptions);

}

function renderStatCards(data) {

	var measures = data.measures;
	var measuresChartData = data.measures_charts;

	// Populate numbers
	renderStatCardValue("#open-requests-metric", "openRequests", measures);
	renderStatCardValue("#pending-requests-metric", "pendingRequests", measures);
	renderStatCardValue("#closed-requests-metric", "closedRequests", measures);
	renderStatCardValue("#avg-days-to-close-metric", "avgDaysToClose", measures);

	// Render sparklines
	renderStatCardSparkline("open-requests-sparkline", "openRequests", "reporting_month", "request_count", measuresChartData);
	renderStatCardSparkline("pending-requests-sparkline", "pendingRequests", "reporting_month", "request_count", measuresChartData);
	renderStatCardSparkline("closed-requests-sparkline", "closedRequests", "reporting_month", "request_count", measuresChartData);
	renderStatCardSparkline("average-requests-sparkline", "averageRequests", "reporting_month", "avg_days_to_close", measuresChartData);

}

function makeGraphs(error, topicsData, statsData, departmentData) {

	if (!error) {
		// Set chart global defaults
		Chart.defaults.global.scaleFontFamily = "'Roboto', sans-serif";

		renderTopicsChart(topicsData);
		renderStatCards(statsData);
	}

};