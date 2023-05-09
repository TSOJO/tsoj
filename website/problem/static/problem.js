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

    // Reset submit button. Is there a better way to do this?
    $('#submitButton').prop('disabled', false)
    $('#submitButton').html('Submit')

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
}

function copy_text(element) {
    const text = element.innerText
    navigator.clipboard.writeText(text)
    const tooltip = bootstrap.Tooltip.getInstance(element)
    tooltip.show()
}