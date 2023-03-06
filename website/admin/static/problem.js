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
    if (document.getElementById('generate-answer-checkbox').checked === true) {
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

function getAlert(message, i, withDetails, isGrader, type='danger') {
    let alert = document.createElement('div')
    let target = isGrader ? 'grader-detail' + i + '-modal' : 'detail' + i + '-modal'
    if (withDetails) {
        alert.innerHTML = [
            '<div class="alert alert-' + type + ' alert-dismissable d-flex justify-items-between align-items-center" role="alert">',
            '   <div class="flex-grow-1">' + message + '</div>',
            '   <div class="d-flex align-items-center" style="gap:10px;">',
            '       <a data-bs-toggle="modal" data-bs-target="#' + target + '" href="#" class="text-decoration-none">Details</a>',
            '       <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
            '   </div>',
            '</div>'
        ].join('')
    }
    else {
        alert.innerHTML = [
            '<div class="alert alert-' + type + ' alert-dismissable d-flex justify-items-between align-items-center" role="alert">',
            '   <div class="flex-grow-1">' + message + '</div>',
            '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
            '</div>'
        ].join('')
    }
    return alert
}

function getModal(message, i, isGrader, header='Error message') {
    let modal = document.createElement('div')
    let name = isGrader ? 'grader-detail' + i  : 'detail' + i 
    modal.innerHTML = [
        '<div class="modal fade" id="'+name+'-modal" tabindex="-1"',
        'aria-labelledby="'+name+'-modal-label" aria-hidden="true">',
        '    <div class="modal-dialog">',
        '        <div class="modal-content">',
        '            <div class="modal-header">',
        '                <h1 class="modal-title fs-5" id="'+name+'-modal-label">' + header,
        '                </h1>',
        '                <button type="button" class="btn-close" data-bs-dismiss="modal"',
        '                    aria-label="Close"></button>',
        '            </div>',
        '            <div class="modal-body">',
        '                <div style="white-space:pre-wrap;" class="consolas">',
                             message,
        '                </div>',
        '            </div>',
        '            <div class="modal-footer">',
        '                <button type="button" class="btn btn-secondary"',
        '                    data-bs-dismiss="modal">Close</button>',
        '            </div>',
        '        </div>',
        '    </div>',
        '</div>'
    ].join('')
    return modal
}

function disableTestcaseButtons() {
    $('#add-testcase-btn').prop('disabled', true)
    $('.remove-testcase-btn').each(function () {
        $(this).prop('disabled', true)
    })
}

function enableTestcaseButtons() {
    $('#add-testcase-btn').prop('disabled', false)
    $('.remove-testcase-btn').each(function () {
        $(this).prop('disabled', false)
    })
}

function generateAnswers() {
    // Disable buttons.
    disableTestcaseButtons()
    $('#gen-answer-button').prop('disabled', true)
    $('#gen-answer-button').html(
        '<span class="spinner-border spinner-border-sm code-submit" role="status" aria-hidden="true"></span> Generating answers...'
    )
    $('#gen-alert-placeholder').empty()
    var payload = {
        generator_code: $('#generator-code').val(),
        language: $('#language-select').val(),
        inputs: [...Array(testcases_count).keys()].map(i => $('#input' + (i + 1)).val()),
        time_limit: $('#time-limit').val(),
        memory_limit: $('#memory-limit').val()
    }

    const placeholder = document.getElementById('gen-alert-placeholder')
    fetch('/api/generate-answers',
        {
            method: 'POST',
            body: JSON.stringify(payload),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data)
            all_ok = true
            for(let [i, result] of Object.entries(data)) {
                let index = parseInt(i) + 1
                console.log(result)
                let verdict = result['verdict']
                if(verdict === 'AC') {
                    $('#answer' + index).val(result['answer'])
                } else {
                    let message = result['message']
                    if(message) {
                        $('#detail' + index + '-modal').remove()
                        all_ok = false
                        const alert = getAlert('Oops... ' + getLongVerdict(verdict)  + ' on Input ' + index, index, true, false)
                        const modal = getModal(message, index, false)
                        placeholder.append(modal)
                        placeholder.append(alert)
                    }
                    else {
                        const alert = getAlert('Oops... ' + getLongVerdict(verdict) + ' on Input ' + index, index, false, false)
                        placeholder.append(alert)
                    }
                }
            }
            if (Object.keys(data).length == testcases_count) {
                if(all_ok) {
                    const alert = getAlert('All answers generated successfully!', 0, false, false, 'success')
                    placeholder.append(alert)
                }
            }
            // Renable buttons.
            enableTestcaseButtons()
            $('#gen-answer-button').prop('disabled', false)
            $('#gen-answer-button').html('Generate answers')
        })
}

function testGrader() {
    // Disable buttons.
    disableTestcaseButtons()
    $('#test-grader-button').prop('disabled', true)
    $('#test-grader-button').html(
        '<span class="spinner-border spinner-border-sm code-submit" role="status" aria-hidden="true"></span> Testing grader...'
    )
    $('#grader-alert-placeholder').empty()
    var payload = {
        grader_code: $('#grader-code').val(),
        language: $('#grader-language-select').val(),
        inputs: [...Array(testcases_count).keys()].map(i => $('#input' + (i + 1)).val()),
        outputs: [...Array(testcases_count).keys()].map(i => $('#answer' + (i + 1)).val()),
        time_limit: $('#time-limit').val(),
        memory_limit: $('#memory-limit').val()
    }
    const placeholder = $('#grader-alert-placeholder')
    fetch('/api/test-grader',
        {
            method: 'POST',
            body: JSON.stringify(payload),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data)
            if (data['verdict'] !== 'AC') {
                let message = data['message']
                let index = data['index']
                let verdict = data['verdict']
                if (message) {
                    $('#grader-detail' + index + '-modal').remove()
                    const alert = getAlert('Oops... Grader ' + getLongVerdict(verdict) + ' on testcase ' + index, index, true, true)
                    const modal = getModal(message, index, true)
                    placeholder.append(modal)
                    placeholder.append(alert)
                }
                else {
                    const alert = getAlertHTML('Oops... Grader ' + getLongVerdict(verdict) + ' on testcase ' + index, index, false, true)
                    placeholder.append(alert)
                }
            } else {
                const alert = getAlert('All testcases passed with grader!', 0, false, true, 'success')
                placeholder.append(alert)
            }
            // Renable buttons.
            enableTestcaseButtons()
            $('#test-grader-button').prop('disabled', false)
            $('#test-grader-button').html('Test grader')
        })
}

$('#language-select').change(() => {
    let editor = ace.edit('editor')
    editor.session.setMode("ace/mode/" + getAceMode($('#language-select').val()))
})

$('#grader-language-select').change(() => {
    let editor = ace.edit('grader-editor')
    editor.session.setMode("ace/mode/" + getAceMode($('#grader-language-select').val()))
})

function judgeMethodOnChange() {
    switch ($('#judge-method-select').val()) {
        case 'compare-output':
            $('#grader-div').hide()
            break
        case 'grader':
            $('#grader-div').show()
            break
    }
}
$('#judge-method-select').change(judgeMethodOnChange)

function restrictLangOnChange() {
    if ($('#restrict-langs').is(':checked')) {
        $('#allowed-languages-wrapper').show()
    } else {
        $('#allowed-languages-wrapper').hide()
    }
}
$('#restrict-langs').change(restrictLangOnChange)

function aqaAddressesOnChange() {
    if ($('#AQAASM').is(':selected')) {
        $('#aqa-addresses-wrapper').show()
    } else {
        $('#aqa-addresses-wrapper').hide()
    }
}
$('#allowed-languages').change(aqaAddressesOnChange)

window.onpageshow = function (event) {
    if (testcases_count === 0) {
        add_field()
    }

    // Initialise code editor.
    ace.config.set('basePath', 'https://cdn.jsdelivr.net/npm/ace-builds@1.13.1/src-noconflict/')
    let editor = ace.edit('editor')
    editor.setTheme('ace/theme/textmate')
    editor.session.setMode('ace/mode/' + getAceMode($('#language-select').val()))
    editor.setOptions({ minLines: 10, maxLines: 20 })
    // editor.session.setUseWrapMode(true)
    editor.getSession().on('change', function () {
        $('textarea[name="generator-code"]').val(editor.getValue())
    })

    // Initialise grader code editor.
    let grader_editor = ace.edit('grader-editor')
    grader_editor.setTheme('ace/theme/textmate')
    grader_editor.session.setMode('ace/mode/' + getAceMode($('#grader-language-select').val()))
    grader_editor.setOptions({ minLines: 10, maxLines: 20 })
    // grader_editor.session.setUseWrapMode(true)
    grader_editor.getSession().on('change', function () {
        $('textarea[name="grader-code"]').val(grader_editor.getValue())
    })
    $('textarea[name="grader-code"]').val(grader_editor.getValue())
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

$(document).ready(() => {
    judgeMethodOnChange()
    restrictLangOnChange()
    aqaAddressesOnChange()
})

$('#description').on('input', function (e) {
    $('#description-md')[0].mdContent = $('#description').val()
})