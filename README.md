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
   dockeimage build -t bootstrapping_app .
   docker run -p 127.0.0.1:5000:5000 bootstrapping_app 
   ```
   this should bootup the flask based docker application which can be tested at

   http://localhost:5000/ \\
   http://localhost:5000/register \\
   http://localhost:5000/bootstrapping.
