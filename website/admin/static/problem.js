let testcases_count = parseInt($('#testcases-count').val())

function add_field() {
    testcases_count++
    $('#testcases-count').val(testcases_count)
    let testcase_node = document.getElementById('testcase-div').cloneNode(true)
    testcase_node.id = ''
    testcase_node.style.display = 'block'
    let h5_node = testcase_node.getElementsByClassName('testcase-number')[0]
    h5_node.innerHTML = 'Testcase ' + testcases_count
    let input_node = testcase_node.getElementsByClassName('testcase-input')[0]
    input_node.name = 'input' + testcases_count
    input_node.id = 'input' + testcases_count
    let answer_node = testcase_node.getElementsByClassName('testcase-answer')[0]
    answer_node.name = 'answer' + testcases_count
    answer_node.id = 'answer' + testcases_count
    let sample_checkbox = testcase_node.getElementsByClassName('testcase-sample')[0]
    sample_checkbox.name = 'sample' + testcases_count
    sample_checkbox.id = 'sample' + testcases_count
    if (document.getElementById('auto-generate-answer-checkbox').checked === true) {
        answer_node.innerHTML = 'Press "Generate answers" to generate answers.'
        answer_node.readOnly = true
    }
    let testcase_container = document.getElementById('testcase-container')
    testcase_container.appendChild(testcase_node)
}

function remove_field(node) {
    if (testcases_count === 1) {
        const wrapper = document.createElement('div')
        wrapper.innerHTML = [
            '<div class="alert alert-danger alert-dismissable d-flex justify-items-between align-items-center" role="alert">',
            '   <div class="flex-grow-1">At least one testcase is required!</div>',
            '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
            '</div>'
        ].join('')
        const placeholder = document.getElementById('rem-alert-placeholder')
        placeholder.append(wrapper)
        return
    }
    testcases_count--
    $('#testcases-count').val(testcases_count)
    let testcase_container = document.getElementById('testcase-container')
    testcase_container.removeChild(node)
    // reindex
    for (let i = 0; i < testcases_count; i++) {
        let testcase_node = testcase_container.childNodes[i]
        let h5_node = testcase_node.getElementsByClassName('testcase-number')[0]
        h5_node.innerHTML = 'Testcase ' + (i + 1)
        let input_node = testcase_node.getElementsByClassName('testcase-input')[0]
        input_node.name = input_node.name.slice(0, -1) + (i + 1)
        input_node.id = input_node.id.slice(0, -1) + (i + 1)
        let answer_node = testcase_node.getElementsByClassName('testcase-answer')[0]
        answer_node.name = answer_node.name.slice(0, -1) + (i + 1)
        answer_node.id = answer_node.id.slice(0, -1) + (i + 1)
        let sample_checkbox = testcase_node.getElementsByClassName('testcase-sample')[0]
        sample_checkbox.name = sample_checkbox.name.slice(0, -1) + (i + 1)
        sample_checkbox.id = sample_checkbox.id.slice(0, -1) + (i + 1)
    }
}

let completed_requests = 0

function generate_answers() {
    // Disable buttons.
    $('#add-testcase-btn').prop('disabled', true)
    $('.remove-testcase-btn').each(function () {
        $(this).prop('disabled', true)
    })
    $('#gen-answer-button').prop('disabled', true)
    $('#gen-answer-button').html(
        '<span class="spinner-border spinner-border-sm code-submit" role="status" aria-hidden="true"></span> Generating answers... (0/' + testcases_count + ')'
    )
    for (let i = 1; i <= testcases_count; i++) {
        var payload = {
            generatorCode: $('#generator-code').val(),
            input: $('#input' + i).val(),
            timeLimit: $('#time-limit').val(),
            memoryLimit: $('#memory-limit').val()
        }

        const placeholder = document.getElementById('gen-alert-placeholder')
        fetch('/api/generate-answer',
            {
                method: 'POST',
                body: JSON.stringify(payload),
            })
            .then(response => response.json())
            .then(data => {
                if (data['verdict'].verdict === 'AC') {
                    $('#answer' + i).val(data['answer'])
                } else {
                    const wrapper = document.createElement('div')
                    let message = data['message']
                    if (message) {
                        wrapper.innerHTML = [
                            '<div class="alert alert-danger alert-dismissable d-flex justify-items-between align-items-center mt-3" role="alert">',
                            '   <div class="flex-grow-1">Oops... ' + data['verdict'].verdict_long + ' on Input ' + i + '</div>',
                            '   <div>',
                            '       <a data-bs-toggle="modal" data-bs-target="#detail' + i + '-modal" href="#" class="text-decoration-none">Details</a>',
                            '       <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
                            '   </div>',
                            '</div>'
                        ].join('')
                        const modal = document.createElement('div')
                        modal.innerHTML = [
                            '<div class="modal fade" id="detail'+i+'-modal" tabindex="-1"',
                            'aria-labelledby="detail'+i+'-modal-label" aria-hidden="true">',
                            '    <div class="modal-dialog">',
                            '        <div class="modal-content">',
                            '            <div class="modal-header">',
                            '                <h1 class="modal-title fs-5" id="detail'+i+'-modal-label">Error message',
                            '                </h1>',
                            '                <button type="button" class="btn-close" data-bs-dismiss="modal"',
                            '                    aria-label="Close"></button>',
                            '            </div>',
                            '            <div class="modal-body">',
                            '                <div style="white-space:pre-wrap;" class="consolas">',
                            '                    '+message+'',
                            '                </div>',
                            '            </div>',
                            '            <div class="modal-footer">',
                            '                <button type="button" class="btn btn-secondary"',
                            '                    data-bs-dismiss="modal">Close</button>',
                            '            </div>',
                            '        </div>',
                            '    </div>',
                            '</div>',].join('')
                        placeholder.append(modal)
                        placeholder.append(wrapper)
                    }
                    else {
                        wrapper.innerHTML = [
                            '<div class="alert alert-danger alert-dismissable d-flex justify-items-between align-items-center mt-3" role="alert">',
                            '   <div class="flex-grow-1">Oops... ' + data['verdict'].verdict_long + ' on Input ' + i + message + '</div>',
                            '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
                            '</div>'
                        ].join('')
                        placeholder.append(wrapper)
                    }
                }
                completed_requests++
                $('#gen-answer-button').html(
                    '<span class="spinner-border spinner-border-sm code-submit" role="status" aria-hidden="true"></span> Generating answers... (' + completed_requests + '/' + testcases_count + ')'
                )
                if (completed_requests == testcases_count) {
                    // All requests done.
                    // Renable buttons.
                    $('#add-testcase-btn').prop('disabled', false)
                    $('.remove-testcase-btn').each(function () {
                        $(this).prop('disabled', false)
                    })
                    $('#gen-answer-button').prop('disabled', false)
                    $('#gen-answer-button').html(
                        'Generate answers'
                    )
                    completed_requests = 0
                }
            })
    }
}

// Form validation. (https://getbootstrap.com/docs/5.2/forms/validation/)
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

const id_field = document.getElementById('id')
const id_invalid_feedback = document.getElementById('id-invalid-feedback')
id_field.addEventListener('blur', () => {
    fetch('/api/db/problem/' + id_field.value,
        {
            method: 'HEAD',
        })
        .then(response => response['status'])
        .then(status => {
            if (status === 200) {
                id_field.setCustomValidity('A problem with that ID already exists.')
                id_invalid_feedback.innerText = 'A problem with that ID already exists.'
            } else {
                id_field.setCustomValidity('')
                id_invalid_feedback.innerText = 'This field is required.'
            }
        })
})


window.onpageshow = function (event) {
    if (testcases_count === 0) {
        add_field()
    }

    // Initialise code editor.
    let editor = ace.edit('editor')
    ace.config.set('basePath', 'https://cdn.jsdelivr.net/npm/ace-builds@1.13.1/src-noconflict/')
    editor.setTheme('ace/theme/textmate')
    editor.session.setMode('ace/mode/python')
    editor.setOptions({ minLines: 10, maxLines: 20 })
    // editor.session.setUseWrapMode(true)

    editor.getSession().on('change', function () {
        $('textarea[name="generator-code"]').val(editor.getValue())
    })

    $('#description-md')[0].mdContent = $('#description').val()

    // Checkbox on changed
    $('input[name="generator-checkbox"]').change(function () {
        if (this.checked) {
            $('#editor-group').show()
        } else {
            $('#editor-group').hide()
        }
        for (let i = 1; i <= testcases_count; i++) {
            if (this.checked === true) {
                document.getElementById('answer' + i).value = 'Press "Generate answers" to generate answers.'
                document.getElementById('answer' + i).readOnly = true
            } else {
                if (document.getElementById('answer' + i).value === 'Press "Generate answers" to generate answers.') {
                    document.getElementById('answer' + i).value = ''
                }
                document.getElementById('answer' + i).readOnly = false
            }
        }
    })
}

$('#description').on('input', function (e) {
    $('#description-md')[0].mdContent = $('#description').val()
})