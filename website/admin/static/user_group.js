function get_selected(table) {
	ids = []
	for (row of table.bootstrapTable('getSelections')) {
		ids.push(row['id'])
	}
	return ids
}

$('#form').submit( function(e) {
	let user_ids = get_selected($('#user-group-table')).join(',')
	if (user_ids != '') {
		input = $('<input />')
			.attr('type', 'hidden')
			.attr('name', 'selected_user_ids')
			.attr('value', user_ids)
		input.appendTo('#form')
	}
	
	return true;
});

// ! Form submission is buggy if user uses 'back' button to go back to the form, so uncheck all.
window.onpageshow = function(e) {
	$('#user-group-table').bootstrapTable('uncheckAll')
};