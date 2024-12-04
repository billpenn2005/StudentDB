# API List
## About CSRF and POST
Please add these in JS if it is in your html
```
const csrfToken = "{{ csrf_token }}";
```
Please add these in headers if not specially mentioned
```
'Content-Type':'application/x-www-form-urlencoded', //if you need to use list or sth in json, ignore this line
"X-CSRFToken": csrfToken
```
If your JS is extern file then please get cookie `csrftoken` and post it
```
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
```

```
const csrftoken = getCookie('csrftoken');
```

```
'Content-Type':'application/x-www-form-urlencoded', //If mentioned InPost, add this line,if mentioned InBody or you need to use list or sth in json, ignore this line
"X-CSRFToken": csrftoken
```
If not specially mentioned then all need CSRFtoken

## 约定
**格式**
[额外说明]
send(InPost/InBody)
参数名称:参数类型:说明(非特别声明则为必须参数)
receive
参数名称:参数类型:说明

## Auth
 - **/auth/api/login**
    Requires CSRF and salt
    **send(InPost)**
    username:str:user's name
    password:str:MD5(MD5(password)+salt)
    **receive**
    state:str:"Success"/"Failed"
    reason:str:Only received when fail, reason of fail
    **Example:**
    ```
    const passwordMD5 = CryptoJS.MD5(password).toString();

    // Step 3: Concatenate salt with MD5 hash of the password
    const hashedPassword = CryptoJS.MD5(passwordMD5 + salt).toString();

    const data = {
        username:username,
        password:hashedPassword
    }

    ```
 - **/auth/api/salt**
    not need CSRF
    **send(InPost)**
    **receive**
    'salt':str:salt string
 - **/auth/api/logout**
    **send(InPost)**
    **receive**
    state:str:"Success"/"Failed"
    reason:str:Only if failed, the reason
