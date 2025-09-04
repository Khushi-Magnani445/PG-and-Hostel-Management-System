import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pickle, os

# 1. Load complaints CSV
df = pd.read_csv('data/complaints.csv')

# 2. Compute resolution days
df['date_raised'] = pd.to_datetime(df['date_raised'])
df['date_resolved'] = pd.to_datetime(df['date_resolved'])
df['resolution_days'] = (df['date_resolved'] - df['date_raised']).dt.days

# 3. Encode features
df['is_urgent'] = df['is_urgent'].astype(int)
df = pd.get_dummies(df, columns=['complaint_type'], drop_first=True)

X = df[['is_urgent'] + [c for c in df.columns if c.startswith('complaint_type_')]]
y = df['resolution_days']

# 4. Train regression model
model = LinearRegression()
model.fit(X, y)

# 5. Save model

with open('ml_models/complaint_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print(" Complaint resolution model trained successfully!")
