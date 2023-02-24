function problem_searcher(data, text) {
    lowered_text = text.toLowerCase()
    return data.filter(row => {
        return row._data.id.toString().toLowerCase().includes(lowered_text) ||
               row._data.name.toString().toLowerCase().includes(lowered_text) ||
               row._data.solves.toString().toLowerCase().includes(lowered_text)
    })
}
