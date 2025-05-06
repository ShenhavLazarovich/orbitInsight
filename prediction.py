"""
AI-powered Satellite Trajectory Prediction Module
Uses machine learning models to predict future satellite positions based on historical data
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scipy.interpolate import CubicSpline
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pickle
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants for model paths
MODEL_DIRECTORY = "models"
POSITION_MODEL_PATH = os.path.join(MODEL_DIRECTORY, "position_model.pkl")
VELOCITY_MODEL_PATH = os.path.join(MODEL_DIRECTORY, "velocity_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIRECTORY, "scaler.pkl")

def ensure_model_directory():
    """Ensure the models directory exists"""
    if not os.path.exists(MODEL_DIRECTORY):
        os.makedirs(MODEL_DIRECTORY)
        logger.info(f"Created directory {MODEL_DIRECTORY}")

class TrajectoryPredictor:
    """
    AI model to predict satellite trajectories based on historical data
    """
    
    def __init__(self):
        """Initialize the predictor"""
        self.position_model = None
        self.velocity_model = None
        self.scaler = None
        ensure_model_directory()
        self._load_or_create_models()
    
    def _load_or_create_models(self):
        """Load existing models or create new ones"""
        try:
            if os.path.exists(POSITION_MODEL_PATH) and os.path.exists(VELOCITY_MODEL_PATH) and os.path.exists(SCALER_PATH):
                logger.info("Loading existing prediction models")
                self.position_model = pickle.load(open(POSITION_MODEL_PATH, 'rb'))
                self.velocity_model = pickle.load(open(VELOCITY_MODEL_PATH, 'rb'))
                self.scaler = pickle.load(open(SCALER_PATH, 'rb'))
                logger.info("Models loaded successfully")
                return True
            else:
                logger.info("No existing models found, models will be created when trained")
                self.position_model = RandomForestRegressor(n_estimators=100, random_state=42)
                self.velocity_model = RandomForestRegressor(n_estimators=100, random_state=42)
                self.scaler = StandardScaler()
                return False
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.position_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.velocity_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.scaler = StandardScaler()
            return False
    
    def _prepare_features(self, trajectory_df):
        """
        Prepare features for the model
        
        Args:
            trajectory_df: DataFrame with trajectory data
        
        Returns:
            X: Features DataFrame
            y_pos: Position target values
            y_vel: Velocity target values
        """
        # Ensure required columns exist
        required_cols = ['x', 'y', 'z']
        if not all(col in trajectory_df.columns for col in required_cols):
            if all(col.upper() in trajectory_df.columns for col in required_cols):
                # Try uppercase column names
                trajectory_df.rename(columns={col.upper(): col for col in required_cols}, inplace=True)
            else:
                logger.error("Required columns x, y, z not found in trajectory data")
                raise ValueError("Required columns x, y, z not found in trajectory data")
        
        # Ensure timestamp column exists
        timestamp_cols = ['timestamp', 'time', 'date']
        timestamp_col = None
        for col in timestamp_cols:
            if col in trajectory_df.columns:
                timestamp_col = col
                break
        
        if timestamp_col is None:
            logger.error("No timestamp column found in trajectory data")
            raise ValueError("No timestamp column found in trajectory data")
        
        # Convert timestamp to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(trajectory_df[timestamp_col]):
            trajectory_df[timestamp_col] = pd.to_datetime(trajectory_df[timestamp_col])
        
        # Sort by timestamp
        trajectory_df = trajectory_df.sort_values(by=timestamp_col)
        
        # Calculate time differences in seconds
        trajectory_df['time_diff'] = (trajectory_df[timestamp_col] - trajectory_df[timestamp_col].min()).dt.total_seconds()
        
        # Calculate velocities (if not already present)
        if 'vx' not in trajectory_df.columns:
            trajectory_df['vx'] = trajectory_df['x'].diff() / trajectory_df['time_diff'].diff()
            trajectory_df['vy'] = trajectory_df['y'].diff() / trajectory_df['time_diff'].diff()
            trajectory_df['vz'] = trajectory_df['z'].diff() / trajectory_df['time_diff'].diff()
            
            # Replace NaN values in the first row
            trajectory_df[['vx', 'vy', 'vz']] = trajectory_df[['vx', 'vy', 'vz']].fillna(0)
        
        # Calculate accelerations
        trajectory_df['ax'] = trajectory_df['vx'].diff() / trajectory_df['time_diff'].diff()
        trajectory_df['ay'] = trajectory_df['vy'].diff() / trajectory_df['time_diff'].diff()
        trajectory_df['az'] = trajectory_df['vz'].diff() / trajectory_df['time_diff'].diff()
        
        # Replace NaN and inf values
        trajectory_df = trajectory_df.replace([np.inf, -np.inf], np.nan)
        trajectory_df = trajectory_df.fillna(0)
        
        # Create features: current position + velocity + acceleration + time
        features = ['time_diff', 
                   'x', 'y', 'z', 
                   'vx', 'vy', 'vz', 
                   'ax', 'ay', 'az']
        
        X = trajectory_df[features].copy()
        
        # Target variables: future positions and velocities (using current as proxy for training)
        y_pos = trajectory_df[['x', 'y', 'z']]
        y_vel = trajectory_df[['vx', 'vy', 'vz']]
        
        return X, y_pos, y_vel, trajectory_df[timestamp_col]
    
    def train(self, trajectory_df):
        """
        Train the prediction model on trajectory data
        
        Args:
            trajectory_df: DataFrame with trajectory data
            
        Returns:
            Dict with training metrics
        """
        logger.info("Training trajectory prediction model")
        
        try:
            # Prepare features and target variables
            X, y_pos, y_vel, _ = self._prepare_features(trajectory_df)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Split data
            X_train, X_test, y_pos_train, y_pos_test, y_vel_train, y_vel_test = train_test_split(
                X_scaled, y_pos, y_vel, test_size=0.2, random_state=42
            )
            
            # Train position model
            logger.info("Training position model")
            self.position_model.fit(X_train, y_pos_train)
            
            # Train velocity model
            logger.info("Training velocity model")
            self.velocity_model.fit(X_train, y_vel_train)
            
            # Evaluate models
            pos_pred = self.position_model.predict(X_test)
            vel_pred = self.velocity_model.predict(X_test)
            
            pos_mse = mean_squared_error(y_pos_test, pos_pred)
            pos_r2 = r2_score(y_pos_test, pos_pred)
            
            vel_mse = mean_squared_error(y_vel_test, vel_pred)
            vel_r2 = r2_score(y_vel_test, vel_pred)
            
            metrics = {
                'position_mse': pos_mse,
                'position_r2': pos_r2,
                'velocity_mse': vel_mse,
                'velocity_r2': vel_r2
            }
            
            # Save models
            pickle.dump(self.position_model, open(POSITION_MODEL_PATH, 'wb'))
            pickle.dump(self.velocity_model, open(VELOCITY_MODEL_PATH, 'wb'))
            pickle.dump(self.scaler, open(SCALER_PATH, 'wb'))
            
            logger.info(f"Models trained and saved. Position R² score: {pos_r2:.4f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise
    
    def predict(self, trajectory_df, days_ahead=7, interval_hours=1):
        """
        Predict future trajectory based on historical data
        
        Args:
            trajectory_df: DataFrame with trajectory data
            days_ahead: Number of days to predict into the future
            interval_hours: Time interval between predictions in hours
            
        Returns:
            DataFrame with predicted trajectory points
        """
        logger.info(f"Predicting trajectory {days_ahead} days ahead")
        
        try:
            # Check if model exists
            if self.position_model is None or self.velocity_model is None:
                logger.error("Models not trained. Please train the model first.")
                raise ValueError("Models not trained. Please train the model first.")
            
            # Prepare features
            X, _, _, timestamps = self._prepare_features(trajectory_df)
            
            # Get the last timestamp and values
            last_timestamp = timestamps.iloc[-1]
            last_values = X.iloc[-1].copy()
            
            # Calculate prediction points
            hours_ahead = days_ahead * 24
            prediction_points = hours_ahead // interval_hours + 1
            
            # Initialize results dataframe
            future_timestamps = [last_timestamp + timedelta(hours=interval_hours*i) for i in range(1, prediction_points+1)]
            predictions_df = pd.DataFrame({
                'timestamp': future_timestamps,
                'x': np.nan,
                'y': np.nan,
                'z': np.nan,
                'vx': np.nan,
                'vy': np.nan,
                'vz': np.nan,
                'prediction': True  # Flag to identify predicted points
            })
            
            # Iteratively predict future points
            current_features = last_values.values.reshape(1, -1)
            
            for i in range(prediction_points):
                # Scale features
                scaled_features = self.scaler.transform(current_features)
                
                # Predict position and velocity
                pos_pred = self.position_model.predict(scaled_features)
                vel_pred = self.velocity_model.predict(scaled_features)
                
                # Update predictions dataframe
                predictions_df.loc[i, 'x'] = pos_pred[0][0]
                predictions_df.loc[i, 'y'] = pos_pred[0][1]
                predictions_df.loc[i, 'z'] = pos_pred[0][2]
                predictions_df.loc[i, 'vx'] = vel_pred[0][0]
                predictions_df.loc[i, 'vy'] = vel_pred[0][1]
                predictions_df.loc[i, 'vz'] = vel_pred[0][2]
                
                # Update features for next prediction
                time_increment = interval_hours * 3600  # convert hours to seconds
                new_time = current_features[0][0] + time_increment
                
                # Calculate approximate acceleration
                if i > 0:
                    ax = (vel_pred[0][0] - current_features[0][4]) / time_increment
                    ay = (vel_pred[0][1] - current_features[0][5]) / time_increment
                    az = (vel_pred[0][2] - current_features[0][6]) / time_increment
                else:
                    ax = current_features[0][7]
                    ay = current_features[0][8]
                    az = current_features[0][9]
                
                # Update current features: time, x, y, z, vx, vy, vz, ax, ay, az
                current_features = np.array([[
                    new_time,
                    pos_pred[0][0], pos_pred[0][1], pos_pred[0][2],
                    vel_pred[0][0], vel_pred[0][1], vel_pred[0][2],
                    ax, ay, az
                ]])
            
            # Create a combined dataframe with historical + predicted data
            # First, extract relevant columns from historical data
            historical_df = trajectory_df[['timestamp', 'x', 'y', 'z']].copy()
            
            if 'vx' in trajectory_df.columns:
                historical_df['vx'] = trajectory_df['vx']
                historical_df['vy'] = trajectory_df['vy']
                historical_df['vz'] = trajectory_df['vz']
            else:
                historical_df['vx'] = 0
                historical_df['vy'] = 0
                historical_df['vz'] = 0
            
            historical_df['prediction'] = False
            
            # Combine historical and predicted data
            combined_df = pd.concat([historical_df, predictions_df], ignore_index=True)
            combined_df = combined_df.sort_values('timestamp')
            
            logger.info(f"Prediction complete. Generated {prediction_points} future trajectory points.")
            return combined_df
            
        except Exception as e:
            logger.error(f"Error predicting trajectory: {e}")
            raise
    
    def generate_smooth_trajectory(self, trajectory_df, prediction_df, points=200):
        """
        Generate a smooth trajectory curve using cubic splines
        
        Args:
            trajectory_df: Historical trajectory DataFrame
            prediction_df: Predicted trajectory DataFrame
            points: Number of points to generate for the smooth curve
            
        Returns:
            DataFrame with smooth trajectory points
        """
        try:
            # Combine historical and predicted data
            if 'prediction' not in trajectory_df.columns:
                trajectory_df['prediction'] = False
            
            combined_df = pd.concat([trajectory_df, prediction_df[prediction_df['prediction']==True]], 
                                    ignore_index=True)
            combined_df = combined_df.sort_values('timestamp')
            
            # Convert timestamps to numerical values (seconds since first point)
            first_timestamp = combined_df['timestamp'].min()
            combined_df['time_seconds'] = (combined_df['timestamp'] - first_timestamp).dt.total_seconds()
            
            # Create spline functions for each dimension
            time_values = combined_df['time_seconds'].values
            
            x_spline = CubicSpline(time_values, combined_df['x'].values)
            y_spline = CubicSpline(time_values, combined_df['y'].values)
            z_spline = CubicSpline(time_values, combined_df['z'].values)
            
            # Generate smooth points
            time_max = time_values[-1]
            time_smooth = np.linspace(0, time_max, points)
            
            # Create smooth dataframe
            smooth_df = pd.DataFrame({
                'time_seconds': time_smooth,
                'x': x_spline(time_smooth),
                'y': y_spline(time_smooth),
                'z': z_spline(time_smooth),
                'prediction': time_smooth > time_values[trajectory_df.shape[0] - 1]
            })
            
            # Convert back to timestamps
            smooth_df['timestamp'] = [first_timestamp + timedelta(seconds=t) for t in time_smooth]
            
            return smooth_df
            
        except Exception as e:
            logger.error(f"Error generating smooth trajectory: {e}")
            raise

def get_prediction_confidence(metrics, threshold=0.7):
    """
    Calculate confidence level of prediction based on model metrics
    
    Args:
        metrics: Dictionary of model metrics
        threshold: Minimum R² score for high confidence
        
    Returns:
        Confidence level string and score
    """
    if 'position_r2' not in metrics:
        return "Unknown", 0.0
    
    r2_score = metrics['position_r2']
    
    if r2_score > 0.9:
        return "Very High", r2_score
    elif r2_score > threshold:
        return "High", r2_score
    elif r2_score > 0.5:
        return "Medium", r2_score
    elif r2_score > 0.3:
        return "Low", r2_score
    else:
        return "Very Low", r2_score

def calculate_prediction_metrics(historical_df, prediction_df, actual_df=None):
    """
    Calculate metrics about the prediction quality
    
    Args:
        historical_df: DataFrame with historical trajectory data
        prediction_df: DataFrame with predicted trajectory data
        actual_df: Optional DataFrame with actual future trajectory data for validation
        
    Returns:
        Dictionary with prediction metrics
    """
    metrics = {}
    
    # Calculate metrics based on historical trend
    try:
        # Get historical velocity trend
        historical_df = historical_df.sort_values('timestamp')
        if 'vx' in historical_df.columns:
            avg_velocity = np.mean([
                np.mean(historical_df['vx'].values[-5:]),
                np.mean(historical_df['vy'].values[-5:]),
                np.mean(historical_df['vz'].values[-5:])
            ])
            metrics['avg_historical_velocity'] = avg_velocity
        
        # Calculate prediction extrapolation distance
        if prediction_df is not None and not prediction_df.empty:
            prediction_df = prediction_df[prediction_df['prediction']==True]
            if not prediction_df.empty:
                first_pred = prediction_df.iloc[0]
                last_pred = prediction_df.iloc[-1]
                
                # Calculate total distance covered in prediction
                dx = last_pred['x'] - first_pred['x']
                dy = last_pred['y'] - first_pred['y']
                dz = last_pred['z'] - first_pred['z']
                total_distance = np.sqrt(dx**2 + dy**2 + dz**2)
                metrics['prediction_distance_km'] = total_distance / 1000  # Convert to km
                
                # Calculate time span of prediction
                time_delta = (last_pred['timestamp'] - first_pred['timestamp']).total_seconds() / 3600  # hours
                metrics['prediction_timespan_hours'] = time_delta
        
        # If actual future data is provided, calculate prediction accuracy
        if actual_df is not None and not actual_df.empty:
            prediction_df = prediction_df[prediction_df['prediction']==True]
            
            # Find overlapping time period
            pred_min_time = prediction_df['timestamp'].min()
            pred_max_time = prediction_df['timestamp'].max()
            
            actual_overlap = actual_df[
                (actual_df['timestamp'] >= pred_min_time) &
                (actual_df['timestamp'] <= pred_max_time)
            ]
            
            if not actual_overlap.empty:
                # Interpolate predicted positions at actual timestamps
                # This requires a more complex approach with time alignment
                pass
    
    except Exception as e:
        logger.error(f"Error calculating prediction metrics: {e}")
    
    return metrics

# Utility function to check if prediction is possible
def can_predict_trajectory(df):
    """
    Check if the dataframe has enough data for prediction
    
    Args:
        df: Trajectory DataFrame
        
    Returns:
        Boolean indicating if prediction is possible, and reason if not
    """
    if df is None or df.empty:
        return False, "No trajectory data available"
    
    # Check minimum number of points
    if df.shape[0] < 10:
        return False, f"Insufficient data points ({df.shape[0]}). Need at least 10."
    
    # Check if required columns exist
    required_cols = ['x', 'y', 'z']
    if not all(col in df.columns for col in required_cols):
        if all(col.upper() in df.columns for col in required_cols):
            # Try uppercase column names
            return True, "OK"
        else:
            return False, "Missing position coordinates (x, y, z)"
    
    # Check if timestamp column exists
    timestamp_cols = ['timestamp', 'time', 'date']
    if not any(col in df.columns for col in timestamp_cols):
        return False, "Missing timestamp column"
    
    return True, "OK"