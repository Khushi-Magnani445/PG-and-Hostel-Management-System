import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# 1. Load your CSV
df = pd.read_csv('data/PG.csv')
print(df.head())
# 2. Select relevant columns
df = df[['area(sq-fit)','bathroomCount','bedAvailable','roomAvailable','shared','furnishingType','minRent(Rs)']]

# Rename columns for Python-friendly usage
df.columns = ['area_sqft','bathroom_count','bed_available','room_available','shared','furnishing_type','min_rent']

# Encode categorical & boolean
df['shared'] = df['shared'].astype(int)  # True/False to 1/0
df = pd.get_dummies(df, columns=['furnishing_type'], drop_first=True)

# Features and target
X = df.drop('min_rent', axis=1)
y = df['min_rent']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

# Save model
with open('ml_models/rent_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print(" Rent prediction model trained successfully!")
