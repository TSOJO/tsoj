$('#language-select').change(() => {
    let editor = ace.edit('editor')
    editor.session.setMode("ace/mode/" + getAceMode($('#language-select').val()))
})

$('#custom-test-checkbox').change(() => {
    if ($('#custom-test-checkbox').is(':checked')) {
        $('#custom-test-group').show()
    } else {
        $('#custom-test-group').hide()
    }
})
$('#custom-test-group').hide()

function disableTestElements() {
    $('#custom-test-button').prop('disabled', true)
    $('#custom-test-button').html(
        '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Testing...')
    $('#custom-input').prop('disabled', true)
    $('#custom-output').prop('disabled', true)
    $('#custom-test-alerts-placeholder').empty()
}

function enableTestElements() {
    $('#custom-test-button').prop('disabled', false)
    $('#custom-test-button').html('Test')
    $('#custom-input').prop('disabled', false)
    $('#custom-output').prop('disabled', false)
}

$('#custom-test-button').click(() => {
    disableTestElements()
    let payload = {
        problem_id: $('#problem-id').html(),
        code: $('#user-code').val(),
        language: $('#language-select').val(),
        inputs: [$('#custom-input').val()],
        time_limit: $('#time-limit').html(),
        memory_limit: $('#memory-limit').html()
    }
    fetch('/api/get-outputs',
    {
        method: 'POST',
        body: JSON.stringify(payload),
    })
        .then(response => response.json())
        .then(data => {
            let output = data[0]['output']
            let verdict = data[0]['verdict']
            let message = data[0]['message']
            if(verdict === "AC") {
                let time = parseFloat(data[0]['time'])/1000
                let memory = parseFloat(data[0]['memory'])/1024
                $('#custom-test-verdict').html(`OK (${time.toFixed(3)}s, ${memory.toFixed(3)}MB)`)
            } else {
                if(message) {
                $('#custom-test-verdict').html(
                    '<b style="color: red;">' + getLongVerdict(verdict) + '</b>' + 
                    ', see <a data-bs-toggle="modal" data-bs-target="#details-modal" href="#" class="text-decoration-none">details</a>')
                    $('#details-body').html(message)
                } else {
                    $('#custom-test-verdict').html(
                        '<b style="color: red;">' + getLongVerdict(verdict) + '</b>')
                }
            }
            $('#custom-output').val(output)
            enableTestElements()
        })
})

function resetSubmitButton() {
    $('#submitButton').prop('disabled', false)
    $('#submitButton').html('Submit')
}

function copy_text(element) {
    const text = element.innerText
    navigator.clipboard.writeText(text)
    const tooltip = bootstrap.Tooltip.getInstance(element)
    tooltip.show()
}

$('#codeForm').submit((e) => {
    e.preventDefault()
    $.ajax({
        url: $('#codeForm').attr('action'),
        type: 'post',
        data:$('#codeForm').serialize(),
        success: (data) => {
            addAttempt(data['submission_id'])
            makeRequest()
        },
        error: (data) => {alert('Error submitting code. Please try again. If this problem persists, please report bug.')}
    })
})

function getVerdictHTML(verdict) {
    switch (verdict) {
        case 'AC':
            return ['<span class="badge rounded-pill text-bg-success d-inline-flex align-items-center">',
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-circle" viewBox="0 0 16 16">',
                '<path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"></path>',
                '<path d="M10.97 4.97a.235.235 0 0 0-.02.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-1.071-1.05z"></path>',
                '</svg>',
                '&nbsp;<span class="verdict-long">' + getLongVerdict(verdict) + '</span>',
                '</span>'].join('')
                case 'WJ':
                    return ['<span class="badge rounded-pill text-bg-secondary d-inline-flex align-items-center">',
                '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-clockwise" viewBox="0 0 16 16">',
                '<path fill-rule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z"></path>',
                '<path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"></path>',
                '</svg>',
                '&nbsp;<span class="verdict-long">' + getLongVerdict(verdict) + '</span>',
                '</span>'].join('')
                default:
            return ['<span class="badge rounded-pill text-bg-danger d-inline-flex align-items-center">',
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle" viewBox="0 0 16 16">',
            '<path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"></path>',
            '<path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"></path>',
            '</svg>',
            '&nbsp;<span class="verdict-long">' + getLongVerdict(verdict) + '</span>',
            '</span>'].join('')
        }
}

function addAttempt(submissionID) {
    $('#attempts-table-body').prepend(
        '<tr class="d-flex" submission-id="' + submissionID + '">' +
        '<th scope="row" class="col-4">' + UTCNow() + '</th>' +
        '<td class="col-6 d-flex align-items-center verdict">' +
        getVerdictHTML('WJ') +
        '&nbsp;&nbsp;(<span class="tests-completed">0</span>&nbsp;/&nbsp;<span class="total-tests">?</span>)' +
        '</td>' +
        '<td class="col-2"> ' +
        '<a href="/submission/' + submissionID + '" class="text-decoration-none">Details</a>' +
        '</td>' +
        '</tr>'
        )
    }
    
    function makeRequest() {
        $('#attempts-table-body').children().each((index, element) => {
            if($(element).find('.verdict-long').text().includes('Waiting for Judge')) {
            let tests_completed = 0
            if($(element).find('.tests-completed').length > 0) {
                if($(element).find('.tests-completed').text() === '?') {
                    tests_completed = 0
                }
                else {
                    tests_completed = parseInt($(element).find('.tests-completed').text())
                }
            }
            let payload = {
                id: $(element).attr('submission-id'),
                tests_completed: tests_completed
            }
            
            // Long poll for submission change.
            fetch("/api/capture-submission-change",
            {
                method: "POST",
                    body: JSON.stringify(payload),
                })
                .then(response => response.json())
                .then(data => {
                    tests_completed = data['tests_completed']
                    $(element).find('.tests-completed').text(tests_completed)
                    $(element).find('.total-tests').text(data['results'].length)
                    if (data['final_verdict'] !== "WJ") {
                        $(element).find('.verdict').html(getVerdictHTML(data['final_verdict']))
                        resetSubmitButton()
                    } else {
                        setTimeout(makeRequest, 500)
                    }
                })
        }
    })
}

// Use `onpageshow` instead of `$(document).ready()` so this runs even when user gets here by back button.
window.onpageshow = function(event) {
    // Initialise code editor.
    let editor = ace.edit('editor')
    ace.config.set('basePath', 'https://cdn.jsdelivr.net/npm/ace-builds@1.13.1/src-noconflict/')
    editor.setTheme("ace/theme/textmate")
    editor.session.setMode("ace/mode/" + getAceMode($('#language-select').val()))
    editor.session.setUseWrapMode(true)
    editor.setOptions({maxLines: 25, minLines: 25})
    editor.getSession().on('change', () => {
        $('#user-code').val(editor.getValue())
    })
    // Initialise tooltips.
    $('[data-bs-toggle="tooltip"]').tooltip()
    $('[data-bs-toggle="tooltip"]').on('mouseleave', function () {
        $(this).tooltip('hide')
      })

    resetSubmitButton()

    $('#submitButton').click(function() {
        // Disable submit button.
        $(this).prop('disabled', true)
        // Replace text with a spinner.
        $(this).html(
            '<span class="spinner-border spinner-border-sm code-submit" role="status" aria-hidden="true"></span> Submitting...'
        )
        // Submit form.
        $('#codeForm').submit()
    })
    makeRequest()
}