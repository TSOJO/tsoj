setInterval("MathJax.typeset()", 100)

function getAceMode(languageName) {
    switch (languageName) {
        case "CPLUSPLUS":
            return "c_cpp";
        case "PYTHON":
            return "python";
        default:
            return "text";
    }
}

async function validate_id() {
    const response = await fetch('/api/db/problem/' + id_field.value,
        {
            method: 'HEAD',
        })
    const status = response['status']
    if (status === 200) {
        id_field.setCustomValidity('A problem with that ID already exists.')
        id_invalid_feedback.innerText = 'A problem with that ID already exists.'
    } else {
        id_field.setCustomValidity('')
        id_invalid_feedback.innerText = 'This field is required.'
    }
}

// Form validation. (https://getbootstrap.com/docs/5.2/forms/validation/)
(() => {
    'use strict'

    const form = document.querySelector('.needs-id-validation')
    form.addEventListener('submit', async event => {
        // You cannot use preventDefault() after await.
        event.preventDefault()
        event.stopPropagation()
        await validate_id()
        if (form.checkValidity()) {
            form.submit()
        }
        form.classList.add('was-validated')
    }, false)
})()

const id_field = document.getElementById('problem_id')
const id_invalid_feedback = document.getElementById('id-invalid-feedback')
id_field.addEventListener('blur', () => {
    validate_id()
})