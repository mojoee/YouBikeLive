from abc import ABC, abstractmethod
import pandas as pd
from DBIO import YouBikeDataManager
from prophet import Prophet


class DemandPredictionStrategy(ABC):
    @abstractmethod
    def predict(self, station_id, forecast_date=None):
        pass


class ProphetDemandPredictionStrategy(DemandPredictionStrategy):
    def __init__(self, data_manager: YouBikeDataManager):
        self.data_manager = data_manager

    def predict(self, station_id, forecast_date=None):


        # Use YouBikeDataManager to load and preprocess station data
        df = self.data_manager.load_and_preprocess_station(station_id)
        if forecast_date is None:
            last_date = df.index[-1].date()
            forecast_date = (pd.to_datetime(last_date) + pd.Timedelta(days=1)).date()

        forecast_start = pd.to_datetime(forecast_date)
        df = df.reset_index()
        df = df[df['mday'] < forecast_start]
        if len(df) < 10:
            return [0] * 24
        m = Prophet(changepoint_prior_scale=0.01)
        df_prophet = df[["mday", "demand"]]
        df_prophet.columns = ["ds", "y"]

        m.fit(df_prophet)

        future = m.make_future_dataframe(periods=23, freq='H')
        forecast = m.predict(future)
        return [int(x) for x in forecast['yhat'].tolist()][-24:]


class NaiveDemandPredictionStrategy(DemandPredictionStrategy):
    def __init__(self, data_manager: YouBikeDataManager):
        self.data_manager = data_manager

    def predict(self, station_id, forecast_date=None):
        # Use YouBikeDataManager to load and preprocess station data
        df = self.data_manager.load_and_preprocess_station(station_id)
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

            if (prev_day in df.index) and (prev_week in df.index):
                val_prev_day = df.loc[prev_day, 'demand']
                val_prev_week = df.loc[prev_week, 'demand']
                pred = (val_prev_day + val_prev_week) / 2.0
                predicted_values.append(float(pred))
            else:
                predicted_values.append(0.0)
        return predicted_values


class DemandPredictionContext:
    def __init__(self, strategy: DemandPredictionStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: DemandPredictionStrategy):
        self._strategy = strategy

    def predict_demand(self, station_id, forecast_date=None):
        return self._strategy.predict(station_id, forecast_date)


# Example usage
if __name__ == "__main__":
    db_path = "./youbike_data.db"
    data_manager = YouBikeDataManager(db_path)

    # Using Prophet strategy
    prophet_strategy = ProphetDemandPredictionStrategy(data_manager)
    context = DemandPredictionContext(prophet_strategy)
    predictions = context.predict_demand("500101001")
    print(predictions)

    # Switching to Naive strategy
    naive_strategy = NaiveDemandPredictionStrategy(data_manager)
    context.set_strategy(naive_strategy)
    predictions = context.predict_demand("500101001")
    print(predictions)
