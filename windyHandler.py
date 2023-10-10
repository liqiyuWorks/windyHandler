import numpy as np
import requests
from pkg.function import Function
from datetime import datetime
import pytz
import netCDF4

__version__ = '1.0'


class WindyWeather:
    def __init__(
        self,
        latitude=0,
        longitude=0,
        date=None,
        timezone="UTC",
    ):
        # Initialize constants
        self.earth_radius = 6.3781 * (10**6)
        self.air_gas_constant = 287.05287  # in J/K/Kg
        self.standard_g = 9.80665

        # Save latitude and longitude
        if latitude is not None and longitude is not None:
            self.latitude, self.longitude = latitude, longitude
        else:
            self.latitude, self.longitude = None, None

        # Save date
        if date is not None:
            self.set_date(date, timezone)
        else:
            self.date = None
            self.datetime_date = None
            self.local_date = None
            self.timezone = None

    def set_date(self, date, timezone="UTC"):
        # Store date and configure time zone
        self.timezone = timezone
        tz = pytz.timezone(self.timezone)
        if type(date) is not datetime:
            local_date = datetime(*date)
        else:
            local_date = date
        if local_date.tzinfo is None:
            local_date = tz.localize(local_date)
        self.date = date
        self.local_date = local_date
        self.datetime_date = self.local_date.astimezone(pytz.UTC)

        return None

    def process_windy_atmosphere(self, model="ECMWF"):
        # model=GFS or ECMWF
        # Process the model string
        model = model.lower()
        if model[-1] == "u":  # case iconEu
            model = "".join([model[:4], model[4].upper(), model[4 + 1:]])
        # Load data from Windy.com: json file
        url = f"https://node.windy.com/forecast/meteogram/{model}/{self.latitude}/{self.longitude}/?step=undefined"
        try:
            response = requests.get(url).json()
        except Exception:
            if model == "iconEu":
                raise ValueError(
                    "Could not get a valid response for Icon-EU from Windy. Check if the latitude and longitude coordinates set are inside Europe.",
                )
            raise

        # Determine time index from model
        time_array = np.array(response["data"]["hours"])
        time_units = "milliseconds since 1970-01-01 00:00:00"
        launch_time_in_units = netCDF4.date2num(self.datetime_date, time_units)
        # Find the index of the closest time in time_array to the launch time
        time_index = (np.abs(time_array - launch_time_in_units)).argmin()
        print(f"*当前时间{self.datetime_date} => 索引值: {time_index}")

        # Define available pressure levels
        pressure_levels = np.array([
            1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 250, 200,
            150
        ])

        # Process geopotential height array
        geopotential_height_array = np.array([
            response["data"][f"gh-{pL}h"][time_index] for pL in pressure_levels
        ])
        # Convert geopotential height to geometric altitude (ASL)
        R = self.earth_radius
        altitude_array = R * geopotential_height_array / (
            R - geopotential_height_array)

        # Process temperature array (in Kelvin)
        temperature_array = np.array([
            response["data"][f"temp-{pL}h"][time_index]
            for pL in pressure_levels
        ])

        # Process wind-u and wind-v array (in m/s)
        wind_u_array = np.array([
            response["data"][f"wind_u-{pL}h"][time_index]
            for pL in pressure_levels
        ])
        wind_v_array = np.array([
            response["data"][f"wind_v-{pL}h"][time_index]
            for pL in pressure_levels
        ])

        # Determine wind speed, heading and direction
        wind_speed_array = np.sqrt(wind_u_array**2 + wind_v_array**2)
        wind_heading_array = (np.arctan2(wind_u_array, wind_v_array) *
                              (180 / np.pi) % 360)
        wind_direction_array = (wind_heading_array - 180) % 360

        # Combine all data into big array
        data_array = np.ma.column_stack([
            100 * pressure_levels,  # Convert hPa to Pa
            altitude_array,
            temperature_array,
            wind_u_array,
            wind_v_array,
            wind_heading_array,
            wind_direction_array,
            wind_speed_array,
        ])

        # Save atmospheric data
        self.pressure = Function(
            data_array[:, (1, 0)],
            inputs="Height Above Sea Level (m)",
            outputs="Pressure (Pa)",
            interpolation="linear",
        )
        self.temperature = Function(
            data_array[:, (1, 2)],
            inputs="Height Above Sea Level (m)",
            outputs="Temperature (F)",
            interpolation="linear",
        )
        self.wind_direction = Function(
            data_array[:, (1, 6)],
            inputs="Height Above Sea Level (m)",
            outputs="Wind Direction (Deg True)",
            interpolation="linear",
        )
        self.wind_heading = Function(
            data_array[:, (1, 5)],
            inputs="Height Above Sea Level (m)",
            outputs="Wind Heading (Deg True)",
            interpolation="linear",
        )
        self.wind_speed = Function(
            data_array[:, (1, 7)],
            inputs="Height Above Sea Level (m)",
            outputs="Wind Speed (m/s)",
            interpolation="linear",
        )
        self.wind_velocity_x = Function(
            data_array[:, (1, 3)],
            inputs="Height Above Sea Level (m)",
            outputs="Wind Velocity X (m/s)",
            interpolation="linear",
        )
        self.wind_velocity_y = Function(
            data_array[:, (1, 4)],
            inputs="Height Above Sea Level (m)",
            outputs="Wind Velocity Y (m/s)",
            interpolation="linear",
        )

        # Save maximum expected height
        self.max_expected_height = max(altitude_array[0], altitude_array[-1])

        # Get elevation data from file
        self.elevation = response["header"]["elevation"]

        # Compute info data
        self.atmospheric_model_init_date = netCDF4.num2date(time_array[0],
                                                            units=time_units)
        self.atmospheric_model_end_date = netCDF4.num2date(time_array[-1],
                                                           units=time_units)
        self.atmospheric_model_interval = netCDF4.num2date(
            (time_array[-1] - time_array[0]) / (len(time_array) - 1),
            units=time_units).hour
        self.atmospheric_model_init_lat = self.latitude
        self.atmospheric_model_end_lat = self.latitude
        self.atmospheric_model_init_lon = self.longitude
        self.atmospheric_model_end_lon = self.longitude

        # Save debugging data
        self.geopotentials = geopotential_height_array
        self.wind_us = wind_u_array
        self.wind_vs = wind_v_array
        self.levels = pressure_levels
        self.temperatures = temperature_array
        self.time_array = time_array
        self.height = altitude_array


# if __name__ == "__main__":
#     ww = WindyWeather(31.571, 120.294, [2023, 10, 10, 3])
#     ww.process_windy_atmosphere()
#     # print("time_array", ww.time_array)
#     print("temperature", ww.temperatures[0])
#     # print("temperature_array", ww.temperature)