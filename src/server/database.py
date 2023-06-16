import pyrebase

firebaseConfig ={
  "apiKey": "AIzaSyDvXiudgzzDEkrJLVG6Tl8gyuL4Ep91FlI",
  "authDomain": "distributed-6022e.firebaseapp.com",
  "databaseURL": "https://distributed-6022e-default-rtdb.firebaseio.com",
  "projectId": "distributed-6022e",
  "storageBucket": "distributed-6022e.appspot.com",
  "messagingSenderId": "31720189256",
  "appId": "1:31720189256:web:0794cfcaf32088fd28977d",
  "measurementId": "G-8P3R01V4JE"
}

firebase=pyrebase.initialize_app(firebaseConfig)

