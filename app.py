# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt
import sqlalchemy
from sqlalchemy import func, create_engine, inspect
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import pandas as pd

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model

Base = automap_base()

# reflect the tables

Base.prepare(autoload_with=engine)

# Save references to each table

Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB

session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# List all the available routes

@app.route("/")
def home():
    """Homepage route."""
    return (
        f"Welcome to the Climate Analysis!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Query precipitation data for the last 12 months

    most_recent_date = session.query(func.max(Measurement.date)).scalar()

    one_year_ago = pd.to_datetime(most_recent_date) - pd.DateOffset(days=365)

    results = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= one_year_ago.strftime('%Y-%m-%d')).all()

    # Convert results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():

    # Query all stations

    stations = session.query(Station.station).all()

    # Convert results to a list

    station_list = [station[0] for station in stations]

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    
    # Query the most active station

    most_active_station = session.query(Measurement.station)\
        .group_by(Measurement.station)\
        .order_by(func.count().desc())\
        .first()[0]
    
    # Calculate the date one year ago from the last date in the dataset

    most_recent_date = session.query(func.max(Measurement.date)).scalar()

    one_year_ago = pd.to_datetime(most_recent_date) - pd.DateOffset(days=365)

    # Query temperature observations for the most active station for the last 12 months
    
    results = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station)\
        .filter(Measurement.date >= one_year_ago.strftime('%Y-%m-%d')).all()

    # Convert results to a list of dictionaries
    
    temperature_data = [{"Date": date, "Temperature": tobs} for date, tobs in results]

    return jsonify(temperature_data)






@app.route("/api/v1.0/<start>")
def temp_stats_start(start):

    # Convert start date to datetime format

    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    # Query temperature statistics for dates greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs).label('TMIN'),
                             func.avg(Measurement.tobs).label('TAVG'),
                             func.max(Measurement.tobs).label('TMAX'))\
        .filter(Measurement.date >= start_date).all()

    # Convert results to a dictionary

    temp_stats = {"TMIN": results[0].TMIN, "TAVG": results[0].TAVG, "TMAX": results[0].TMAX}
    
    return jsonify(temp_stats)


@app.route("/api/v1.0/<start>/<end>")
def temp_stats_start_end(start, end):

     # Convert start and end dates to datetime format
    
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
   
    # Query temperature statistics for dates between the start and end dates
    
    results = session.query(func.min(Measurement.tobs).label('TMIN'),
                             func.avg(Measurement.tobs).label('TAVG'),
                             func.max(Measurement.tobs).label('TMAX'))\
        .filter(Measurement.date >= start)\
        .filter(Measurement.date <= end).all()

    # Convert results to a dictionary
    
    temp_stats = {"TMIN": results[0].TMIN, "TAVG": results[0].TAVG, "TMAX": results[0].TMAX}

    return jsonify(temp_stats)



if __name__ == "__main__":
    app.run(debug=True)