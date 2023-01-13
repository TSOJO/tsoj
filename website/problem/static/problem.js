// Use `onpageshow` instead of `$(document).ready()` so this runs even when user gets here by back button.
window.onpageshow = function(event) {
    // Initialise code editor.
    let editor = ace.edit('editor');
    ace.config.set('basePath', 'https://cdn.jsdelivr.net/npm/ace-builds@1.13.1/src-noconflict/');
    editor.setTheme("ace/theme/textmate");
    editor.session.setMode("ace/mode/python");
    editor.session.setUseWrapMode(true);
    editor.setOptions({maxLines: 25, minLines: 25});
    let textarea = $('textarea[name="user_code"]').hide();

    // Reset submit button. Is there a better way to do this?
    $('#submitButton').prop('disabled', false);
    $('#submitButton').html('Submit');

    $('#submitButton').click(function() {
        textarea.val(editor.getValue());
        // Disable submit button.
        $(this).prop('disabled', true);
        // Replace text with a spinner.
        $(this).html(
            '<span class="spinner-border spinner-border-sm code-submit" role="status" aria-hidden="true"></span> Running...'
        );
        // Submit form.
        $('#codeForm').submit();
    });
}

function copy_text(element) {
    const text = element.innerText;
    navigator.clipboard.writeText(text);
}