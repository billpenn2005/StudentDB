# API List
## About CSRF and POST
Please add these in JS
```
const csrfToken = "{{ csrf_token }}";
```
Please add these in headers if not specially mentioned
```
'Content-Type':'application/x-www-form-urlencoded', //if you need to use list or sth in json, ignore this line
"X-CSRFToken": csrfToken
```
## Auth
 - /auth/loginapi
    Requires CSRF and salt
    **send**
    username<-username
    password<-MD5(MD5(password)+salt)
    Example:
    ```
    const passwordMD5 = CryptoJS.MD5(password).toString();

    // Step 3: Concatenate salt with MD5 hash of the password
    const hashedPassword = CryptoJS.MD5(passwordMD5 + salt).toString();

    const data = {
        username:username,
        password:hashedPassword
    }

    ```
    **result**
    if success:
    ```
    'state':'Success'
    ```
    else:
    ```
    'state':'Failed',
    'reason':<reason of fail>
    ```
 - /auth/salt
    not need CSRF
    **send**
    just POST
    **result**
    ```
    'salt':<salt>
    ```
 - /auth/logoutapi
    Requires CSRF
    **send**
    just POST
    **result**
    ```
    "state":<"Success"or"Failed">,
    "reason":<if failed>
    ```