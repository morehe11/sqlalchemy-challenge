import datetime as dt
import numpy as np
import pandas as pd


from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import sqlalchemy
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)
################################################
#Flask Setup
################################################
app = Flask(__name__)

most_recent_date = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())
most_recent_date = list(np.ravel(most_recent_date))[0]

most_recent_date= dt.datetime.strptime(most_recent_date, '%Y-%m-%d')

recent_year = int(dt.datetime.strftime(most_recent_date, '%Y'))
recent_month = int(dt.datetime.strftime(most_recent_date, '%m'))
recent_day = int(dt.datetime.strftime(most_recent_date, '%d'))

year_earlier = dt.date(recent_year, recent_month, recent_day) - dt.timedelta(days=365)
#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/2016-08-23<br/>"
        f"/api/v1.0/temp/2016-08-23/2017-08-23"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp, Measurement.station).\
                filter(Measurement.date >= year_earlier).\
                order_by(Measurement.date).all()
    session.close()
    percp_data = []
    for result in results:
        percp_dict = {result.date: result.prcp, 'Station': result.station}
        percp_data.append(percp_dict)
    return jsonify(percp_data) 
    
    
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    session = Session(engine)
    results = session.query(Station.name).all()
    session.close()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)
    
@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for previous year."""
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
                filter(Measurement.date >= year_earlier).\
                order_by(Measurement.date).all()
    session.close()
    temp_data = []
    for result in results:
        temp_dict = {result.date: result.tobs, 'Station': result.station}
        temp_data.append(temp_dict)
    return jsonify(temp_data)

@app.route("/api/v1.0/temp/<start>")
def stats_start(start):
    """Return TMIN, TAVG, TMAX."""
    session = Session(engine)
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).\
                group_by(Measurement.date).all()
    session.close()

    dates = []
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Lowest Temp"] = result[1]
        date_dict["Highest Temp"] = result[2]
        date_dict["Average Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

@app.route("/api/v1.0/temp/<start>/<end>")
def stats_start_end(start, end):
    """Return TMIN, TAVG, TMAX."""
    session = Session(engine)
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).\
                filter(func.strftime("%Y-%m-%d", Measurement.date) <= end).\
                group_by(Measurement.date).all()
    session.close()

    dates = []
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Lowest Temp"] = result[1]
        date_dict["Highest Temp"] = result[2]
        date_dict["Average Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

session.close()
if __name__ == '__main__':
    app.run(debug=True)