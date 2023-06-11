problem_searcher = custom_searcher(['id', 'name', 'solves'])
submission_searcher = custom_searcher(['time', 'username', 'problem', 'language', 'verdict'])
assignment_searcher = custom_searcher(['time', 'creator', 'solved'])

window.onpageshow = () => {
    // Initialise code editor.
    if($('#editor').length > 0) {
        let editor = ace.edit('editor')
        ace.config.set('basePath', 'https://cdn.jsdelivr.net/npm/ace-builds@1.13.1/src-noconflict/')
        editor.setTheme("ace/theme/textmate")
        editor.session.setMode("ace/mode/python")
        editor.session.setUseWrapMode(true)
        editor.setOptions({ readOnly: true, highlightActiveLine: false, highlightGutterLine: false, maxLines: Infinity })
        editor.renderer.$cursorLayer.element.style.display = "none"
    }
}
