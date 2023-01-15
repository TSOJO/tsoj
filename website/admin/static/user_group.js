(() => {
    'use strict'

    const form = document.querySelector('.needs-validation')
    form.addEventListener('submit', event => {
        if (!form.checkValidity()) {
            event.preventDefault()
            event.stopPropagation()
        }

        form.classList.add('was-validated')
    }, false)
})()

function update_selected(table) {
	ids = []
	for (row of table.bootstrapTable('getSelections')) {
		console.log(row)
		ids.push(row['id'])
	}
	return ids
}

$('#form').submit( function(e) {
	let user_ids = update_selected($('#user-group-table')).join(',');
	input = $('<input />')
		.attr('type', 'hidden')
		.attr('name', 'selected_user_ids')
		.attr('value', user_ids);
	
	input.appendTo('#form');
	return true;
});

$('#table').on('check.bs.table check-all.bs.table check-some.bs.table uncheck.bs.table uncheck-all.bs.table uncheck-some.bs.table', function (e, row, element) {
	update_selected($('#table'), $('#selected-problem-ids'));
})
