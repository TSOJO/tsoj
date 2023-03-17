function update_selected(table, target, key) {
	selected_keys = []
	selected_ids = []
	for (row of table.bootstrapTable('getSelections')) {
		selected_keys.push(row[key])
		selected_ids.push(row['id'])
	}
	target.text(selected_keys.join(', '))
	return selected_ids
}

function update_table(table, data) {
	data = data.split(', ')
	table.bootstrapTable('checkBy', {field: 'id', values: data})
}

$('#form').submit(() => {
	let problem_ids = update_selected($('#table'), $('#selected-problem-ids'), 'id').join(',')
	let user_group_ids = update_selected($('#user-group-table'), $('#selected-user-group-names'), 'name').join(',')

	if (problem_ids === '') {
		alert('No problems selected!')
		return false
	}
	if (user_group_ids === '') {
		alert('No groups selected!')
		return false
	}

	input = $('<input />')
		.attr('type', 'hidden')
		.attr('name', 'selected_problem_ids')
		.attr('value', problem_ids)
	input2 = $('<input />')
		.attr('type', 'hidden')
		.attr('name', 'selected_user_group_ids')
		.attr('value', user_group_ids)
	
	input.appendTo('#form')
	input2.appendTo('#form')
	return true
})

$('#table').on('check.bs.table check-all.bs.table check-some.bs.table uncheck.bs.table uncheck-all.bs.table uncheck-some.bs.table', () => {
	update_selected($('#table'), $('#selected-problem-ids'), 'id')
})

$('#user-group-table').on('check.bs.table check-all.bs.table check-some.bs.table uncheck.bs.table uncheck-all.bs.table uncheck-some.bs.table', () => {
	update_selected($('#user-group-table'), $('#selected-user-group-names'), 'name')
})

// ! Form submission is buggy if user uses 'back' button to go back to the form, so uncheck all.
window.onpageshow = () => {
    $('#table').bootstrapTable('uncheckAll')
	$('#user-group-table').bootstrapTable('uncheckAll')
}
