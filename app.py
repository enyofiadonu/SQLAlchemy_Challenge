#import packages
import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np 

from flask import Flask, jsonify

import datetime as dt 

#Create engine
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

#reflecting an existing db into a new model, 
#reflect tables, save refernces of the tables
base = automap_base()
base.prepare(engine, reflect=True)

measurement = base.classes.measurement
station = base.classes.station


#Flask set up
app = Flask(__name__)




#Flask Routes
@app.route('/')
def welcome():
    '''List all available API routes.'''
    return(
        f'Welcome to the SQLAlchemy APP API!<br/>'
        f'Available Routes:<br/>'
        f'Precipitation: /api/v1.0/precipitation<br/>'
        f'List of Stations: /api/v1.0/stations<br/>'
        f'Temperature for One Year: /api.v1.0/tobs<br/>'
        f'Temperature Stats from the Start Date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>'
        f'Temperature Stats from the Start to End Dates(yyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd'
   )

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    qr = session.query(measurement.date, measurement.prcp).all()
    session.close()
    
    all_prcp=[('Date','Precipitation')]
    for date,prcp in qr:
        prcp_dict = {}
        prcp_dict[date] = prcp
        
        all_prcp.append(prcp_dict)
        
    return jsonify(all_prcp)

@app.route('/api/v1.0/stations')
def stations():
    
    
    session = Session(engine)
    qr = session.query(station.station).order_by(station.station).all()
    session.close()
    
    all_stations =  list(np.ravel(qr))
    return jsonify(all_stations)
            
@app.route('/api/v1.0/<start>')
def start_date(start):
    session = Session(engine)
    qr = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", measurement.date))).all()
    max_date_string = final_date_query[0][0]
    session.close()
   
    tobsall = []
    for min,avg,max in qr:
        tobs_dict = {}
        tobs_dict['Start Date'] = start
        tobs_dict['End Date'] = max_date_string
        tobs_dict['TMin'] = min
        tobs_dict['TAve'] = avg
        tobs_dict['TMax'] = max 
            
        tobsall.append(tobs_dict) 
        
    return jsonify(tobsall)

@app.route('/api/v1.0/<start>/<stop>')
def get_temp_start_stop(start,stop):
    session = Session(engine)
    qr = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= stop).all()
    session.close()
 
    tobsall = []
    for min,avg,max in qr:
        tobs_dict = {}
        tobs_dict['Start Date'] = start
        tobs_dict['End Date'] = stop
        tobs_dict['TMin'] = min
        tobs_dict['TAve'] = avg
        tobs_dict['TMax'] = max 
        tobsall.append(tobs_dict) 
        
    return jsonify(tobsall)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", measurement.date))).all()
    max_date_string = final_date_query[0][0]
    max_date = dt.datetime.strptime(max_date_string, "%Y-%m-%d")
    min_date = max_date - dt.timedelta(365)
    
    station = session.query(measurement.station,func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    
   

    qr = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= min_date).\
        filter(measurement.station == station[0][0]).\
        order_by(measurement.date).all()
    
    session.close()
    
    tobsall = []
    for date,tobs in qr:
        tobs_dict = {}
        tobs_dict['Date'] = date
        tobs_dict['tobs'] = tobs
        
        tobsall.append(tobs_dict)
        
    return jsonify(tobsall)

#running app
if __name__ =='__main__':
    app.run(debug=True)
    
    
    
        