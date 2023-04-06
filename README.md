# NasalSymmetryFinder
This simple Flask app has a file upload where the user can upload a .obj or .stl file of their face. The application will return images depicting the symmetry of the user's nose. 

### How to Run
You will need:
- Flask: `pip install flask`
- That's pretty much it 

Unix Bash (Linux, Mac, etc.):
```
$ export FLASK_APP=flask_app
$ flask run
```

Windows CMD
```
> set FLASK_APP=flask_app
> flask run
```

Powershell
```
> $env:FLASK_APP = "flask_app"
> flask run
```

### How to use
- Go to the host and port number you specified. The default should be http://127.0.0.1:5000/
- Navigate to /upload 
- Upload your image
- You will be redirected
