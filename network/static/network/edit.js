function showEdit(element, id) {
    let parent = element.parentElement
    let value = element.nextElementSibling.innerHTML
    let form = document.createElement('form')
    form.innerHTML = `<textarea class="form-control">${value}</textarea>
        <input type="submit" class="btn btn-primary mb-4 mt-2" value="Save"/>`

    form.addEventListener('submit', (event) => {
        event.preventDefault()
        let value = form.querySelector('textarea').value
        fetch(`/edit/${id}`, {
            method: 'PUT',
            body: JSON.stringify({
                post: value
            })
        }).then(() => {
            form.remove()
            element.nextElementSibling.style.display = 'block'
            element.nextElementSibling.innerHTML = value
            element.style.display = 'block'
        })

    })

    parent.insertBefore(form, element)
    element.nextElementSibling.style.display = 'none'
    element.style.display = 'none'

}


function updateLike(element, id) {
    let likes = parseInt(element.previousElementSibling.innerHTML)
    console.log(likes);
    if (element.className.includes("up")) {
        fetch(`/like/${id}`, {
            method: "PUT"
        }).then(response => response.json()).then(() => {
            element.className = 'fa fa-thumbs-down'
            element.previousElementSibling.innerHTML = `${likes + 1} like${(likes + 1) == 1 ? '' : 's'}`
        })
    }
    else if (element.className.includes("down")) {
        fetch(`/unlike/${id}`, {
            method: "PUT"
        }).then(response => {
            element.className = 'fa fa-thumbs-up'
            element.previousElementSibling.innerHTML = `${likes - 1} like${(likes - 1) == 1 ? '' : 's'}`
        })
    }
}