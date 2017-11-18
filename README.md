# flup
A simple pastebin written in Flask

~~~
flup is a simple pastebin: you upload a file and get an identifier
as a response.

the identifier is later used to retrieve your data, with the format:
GET /<identifier>

the file must be uploaded with a POST request to /, attaching the file to
a form field named 'f', and using the content-type multipart/form-data.

when you upload a file, you get a the identifier to your data as a
response; you should save this to later retrieve your data.

printing this help message:
    $ curl localhost:5000
    $ http localhost:5000

uploading a file with curl:
    $ curl -F 'f=@file.txt' localhost:5000

uploading a file with httpie:
    $ http -f localhost:5000 f@file.txt

uploading from stdin with curl:
    $ cat file.txt | curl -F 'f=@-' localhost:5000

retrieving a file with curl:
    $ curl localhost:5000/<identifier>

retrieving a file with httpie:
    $ http localhost:5000/<identifier>

say you get an identifier 'abc-123' as a response when you upload your
file:
    $ curl localhost:5000/abc-123
    $ http localhost:5000/abc-123
~~~
