/* create_problem.html */
let testcases_count = 0

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
        let h5_node = testcase_node.getElementsByTagName('h5')[0];
        h5_node.innerHTML = 'Testcase ' + (i + 1);
        let input_node = testcase_node.getElementsByClassName('testcase-input')[0];
        // console.log(input_node);
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
                if (data['verdict'] == 'AC') {
                    $('#answer' + i).val(data['answer']);
                } else {
                    const wrapper = document.createElement('div');
                    wrapper.innerHTML = [
                        '<div class="alert alert-danger alert-dismissable d-flex justify-items-between align-items-center mt-3" role="alert">',
                        '   <div class="flex-grow-1">Oops... ' + data['verdict'] + ' on Input ' + i + '</div>',
                        '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
                        '</div>'
                    ].join('');
                    placeholder.append(wrapper);
                }
            })
    }
}

function readonly_inputs(box) {
    for (let i = 1; i <= testcases_count; i++) {
        if (box.checked == true) {
            document.getElementById('answer' + i).readOnly = true;
        } else {
            document.getElementById('answer' + i).readOnly = false;
        }
    }
}

/* create_assignment.html */
let problems_count = 0

function add_problem() {
    problems_count++;
    let this_id = 'problem' + problems_count;
    var selected_problem_id = $('#problem-selector').val();
    const container = document.getElementById('problem-container');
    const wrapper = document.createElement('div');
    wrapper.setAttribute('id', this_id);
    wrapper.innerHTML = [
        '<div class="card mb-3" aria-hidden="true">',
        '   <div class="card-body">',
        '       <h5 class="card-title placeholder-glow">',
        '           <span class="placeholder col-3"></span>',
        '       </h5>',
        '       <p class="card-text placeholder-glow">',
        '           <span class="placeholder col-7"></span>',
        '       </p>',
        '       <a href="#" tabindex="-1" class="btn btn-primary disabled placeholder col-1"></a>',
        '       <button type="button" class="btn btn-danger disabled placeholder col-1"></button>',
        '   </div>',
        '</div>'
    ].join('');
    container.append(wrapper);
    fetch('/api/problem/' + selected_problem_id)
        .then(response => response.json())
        .then(data => {
            document.getElementById(this_id).remove();
            const wrapper_new = document.createElement('div');
            wrapper_new.setAttribute('id', this_id);
            wrapper_new.innerHTML = [
                '<div class="card mb-3" aria-hidden="true">',
                '   <div class="card-body">',
                '       <h5 class="card-title">',
                '           ' + data['id'] + ': ' + data['name'],
                '       </h5>',
                '       <p class="card-text">',
                '           ' + data['description'],
                '       </p>',
                '       <a href="/problem/' + data['id'] + '" class="btn btn-primary">View</a>',
                '       <button type="button" class="btn btn-danger" onclick="remove_problem(\'' + this_id + '\')">Remove</button>',
                '   </div>',
                '</div>',
                '<input type="hidden" name="' + this_id + '" value="' + data['id'] + '" />'
            ].join('');
            container.append(wrapper_new);
        })
}

function remove_problem(id) {
    document.getElementById(id).remove();
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
    if ($('div#create-problem-page').length > 0) {
        /* create_problem.html */
        if (testcases_count == 0) {
            add_field()
        }
    
        // Initialise code editor.
        let editor = ace.edit('editor');
        ace.config.set('basePath', 'https://cdn.jsdelivr.net/npm/ace-builds@1.13.1/src-noconflict/');
        editor.setTheme("ace/theme/textmate");
        editor.session.setMode("ace/mode/python");
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
        });
    }
}