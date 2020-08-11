import numpy as np

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Sation List : /api/v1.0/stations<br/>"
        f"Temperature for previous year: /api/v1.0/tobs<br/>"
        f"Temp stats from start_date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temp stats from start_date to end_date (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )
####Route precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query Measurement 
    p_results = session.query(Measurement.date,Measurement.prcp).all()

    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value
    precipitation = []
    for date,prcp in p_results:
        prcp_dict = {}
        prcp_dict[f"{date}"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

####Route Station
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query Station
    s_results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(s_results))

    #Return a JSON list of stations from the dataset
    return jsonify(all_stations)

####Route tobs
@app.route('/api/v1.0/tobs')
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Get Last Date from measurement table
    last_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Calculate the date 1 year ago from the last data point in the database
    latest_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    query_date = dt.date(latest_date.year -1, latest_date.month, latest_date.day)

    #Most active station
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).\
    order_by(func.count(Measurement.id).desc()).first()

    #Query the dates and temperature observations of the most active station for the last year of data.
    t_results= session.query( Measurement.date,Measurement.tobs).\
        filter(Measurement.date >= query_date).\
        filter(Measurement.station == most_active_station[0]).all()

    session.close()

    #Return a JSON list of temperature observations (TOBS) for the previous year
    temp_active_station = []
    for date, tobs in t_results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temperature observations"] = tobs
        temp_active_station.append(tobs_dict)

    return jsonify(temp_active_station)

####Route Start date
@app.route('/api/v1.0/<start_date>')
def temp_start(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query to calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
    ts_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    session.close()

    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date
    temp_stat_date1 = []
    for min,avg,max in ts_results:
        tobs_dict_1 = {}
        tobs_dict_1["Min"] = min
        tobs_dict_1["Avg"] = avg
        tobs_dict_1["Max"] = max
        temp_stat_date1.append(tobs_dict_1)


    return jsonify(temp_stat_date1)

####Route Start and End date
@app.route('/api/v1.0/<start_date>/<end_date>')
def temp_start_end(start_date,end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query to calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive
    tse_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()


    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a givensatart to end date
    temp_stat_date2 = []
    for min,avg,max in tse_results:
        tobs_dict_2 = {}
        tobs_dict_2["Min"] = min
        tobs_dict_2["Average"] = avg
        tobs_dict_2["Max"] = max
        temp_stat_date2.append(tobs_dict_2)

    return jsonify(temp_stat_date2)

if __name__ == '__main__':
    app.run(debug=True)