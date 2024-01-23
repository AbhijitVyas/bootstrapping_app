# Bootstrapping task learning app
This application provides a GUI based user interface to help human teachers iteratively guide the robot student in interactive task learning setup.

## Steps
1. ```bash
   git clone git@github.com:AbhijitVyas/bootstrapping_app.git
2. Run
   ```bash
   pip install -r requirements.txt
3. Open the project files in your preferable IDE (eg. PyCharm)
5. From the ROOT directory, run the command
   ```bash
   docker build -t bootstrapping_app .
   docker run -p 127.0.0.1:5000:5000 bootstrapping_app 
   ```
   this should bootup the flask based docker application which can be tested at

   http://localhost:5000/
   http://localhost:5000/register
   http://localhost:5000/bootstrapping.

## Steps (to run bootstrapping + rasaactions)
1. ```bash
   git clone git@github.com:Srikanth635/bootstrapping.git
2. Run
   ```bash
   docker-compose -f compose.yml up
3. This should download images from hub (if not available locally) and then start two containers (1.bootstrapping,2.rasaactions)
4. Once the RASA server is up and running, open 'http://localhost:5000/bootstrapping' on host machine to access bootstrapping app.
5. Enter the instruction in the text box shown and press next.
