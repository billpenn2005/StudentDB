  
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

  document.addEventListener('DOMContentLoaded', () => {
            const infoWindow = document.getElementById('infoWindow');
            const loadingText = document.getElementById('loading');
            const csrftoken = getCookie('csrftoken');
            //const csrfToken = "{{ csrf_token }}";
            // 获取基本信息
            fetch('/api/basicinfo', {
                method: 'POST',
                headers: {
                    //'Content-Type': 'application/json'
                    'Content-Type':'application/x-www-form-urlencoded',
                    "X-CSRFToken": csrftoken
                }
            })
            .then(response => response.json())
            .then(data => {
                loadingText.textContent = '';
                if (data.state === 'Failed') {
                    infoWindow.innerHTML = '<p class="error">获取基本信息失败</p>';
                } else if (data.state === 'Success') {
                    const role = data.role;
                    const name = data.name;
                    let idField = '';

                    if (role === 'Student') {
                        idField = `<p>学生ID: ${data.student_id}</p>
                                    <p>年龄: ${data.age}</p>
                                    <p>性别：${data.sex}`;
                    } else if (role === 'Teacher') {
                        idField = `<p>教师ID: ${data.teacher_id}</p>`;
                    }

                    infoWindow.innerHTML = `
                        <p>姓名: ${name}</p>
                        <p>角色: ${role}</p>
                        ${idField}
                    `;
                }
            })
            .catch(error => {
                loadingText.textContent = '';
                infoWindow.innerHTML = `<p class="error">请求失败: ${error.message}</p>`;
            });

            // 登出功能
            document.getElementById('logoutButton').addEventListener('click', () => {
                fetch('/auth/logoutapi', {
                    method: 'POST',
                    headers: {
                        //'Content-Type': 'application/json'
                        'Content-Type':'application/x-www-form-urlencoded',
                        "X-CSRFToken": csrfToken
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.state === 'Success') {
                        location.reload();
                    } else {
                        alert('登出失败: ' + (data.message || '未知错误'));
                    }
                })
                .catch(error => {
                    alert('请求失败: ' + error.message);
                });
            });
        });