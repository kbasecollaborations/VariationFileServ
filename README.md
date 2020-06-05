Dyanmic server to support byte ranges for variation workflows


To test use (Edit token information in .env)
<code>cp .env.example  .env</code>
<code>docker-compose up</code>

Run tests with (currently working for  appdev)
<code>docker-compose run web test </code>



```python
shock_id = "ad4ebf34-49fa-41b0-ab4c-9358d46a352b"
token = "**********"
kbase_session_token = "kbase_session=" + token
header={'Cookie': kbase_session_token, 'Range': 'bytes:6-10'}
# appdev.kbase.us/services/shock-api/node/ad4ebf34-49fa-41b0-ab4c-9358d46a352b in the following code
# can be changed to url for any environment
url = "http://127.0.0.1:5000/jbrowse_query/appdev.kbase.us/services/shock-api/node/ad4ebf34-49fa-41b0-ab4c-9358d46a352b"
response = requests.post(url, headers=header)
```

