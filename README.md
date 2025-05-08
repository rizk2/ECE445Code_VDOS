# Running the webserver. 

## Run the backend first. 
  1) Go to the 'vdos_webapp/backend' directory
  2) Use 'uvicorn main:app --reload' in terminal. You may have to specify python version with 'python3.13 -m uvicorn main:app --reload'. There is a problem with soundfile library on Apple Silicon Macs on some python versions.

## Running the front end 
  1) Go to the 'vdos_webapp/react-frontend'
  2) Run 'npm install' on first execution
  3) Then use 'npm start' in terminal 

## Starting the web application through bash
  1) Make sure all dependencies are installed
  2) Run 'bash start_app.sh' in the directory 'vdos_webapp'


# Prerequisites

Python (tested on python 3.13):
uvicorn, librosa, numpy, parselmouth, soundfile, matplotlib, fastapi

Javascript: react, npm, plotly