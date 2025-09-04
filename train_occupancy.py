import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import pickle, os

# Load occupancy data
df = pd.read_csv('data/occupancy_data.csv')

# Convert month to numeric index
df['month'] = pd.PeriodIndex(df['month'], freq='M')
df['month_num'] = df['month'].apply(lambda x: x.year*12 + x.month)

# Train model
X = df[['month_num']]
y = df['beds_booked']

model = LinearRegression()
model.fit(X, y)

# Save model
os.makedirs('ml_models', exist_ok=True)
with open('ml_models/occupancy_model.pkl', 'wb') as f:
    pickle.dump(model, f)

# Predict next 3 months
last_month_num = df['month_num'].max()
future_months = np.array(range(last_month_num+1, last_month_num+4)).reshape(-1, 1)
forecast = model.predict(future_months)

# Save forecast
forecast_df = pd.DataFrame({
    'month_num': range(last_month_num+1, last_month_num+4),
    'beds_predicted': forecast.round().astype(int)
})
forecast_df.to_csv('data/occupancy_forecast.csv', index=False)

print(" Forecast saved to data/occupancy_forecast.csv")
print(forecast_df)
