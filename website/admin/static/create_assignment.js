function update_selected(table, selected_ids) {
	ids = []
	for (row of table.bootstrapTable('getSelections')) {
		ids.push(row['id'])
	}
	selected_ids.text(ids.join(', '))
	return ids
}

$('#form').submit( function(e) {
	let problem_ids = update_selected($('#table'), $('#selected-problem-ids')).join(',')
	let user_group_ids = update_selected($('#user-group-table'), $('#selected-user-group-ids')).join(',')
	if (problem_ids == '') {
		alert('No problems selected!');
		return false;
	}
	input = $('<input />')
		.attr('type', 'hidden')
		.attr('name', 'selected_problem_ids')
		.attr('value', problem_ids);
	input2 = $('<input />')
		.attr('type', 'hidden')
		.attr('name', 'selected_user_group_ids')
		.attr('value', user_group_ids);
	
	input.appendTo('#form');
	input2.appendTo('#form');
	return true;
});

$('#table').on('check.bs.table check-all.bs.table check-some.bs.table uncheck.bs.table uncheck-all.bs.table uncheck-some.bs.table', function (e, row, element) {
	update_selected($('#table'), $('#selected-problem-ids'));
})

$('#user-group-table').on('check.bs.table check-all.bs.table check-some.bs.table uncheck.bs.table uncheck-all.bs.table uncheck-some.bs.table', function (e, row, element) {
	update_selected($('#user-group-table'), $('#selected-user-group-ids'));
})

