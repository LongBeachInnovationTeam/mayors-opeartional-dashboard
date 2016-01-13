queue()
  .defer(d3.json, "data/go_lb/topics")
  .defer(d3.json, "data/go_lb/measures")
  //.defer(d3.json, "data/go_lb/departments")
  .await(makeGraphs);

// ensures that our d3 chart is only rendered once
var isScatterPlotRendered = false;

// Render contect on tab switch
$('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
  var target = $(e.target).attr("href");
  if (target == '#locations') {
		renderRequestsMap();
  }
  if (target == '#departments' && !isScatterPlotRendered) {
  	$.getJSON('data/go_lb/departments', function (data) {
  		renderDepartmentAverageChart(data);
		});
  }
});

// function getMonthName(d) {
// 	var monthNames = ["January", "February", "March", "April", "May", "June",
//   	"July", "August", "September", "October", "November", "December"
// 	];
// 	var d = new Date(d);
// 	return monthNames[d.getMonth()];
// }

function Month(date) {
	this.date = new Date(date);
}

Month.prototype.getMonthName = function () {
	this.monthNames = [
		"January", "February", "March", "April", "May", "June",
  	"July", "August", "September", "October", "November", "December"
	];
	return this.monthNames[this.date.getMonth()];
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

function renderTopicsCountChart(data) {

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
	var ctx = document.getElementById("go-lb-topic-count").getContext("2d");
	var chart = new Chart(ctx).HorizontalBar(chartData, {
		animation: false,
		barValueSpacing : 1,
		responsive: true,
		scaleFontColor: "#a9aebd",
		scaleLineColor: "#a9aebd",
		scaleShowGridLines: false
	});

}

function renderTopicsAverageChart(data) {

	// Pluck values
	var labels = _.pluck(data, 'topic');
	var values = _.pluck(data, 'avg_days_to_close');

	// Prepare chart data format
	var chartData = {
    labels: labels,
    datasets: [
      {
        label: "Topic Average",
        fillColor: "#630CE8",
        strokeColor: "rgba(99,12,232,0.8)",
        highlightFill: "rgba(99,12,232,0.5)",
        highlightStroke: "rgba(99,12,232,1)",
        data: values
      }
    ]
	}

	// Render chart
	var ctx = document.getElementById("go-lb-topic-average").getContext("2d");
	var chart = new Chart(ctx).HorizontalBar(chartData, {
		animation: false,
		barValueSpacing : 1,
		responsive: true,
		scaleFontColor: "#a9aebd",
		scaleLabel: "<%=value%> days",
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

	console.log(measuresChartData);

	// Populate numbers
	renderStatCardValue("#open-requests-metric", "openRequests", measures);
	renderStatCardValue("#pending-requests-metric", "pendingRequests", measures);
	renderStatCardValue("#closed-requests-metric", "closedRequests", measures);
	renderStatCardValue("#avg-days-to-close-metric", "avgDaysToClose", measures);

	// Render sparklines
	renderStatCardSparkline("open-requests-sparkline", "openRequests", "reporting_date", "request_count", measuresChartData);
	renderStatCardSparkline("pending-requests-sparkline", "pendingRequests", "reporting_date", "request_count", measuresChartData);
	renderStatCardSparkline("closed-requests-sparkline", "closedRequests", "reporting_date", "request_count", measuresChartData);
	renderStatCardSparkline("average-requests-sparkline", "averageRequests", "reporting_date", "avg_days_to_close", measuresChartData);

}

function renderDepartmentAverageChart(data) {

	var margin = {
		"left": 40,
		"right": 30,
		"top": 30,
		"bottom": 30
	};

  var width = document.getElementById("department-scatter").clientWidth;
  var height = 400;

  // this will be our color scale. An Ordinal scale.
  var colors = d3.scale.category10();

  var svg = d3.select("#department-scatter")
  	.append("svg")
  	.attr("width", width)
  	.attr("height", height)
    .on({
      "click": function() {
      	window.location = "/go_lb/drilldown";
      },
    })
  	.append("g")
    	.attr("transform", "translate(" + margin.left + "," + margin.top + ")");


  var x = d3.scale.linear()
    .domain(d3.extent(data, function (d) {
    	return d.avg_days_to_close;
  	}))
		// the range maps the domain to values from 0 to the width minus the left and right margin (used to space out the visualization)
		.range([0, width - margin.left - margin.right]);

  // this does the same as for the y axis but maps from the rating variable to the height to 0.
  var y = d3.scale.linear()
  	.domain(d3.extent(data, function (d) {
      return d.requests_count;
  	}))
	  // Note that height goes first due to the weird SVG coordinate system
	  .range([height - margin.top - margin.bottom, 0]);

  // We add the axes SVG component. At this point, this is just a placeholder.
  // The actual axis will be added in a bit
  svg.append("g")
  	.attr("class", "x axis")
  	.attr("transform", "translate(0," + y.range()[0] + ")");

  svg.append("text")
    .attr("fill", "#a9aebd")
    .attr("text-anchor", "end")
    .attr("x", width / 2)
    .attr("y", height - 35)
    .text("Average days to close");

  svg.append("g")
		.attr("class", "y axis");

  svg.append("text")
    .attr("transform", "rotate(-90)")
    .attr("y", 0 - margin.left)
    .attr("x", 0 - (height / 2))
    .attr("dy", "1em")
    .style("text-anchor", "middle")
    .text("No. of requests");

  var xAxis = d3.svg.axis().scale(x).orient("bottom").tickPadding(2);
  var yAxis = d3.svg.axis().scale(y).orient("left").tickPadding(2);
  svg.selectAll("g.y.axis").call(yAxis);
  svg.selectAll("g.x.axis").call(xAxis);

  // now, we can get down to the data part, and drawing stuff.
  // We are telling D3 that all nodes (g elements with class node)
  // will have data attached to them. The 'key' we use
  // (to let D3 know the uniqueness of items) will be the name.
  var department = svg.selectAll("g.node")
		.data(data, function (d) {
	  	if (d.avg_days_to_close > 0.00)
	  	{
	  		return d.department;
	  	}
	  });

  var departmentGroup = department.enter()
	  .append("g")
	  .attr("class", "node")
	  .attr('transform', function (d) {
	    return "translate(" + x(d.avg_days_to_close) + "," + y(d.requests_count) + ")";
	  });

  departmentGroup.append("circle")
    .attr("r", function (d) {
    	return Math.sqrt(d.requests_count);
		})
    .attr("class", "dot")
    .style("fill", function (d) { return colors(d.department); });

  // now we add some text, so we can see what each item is.
  departmentGroup.append("text")
    .style("text-anchor", "middle")
    .attr("dy", -15)
    .text(function (d) { return d.department_display_name; });

  isScatterPlotRendered = true;
}


function makeGraphs(error, topicsData, statsData) {
	if (!error) {
		// Set chart global defaults
		Chart.defaults.global.scaleFontFamily = "'Roboto', sans-serif";

		renderTopicsCountChart(topicsData.topics_count);
		renderTopicsAverageChart(topicsData.topics_average)
		renderStatCards(statsData);
	}
};