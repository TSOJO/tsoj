// Use `onpageshow` instead of `$(document).ready()` so this runs even when user gets here by back button.
window.onpageshow = function(event) {
    // Reset button. Is there a better way to do this?
    $('#submitButton').prop('disabled', false);
    $('#submitButton').html('Submit');
    
    $('#submitButton').click(function() {
        // Disable submit button.
        $(this).prop('disabled', true);
        // Replace text with a spinner.
        $(this).html(
            '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Running...'
        );
        // Submit form.
        $('#codeForm').submit();
    });
}
