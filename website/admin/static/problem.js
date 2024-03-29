let testcases_count = parseInt($('#testcases-count').val())
let currentTestcaseIndex = 0

function getTestcaseButton(index) {
    let button = document.createElement('button')
    button.innerHTML = 'Testcase ' + (index+1)
    button.setAttribute('id', 'testcase-button' + index)
    button.setAttribute('class', 'btn btn-light')
    button.setAttribute('style', 'width:100%;')
    button.setAttribute('type', 'button')
    button.setAttribute('onclick', 'selectTestcase(' + index + ')')
    return button
}

function selectTestcase(index) {
    currentTestcaseIndex = index
    for (let i = 0; i < testcases_count; i++) {
        $('#testcase-button' + i).attr('class', 'btn btn-light')
        $('#testcase-group' + i).css('display', 'none')
    }
    $('#testcase-button' + index).attr('class', 'btn btn-primary')
    $('#testcase-group' + index).css('display', 'block')
}

function getTestcaseGroup(index) {
    let group = document.createElement('div')
    group.innerHTML = [
        '<div id="testcase-group' + index + '" style="display: none;">',
        '<div class="d-flex justify-content-between">',
        '    <div>',
        '        <h5 id="testcase-number' + index + '">Testcase ' + (index+1) + '</h5>',
        '    </div>',
        '    <div>',
        '        <input class="form-check-input" type="checkbox" value="" name="example' + index + '" id="example' + index + '" onclick="exampleTestcaseOnChange(this)"/>',
        '        <label class="form-check-label">Example testcase</label>',
        '    </div>',
        '</div>',
        '<div class="form-group mb-3">',
        '    <label class="form-label">Batch number</label>',
        '    <input class="form-control testcase-batch-number" type="number" min="1" name="batch_number' + index + '" id="batch_number' + index + '"',
        '        value="1"/>',
        '</div>',
        '<label class="form-label" for="input' + index + '">',
            'Input',
        '</label>',
        '<textarea class="form-control testcase-input mb-2" rows="3" id="input' + index + '"',
        '    name="input' + index + '"></textarea>',
        '<label class="form-label" for="answer' + index + '">',
            'Answer',
        '</label>',
        '<textarea class="form-control testcase-answer" rows="3" id="answer' + index + '"',
        '    name="answer' + index + '"></textarea>',
        '</div>',
    ].join('')
    return group
}

const testcases_buttons_container = $('#testcases-buttons-container')
function createTestcase() {
    testcases_buttons_container.append(getTestcaseButton(testcases_count))
    testcases_count++
    $('#testcases-count').val(testcases_count)
    $('#testcase-groups-container').append(getTestcaseGroup(testcases_count-1))
}

function deleteTestcase() {
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
    $('#testcases-count').val(testcases_count)
    $('#testcase-button' + currentTestcaseIndex).remove()
    $('#testcase-group' + currentTestcaseIndex).remove()
    // reindex
    for (let i = currentTestcaseIndex+1; i < testcases_count; i++) {
        $('#testcase-button' + i).attr('onclick', 'selectTestcase(' + (i-1) + ')')
        $('#testcase-button' + i).html('Testcase ' + i)
        $('#testcase-button' + i).attr('id', 'testcase-button' + (i-1))
        $('#testcase-group' + i).attr('id', 'testcase-group' + (i-1))
        $('#input' + i).attr('name', 'input' + (i-1))
        $('#input' + i).attr('id', 'input' + (i-1))
        $('#answer' + i).attr('name', 'answer' + (i-1))
        $('#answer' + i).attr('id', 'answer' + (i-1))
        $('#example' + i).attr('name', 'example' + (i-1))
        $('#example' + i).attr('id', 'example' + (i-1))
        $('#batch_number' + i).attr('name', 'batch_number' + (i-1))
        $('#batch_number' + i).attr('id', 'batch_number' + (i-1))
        $('#testcase-number' + i).html('Testcase ' + i)
        $('#testcase-number' + i).attr('id', 'testcase-number' + (i-1))
    }
    testcases_count--
    if (currentTestcaseIndex === testcases_count) {
        currentTestcaseIndex--
    }
    selectTestcase(currentTestcaseIndex)
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

function generateInputs() {
    disableTestcaseButtons()
    $('#gen-input-button').prop('disabled', true)
    $('#gen-input-button').html(
        '<span class="spinner-border spinner-border-sm code-submit" role="status" aria-hidden="true"></span> Generating inputs...'
    )
    $('#input-gen-alert-placeholder').empty()

    let testcaseIndicies = []
    for (let i = 0; i < testcases_count; ++i) {
        if ($('#batch_number' + i).val() == $('#generate-input-batch-number').val()) {
            testcaseIndicies.push(i)
        }
    }

    let payload = {
        code: $('#input-generator-code').val(),
        language: $('#input-language-select').val(),
        inputs: testcaseIndicies.map(i => ''),
        time_limit: $('#time-limit').val(),
        memory_limit: $('#memory-limit').val()
    }

    const placeholder = document.getElementById('input-gen-alert-placeholder')
    fetch('/api/get-outputs',
        {
            method: 'POST',
            body: JSON.stringify(payload),
        })
        .then(response => response.json())
        .then(data => {
            all_ok = true
            for(let [i, result] of Object.entries(data)) {
                let index = testcaseIndicies[parseInt(i)]
                let verdict = result['verdict']
                if(verdict === 'AC') {
                    if(result['output'].length > 4000) {
                        all_ok = false
                        const alert = getAlert('Input exceeded 4000 characters on testcase ' + (index+1), index, false, false)
                        placeholder.append(alert)
                    } else {
                        $('#input' + index).val(result['output'])
                    }
                } else {
                    let message = result['message']
                    if(message) {
                        $('#detail' + index + '-modal').remove()
                        all_ok = false
                        const alert = getAlert('Oops... ' + getLongVerdict(verdict)  + ' on testcase ' + (index+1), index, true, false)
                        const modal = getModal(message, index, false)
                        placeholder.append(modal)
                        placeholder.append(alert)
                    }
                    else {
                        const alert = getAlert('Oops... ' + getLongVerdict(verdict) + ' on testcase ' + (index+1), index, false, false)
                        placeholder.append(alert)
                    }
                }
            }
            if (Object.keys(data).length == testcases_count) {
                if(all_ok) {
                    const alert = getAlert('All inputs generated successfully!', 0, false, false, 'success')
                    placeholder.append(alert)
                }
            }
            // Renable buttons.
            enableTestcaseButtons()
            $('#gen-input-button').prop('disabled', false)
            $('#gen-input-button').html('Generate inputs')
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
    let payload = {
        code: $('#generator-code').val(),
        language: $('#language-select').val(),
        inputs: [...Array(testcases_count).keys()].map(i => $('#input' + i).val()),
        time_limit: $('#time-limit').val(),
        memory_limit: $('#memory-limit').val()
    }

    const placeholder = document.getElementById('gen-alert-placeholder')
    fetch('/api/get-outputs',
        {
            method: 'POST',
            body: JSON.stringify(payload),
        })
        .then(response => response.json())
        .then(data => {
            all_ok = true
            for(let [i, result] of Object.entries(data)) {
                let index = parseInt(i)
                let verdict = result['verdict']
                if(verdict === 'AC') {
                    if(result['output'].length > 4000) {
                        all_ok = false
                        const alert = getAlert('Output exceeded 4000 characters on testcase ' + (index+1), index, false, false)
                        placeholder.append(alert)
                    } else {
                        $('#answer' + index).val(result['output'])
                    }
                } else {
                    let message = result['message']
                    if(message) {
                        $('#detail' + index + '-modal').remove()
                        all_ok = false
                        const alert = getAlert('Oops... ' + getLongVerdict(verdict)  + ' on testcase ' + (index+1), index, true, false)
                        const modal = getModal(message, index, false)
                        placeholder.append(modal)
                        placeholder.append(alert)
                    }
                    else {
                        const alert = getAlert('Oops... ' + getLongVerdict(verdict) + ' on testcase ' + (index+1), index, false, false)
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
    let payload = {
        grader_code: $('#grader-code').val(),
        language: $('#grader-language-select').val(),
        inputs: [...Array(testcases_count).keys()].map(i => $('#input' + i).val()),
        outputs: [...Array(testcases_count).keys()].map(i => $('#answer' + i).val()),
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
    if ($('#AQAASM').is(':selected') || !($('#restrict-langs').is(':checked'))) {
        $('#aqa-addresses-wrapper').show()
    } else {
        $('#aqa-addresses-wrapper').hide()
    }
}
$('#allowed-languages').change(aqaAddressesOnChange)
$('#restrict-langs').change(aqaAddressesOnChange)

function generatorCheckboxOnChange() {
    if ($('#generate-answer-checkbox').is(':checked')) {
        $('#editor-group').show()
    } else {
        $('#editor-group').hide()
    }
}
$('#generate-answer-checkbox').change(generatorCheckboxOnChange)

function inputGeneratorCheckboxOnChange() {
    if ($('#generate-input-checkbox').is(':checked')) {
        $('#input-editor-group').show()
    } else {
        $('#input-editor-group').hide()
    }
}
$('#generate-input-checkbox').change(inputGeneratorCheckboxOnChange)

function exampleTestcaseOnChange(self) {
    if($(self).is(':checked')) {
        // set batch number to 0 and disable it
        $(self).parent().parent().parent().find('input.testcase-batch-number').val(0)
        $(self).parent().parent().parent().find('input.testcase-batch-number').prop('disabled', true)
    } else {
        $(self).parent().parent().parent().find('input.testcase-batch-number').val(1)
        $(self).parent().parent().parent().find('input.testcase-batch-number').prop('disabled', false)
    }
}

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
    $('textarea[name="generator-code"]').val(editor.getValue())
    editor.getSession().on('change', function () {
        $('textarea[name="generator-code"]').val(editor.getValue())
    })

    // Initialise input generator code editor.
    ace.config.set('basePath', 'https://cdn.jsdelivr.net/npm/ace-builds@1.13.1/src-noconflict/')
    let input_editor = ace.edit('input-editor')
    input_editor.setTheme('ace/theme/textmate')
    input_editor.session.setMode('ace/mode/' + getAceMode($('#input-language-select').val()))
    input_editor.setOptions({ minLines: 10, maxLines: 20 })
    // input_editor.session.setUseWrapMode(true)
    $('textarea[name="input-generator-code"]').val(input_editor.getValue())
    input_editor.getSession().on('change', function () {
        $('textarea[name="input-generator-code"]').val(input_editor.getValue())
    })

    // Initialise grader code editor.
    let grader_editor = ace.edit('grader-editor')
    grader_editor.setTheme('ace/theme/textmate')
    grader_editor.session.setMode('ace/mode/' + getAceMode($('#grader-language-select').val()))
    grader_editor.setOptions({ minLines: 10, maxLines: 20 })
    // grader_editor.session.setUseWrapMode(true)
    $('textarea[name="grader-code"]').val(grader_editor.getValue())
    grader_editor.getSession().on('change', function () {
        $('textarea[name="grader-code"]').val(grader_editor.getValue())
    })
    $('textarea[name="grader-code"]').val(grader_editor.getValue())
    $('#description-md')[0].mdContent = $('#description').val()
}

$(document).ready(() => {
    judgeMethodOnChange()
    restrictLangOnChange()
    aqaAddressesOnChange()
    selectTestcase(0)
})

$('#description').on('input', function (e) {
    $('#description-md')[0].mdContent = $('#description').val()
})

function testcaseTypeOnChange() {
    if ($('#testcase-type-select').val() === 'manual') {
        $('#testcase-manual-div').show()
        $('#testcase-file-div').hide()
    } else {
        $('#testcase-manual-div').hide()
        $('#testcase-file-div').show()
    }
}
testcaseTypeOnChange()
$('#testcase-type-select').change(testcaseTypeOnChange)