# Import dependencies
import numpy as np
from flask import Flask, jsonify
from datetime import datetime
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite?check_same_thread=False")
conn = engine.connect()

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

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

@app.route("/")
def home():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/calc_temps/<start><br/>"
        f"/api/v1.0/calc_temps/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of dates & precipitations"""
    prec_12_month = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= "2016-08-23").filter(Measurement.date <= "2017-08-23").\
        order_by(Measurement.date).all()

    precipitation = []
    for prec in prec_12_month:
        row = {"Date": "Precipitation"}
        row["Date"] = prec[0]
        row["Precipitation"] = float(prec[1])
        precipitation.append(row)

    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    stations = session.query(Station.station, Station.name).group_by(
        Station.station).all()
    station_list = list(np.ravel(stations))

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of dates and temps from a year of last data point"""
    temps = session.query(Measurement.station, Measurement.tobs).\
        filter(Measurement.date >= "2016-08-23").\
            filter(Measurement.date <= "2017-08-23")
    
    temp_list = []
    for temp in temps:
        temp_dict = {}
        temp_dict["Station"] = temp[0]
        temp_dict["Temperatures"] = float(temp[1])
        temp_list.append(temp_dict)
    
    return jsonify(temp_list)


@app.route("/api/v1.0/calc_temps/<start>")
def calc_temps(start="start_date"):
    start_date = datetime.strptime("2017-06-29", "%Y-%m-%d").date()
    start_results = session.query(func.max(Measurement.tobs),
                                  func.min(Measurement.tobs),
                                  func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date)

    start_temps = []
    for temp in start_results:
        temp_dict = {}
        temp_dict["TAVG"] = float(temp[2])
        temp_dict["TMAX"] = float(temp[0])
        temp_dict["TMIN"] = float(temp[1])
        start_temps.append(temp_dict)

    return jsonify(start_temps)


@app.route("/api/v1.0/calc_temps/<start>/<end>")
def calc_temps_2(start="start_date", end="end_date"):
    start_date = datetime.strptime("2017-06-29", "%Y-%m-%d").date()
    end_date = datetime.strptime("2017-07-07", "%Y-%m-%d").date()
    trip_results = session.query(func.max(Measurement.tobs).label("max_temps"),
                                 func.min(Measurement.tobs).label("min_temps"),\
                                    func.avg(Measurement.tobs).label("avg_temps")).\
                                        filter(Measurement.date >= "start_date").\
                                            filter(Measurement.date <= "end-date")

    trip_temps = []
    for temp in trip_results:
        temp_dict = {}
        temp_dict["TAVG"] = float(temp[2])
        temp_dict["TMAX"] = float(temp[0])
        temp_dict["TMIN"] = float(temp[1])
        trip_temps.append(temp_dict)
        
    return jsonify(trip_temps)


if __name__ == "__main__":
    app.run(debug=True)
