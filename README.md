Dyanmic server to support byte ranges for variation workflows


To test 
</br>

(copy .env.example to .env and update token information in .env)
</br>
<code>cp .env.example  .env</code>

The test uses public workspaces in appdev or ci
So set the following variables for ci or appdev in .env file
KBASE_ENDPOINT=https://appdev.kbase.us/services
token=************



</br>
<code>docker-compose up</code>

</br>
Run tests with (currently working for  appdev)

</br>
<code>docker-compose run web test </code>
</br>


