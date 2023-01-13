var $table = $('#table')
var $button = $('#button')

function update_selected() {
	ids = []
	for (row of $table.bootstrapTable('getSelections')) {
		ids.push(row['id'])
	}
	$('#selected_ids').text(ids.join(', '))
	return ids
}

$('#form').submit( function(e) {
	ids = update_selected().join(',')
	if (ids == '') {
		alert('No problems selected!');
		return false;
	}
	input = $('<input />')
		.attr('type', 'hidden')
		.attr('name', 'selected_ids')
		.attr('value', ids);
	input.appendTo('#form');
	return true;
});

$('#table').on('check.bs.table check-all.bs.table check-some.bs.table uncheck.bs.table uncheck-all.bs.table uncheck-some.bs.table', function (e, row, element) {
	update_selected();
})
