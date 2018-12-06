!function() {

	var data_url = "/api/search-map/timeline-data";
	$.getJSON( data_url, function( data ) { 
		// console.log('data=');
		// console.log(data);
		data = MG.convert.date(data, 'date');
		MG.data_graphic({
			title: "Records over time",
			description: "To filter based on Time click on 'Filter Time/Space' and then choose 'by Date'.",
			data: data,
			width: 1000,
			height: 100,
			right: 40,
			target: document.getElementById('timeline-canvas'),
			x_accessor: 'date',
			y_accessor: 'value'
		});
	});
}();
