let testcases_count = $('#testcases-count').val();

function add_field() {
    testcases_count++;
    $('#testcases-count').val(testcases_count);
    let testcase_node = document.getElementById('testcase-div').cloneNode(true);
    testcase_node.id = '';
    testcase_node.style.display = 'block';
    let h5_node = testcase_node.getElementsByClassName('testcase-number')[0];
    h5_node.innerHTML = 'Testcase ' + testcases_count;
    let input_node = testcase_node.getElementsByClassName('testcase-input')[0];
    input_node.name = 'input' + testcases_count;
    input_node.id = 'input' + testcases_count;
    let answer_node = testcase_node.getElementsByClassName('testcase-answer')[0];
    answer_node.name = 'answer' + testcases_count;
    answer_node.id = 'answer' + testcases_count;
    if (document.getElementById('auto-generate-answer-checkbox').checked == true) {
        answer_node.readOnly = true;
    }
    let testcase_container = document.getElementById('testcase-container');
    // input_node.setAttribute('required', '');
    // answer_node.setAttribute('required', '');
    testcase_container.appendChild(testcase_node);
}

function remove_field(node) {
    if (testcases_count == 1) {
        const wrapper = document.createElement('div');
        wrapper.innerHTML = [
            '<div class="alert alert-danger alert-dismissable d-flex justify-items-between align-items-center" role="alert">',
            '   <div class="flex-grow-1">At least one testcase is required!</div>',
            '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
            '</div>'
        ].join('');
        const placeholder = document.getElementById('rem-alert-placeholder');
        placeholder.append(wrapper);
        return;
    }
    testcases_count--;
    $('#testcases-count').val(testcases_count);
    let testcase_container = document.getElementById('testcase-container');
    testcase_container.removeChild(node);
    // reindex
    for (let i = 0; i < testcases_count; i++) {
        let testcase_node = testcase_container.childNodes[i];
        let h5_node = testcase_node.getElementsByClassName('testcase-number')[0];
        h5_node.innerHTML = 'Testcase ' + (i + 1);
        let input_node = testcase_node.getElementsByClassName('testcase-input')[0];
        input_node.name = input_node.name.slice(0, -1) + (i + 1);
        input_node.id = input_node.id.slice(0, -1) + (i + 1);
        let answer_node = testcase_node.getElementsByClassName('testcase-answer')[0];
        answer_node.name = answer_node.name.slice(0, -1) + (i + 1);
        answer_node.id = answer_node.id.slice(0, -1) + (i + 1);
    }
}

function generate_answers() {
    for (let i = 1; i <= testcases_count; i++) {
        var payload = {
            generatorCode: $('#generator-code').val(),
            input: $('#input' + i).val(),
            timeLimit: $('#time-limit').val(),
            memoryLimit: $('#memory-limit').val()
        };

        const placeholder = document.getElementById('gen-alert-placeholder');
        fetch("/api/generate-answer",
            {
                method: "POST",
                body: JSON.stringify(payload),
            })
            .then(response => response.json())
            .then(data => {
                if (data['verdict'].verdict == 'AC') {
                    $('#answer' + i).val(data['answer']);
                } else {
                    const wrapper = document.createElement('div');
                    wrapper.innerHTML = [
                        '<div class="alert alert-danger alert-dismissable d-flex justify-items-between align-items-center mt-3" role="alert">',
                        '   <div class="flex-grow-1">Oops... ' + data['verdict'].verdict_long + ' on Input ' + i + '</div>',
                        '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
                        '</div>'
                    ].join('');
                    placeholder.append(wrapper);
                }
            })
    }
}

// Form validation. (https://getbootstrap.com/docs/5.2/forms/validation/)
(() => {
    'use strict'
    
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    const forms = document.querySelectorAll('.needs-validation')
    
    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()
            }

            form.classList.add('was-validated')
        }, false)
    })
})()

window.onpageshow = function (event) {
    if (testcases_count == 0) {
        add_field()
    }

    // Initialise code editor.
    let editor = ace.edit('editor');
    ace.config.set('basePath', 'https://cdn.jsdelivr.net/npm/ace-builds@1.13.1/src-noconflict/');
    editor.setTheme("ace/theme/textmate");
    editor.session.setMode("ace/mode/python");
    editor.setOptions({ minLines: 10, maxLines: 20 });
    // editor.session.setUseWrapMode(true);
    
    editor.getSession().on('change', function () {
        $('textarea[name="generator-code"]').val(editor.getValue());
    });
    
    // Checkbox on changed
    $('input[name="generator-checkbox"]').change(function () {
        if (this.checked) {
            $('#editor-group').show();
        } else {
            $('#editor-group').hide();
        }
        for (let i = 1; i <= testcases_count; i++) {
            if (this.checked == true) {
                document.getElementById('answer' + i).value = 'Press "Generate answers" to generate answers.';
                document.getElementById('answer' + i).disabled = true;
            } else {
                if (document.getElementById('answer' + i).value == 'Press "Generate answers" to generate answers.') {
                    document.getElementById('answer' + i).value = '';
                }
                document.getElementById('answer' + i).disabled = false;
            }
        }
    });
}