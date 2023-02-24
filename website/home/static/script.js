function contains(object, keys, text) {
    lowered_text = text.toLowerCase()
    for (const key of keys) {
        if (object[key].toString().toLowerCase().includes(lowered_text)) {
            return true
        }
    }
    return false
}

function problem_searcher(data, text) {
    return data.filter(row => {
        return contains(row._data, ['id', 'name', 'solves'], text)
    })
}

function submission_searcher(data, text) {
    return data.filter(row => {
        return contains(row._data, ['time', 'username', 'problem', 'language', 'verdict'], text)
    })
}

