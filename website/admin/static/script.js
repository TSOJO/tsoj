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
    let answer_node = testcase_node.getElementsByClassName('testcase-answer')[0];
    answer_node.name = 'answer' + testcases_count;
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
        const placeholder = document.getElementById('alert-placeholder');
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
        console.log(input_node);
        input_node.name = input_node.name.slice(0, -1) + (i + 1);
        let answer_node = testcase_node.getElementsByClassName('testcase-answer')[0];
        answer_node.name = answer_node.name.slice(0, -1) + (i + 1);
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