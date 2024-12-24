function showHidePass(...fieldIds) {
    fieldIds.forEach(id => {
        var field = document.getElementById(id);
        if (field) {
            field.type = field.type === "password" ? "text" : "password";
        }
    });
}


function addComment(roomId) {
    const textarea = document.getElementById("comment")
    const content = textarea.value.trim();

    if (!content) {
        alert("Vui lòng nhập nội dung bình luận!");
        return;
    }

    fetch(`/api/rooms/${roomId}/comments`, {
        method: "post",
        body: JSON.stringify({
            "content": content
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => res.json()).then(c => {
        let html = `
           <div class="border p-3 rounded mb-2">
               <strong>${ c.user.name }</strong>
               <p>${ c.content }</p>
               <span class="text-muted date">${ moment(c.created_date).locale("vi").fromNow() }</span>
           </div>
        `

        let e = document.getElementById("comment_section");
        e.innerHTML = html + e.innerHTML;

        textarea.value = '';
    }).catch(error => {
        console.error('Error adding comment:', error);
        alert("Đã xảy ra lỗi khi thêm bình luận. Vui lòng thử lại!");
    });
}