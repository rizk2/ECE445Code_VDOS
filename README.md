# Running the code. 

## Run the backend first. 
  1) cd to the backend folder
  2) use 'uvicorn main:app --reload' in terminal. You may have to specify python version with 'python3.13 -m uvicorn main:app --reload'. There is a problem with soundfile library on Apple Silicon Macs on some python versions.

## Running the front end 
  1) cd to the vdostest
  2) run 'npm install' on first execution
  3) then use 'npm start' in terminal 

## Starting the web application through bash
  1) make sure all dependencies are installed
  2) run 'bash start_app.sh' in the home directory '../ECE445CODE_VDOS'


# Prerequisites

Python (tested on python 3.13):
uvicorn, librosa, numpy, parselmouth, soundfile, matplotlib, fastapi

Javascript: react, npm, plotly