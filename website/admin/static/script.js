window.onpageshow = function(event) {
    // Initialise tooltips.
    $('[data-bs-toggle="tooltip"]').tooltip()
    $('[data-bs-toggle="tooltip"]').on('mouseleave', function () {
        $(this).tooltip('hide')
    })
}

function copy_text(element, assignment_url) {
    const text = window.location.hostname + assignment_url
    navigator.clipboard.writeText(text)
    const tooltip = bootstrap.Tooltip.getInstance(element)
    tooltip.show()
}

assignment_searcher = custom_searcher(['id', 'time', 'creator', 'problems', 'groups'])
create_assignment_searcher = custom_searcher(['id', 'name'])  // since both problem and group tables have `id` and `name`
privilege_searcher = custom_searcher(['id', 'name', 'privileges'])
edit_group_searcher = custom_searcher(['name', 'id', 'privileges'])
group_searcher = custom_searcher(['name', 'students'])