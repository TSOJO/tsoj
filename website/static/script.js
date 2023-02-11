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