from abc import ABC, abstractmethod
import pandas as pd
from DBIO import load_and_preprocess_station

class DemandPredictionStrategy(ABC):
    @abstractmethod
    def predict(self, station_id, forecast_date=None):
        pass

class ProphetDemandPredictionStrategy(DemandPredictionStrategy):
    def predict(self, station_id, forecast_date=None):
        # Implement Prophet prediction logic here
        pass

class NaiveDemandPredictionStrategy(DemandPredictionStrategy):
    def predict(self, station_id, forecast_date=None):
        df = load_and_preprocess_station(station_id)
        if df.empty:
            return [0] * 24

        if forecast_date is None:
            last_date = df.index[-1].date()
            forecast_date = (pd.to_datetime(last_date) + pd.Timedelta(days=1)).date()

        forecast_start = pd.to_datetime(forecast_date)
        forecast_end = forecast_start + pd.Timedelta(days=0, hours=23)
        hours = pd.date_range(start=forecast_start, end=forecast_end, freq='1H')

        predicted_values = []
        for hour in hours:
            prev_day = hour - pd.Timedelta(days=1)
            prev_week = hour - pd.Timedelta(days=7)
            # maybe can think about more sophisticated approach here. 

            if (prev_day in df.index) and (prev_week in df.index):
                val_prev_day = df.loc[prev_day, 'demand']
                val_prev_week = df.loc[prev_week, 'demand']
                pred = (val_prev_day + val_prev_week) / 2.0
                predicted_values.append(float(pred))
            else:
                predicted_values.append(0.0)
        # Implement naive prediction logic here
        return predicted_values


class DemandPredictionContext:
    def __init__(self, strategy: DemandPredictionStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: DemandPredictionStrategy):
        self._strategy = strategy

    def predict_demand(self, station_id, forecast_date=None):
        return self._strategy.predict(station_id, forecast_date)