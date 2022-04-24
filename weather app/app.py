from flask import Flask, render_template, request
import requests
import time


app = Flask(__name__,
            static_url_path='', 
            static_folder='static',
            template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def getvalue():
    place = request.form['place']
    place = str(place).title()
    apikey = "dda1f46a20919096f27ebb02dff4b399"
    api = f"http://api.openweathermap.org/data/2.5/weather?q={place}&appid={apikey}"
    json_data = requests.get(api).json()
    condition = json_data['weather'][0]['main']
    temp = int(json_data['main']['temp'] - 273.15)
    atemp = str(temp)+"°C"
    mintemp = int(json_data['main']['temp_min'] - 273.15)
    maxtemp = int(json_data['main']['temp_max'] - 273.15)
    pressure = json_data['main']['pressure']
    humidity = json_data['main']['humidity']
    wind = json_data['wind']['speed']
    wind =str(wind)+ "m.p.h"
    sunrise = time.strftime("%I:%M:%S",time.gmtime(json_data['sys']['sunrise'] - 21600))

    sunset = time.strftime("%I:%M:%S",time.gmtime(json_data['sys']['sunset'] - 21600))
    return render_template('wea.html',j=json_data, p=place,c=condition,t=temp,min=mintemp,max=maxtemp,pr=pressure,h=humidity,w=wind,sr=sunrise,ss=sunset,a=atemp)




if __name__ == '__main__':
    app.run(debug=True)