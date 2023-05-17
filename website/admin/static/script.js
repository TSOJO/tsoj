window.onpageshow = function(event) {
    // Initialise tooltips.
    $('[data-bs-toggle="tooltip"]').tooltip()
    $('[data-bs-toggle="tooltip"]').on('mouseleave', function () {
        $(this).tooltip('hide')
    })
}

function copy_text(element, text, add_hostname) {
    if (add_hostname) {
        text = window.location.hostname + text
    }
    navigator.clipboard.writeText(text)
    const tooltip = bootstrap.Tooltip.getInstance(element)
    tooltip.show()
}

assignment_searcher = custom_searcher(['id', 'time', 'creator', 'problems', 'groups'])
edit_assignment_searcher = custom_searcher(['id', 'name'])  // since both problem and group tables have `id` and `name`
privilege_searcher = custom_searcher(['id', 'name', 'privileges'])
edit_group_searcher = custom_searcher(['name', 'id', 'privileges'])
group_searcher = custom_searcher(['name', 'students'])

$('#problem-head-select').change(() => {
    let head = $('#problem-head-select').val()
    if(head === "Other") {
        $('#problem-head-group').show()
        $('#problem-head-other').removeAttr('disabled')
        $('#problem-id').html('-')
    } else {
        $('#problem-head-group').hide()
        $('#problem-head-other').val('')
        $('#problem-head-other').attr('disabled', 'true')
        $('#problem-id').html(`${head}-${problemMaxIDs[head]+1}`)
        $('#problem-id-hidden').val(`${head}-${problemMaxIDs[head]+1}`)
    }
})

$('#problem-head-other').change(() => {
    let head = $('#problem-head-other').val()
    let number = (head in problemMaxIDs) ? problemMaxIDs[head] + 1 : 1
    $('#problem-id').html(`${head}-${number}`)
    $('#problem-id-hidden').val(`${head}-${number}`)
})

function getSelectOption(name) {
    let option = $(document.createElement('option'))
    option.attr('value', name)
    option.html(name)
    return option
}

let problemMaxIDs = {}
function createProblem() {
    $('#problem-head-select').empty()
    $('#problem-head-group').hide()
    $('#problem-id').empty()
    $('#problem-id-hidden').val('')
    fetch('/api/get-problem-max-ids')
        .then(response => response.json())
        .then(data => {
            for(let [head, max_id] of Object.entries(data)) {
                $('#problem-head-select').append(getSelectOption(head))
                problemMaxIDs[head] = max_id
            }
            $('#problem-head-select').append(getSelectOption("Other"))
            $('#problem-head-select').selectpicker('refresh')
        })
}