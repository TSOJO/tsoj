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