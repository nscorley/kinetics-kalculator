import pandas as pd
from scipy.stats import linregress

def convert_to_concentration_using_standard_curves(df: pd.DataFrame, slope: float, y_intercept: float) -> None:
    """
    Convert the 'value' column in the DataFrame to concentration units using the provided slope and y-intercept
    of the standard curve.

    NOTE: Only support linear standard curves of the form y = mx + c.
    
    Args:
        df (pd.DataFrame): A DataFrame containing a 'value' column.
        slope (float): The slope of the standard curve.
        y_intercept (float): The y-intercept of the standard curve.
    
    Returns:
        None: The DataFrame is modified in-place.
    
    Raises:
        ValueError: If the DataFrame does not contain the required 'value' column.
    
    Example:
        >>> df = pd.DataFrame({'value': [1, 2, 3, 4, 5]}) # E.g., units of absorbance
        >>> convert_to_concentration_using_standard_curves(df, 2, 1)
        >>> df
           value
        0    0.5
        1    1.0
        2    1.5
        3    2.0
        4    2.5
    """
    # Ensure the DataFrame contains the required 'value' column
    if 'value' not in df.columns:
        raise ValueError("DataFrame must contain a 'value' column.")

    # Apply the conversion using the standard curve parameters
    df['value'] = df['value'].apply(lambda x: (x - y_intercept) / slope)

def filter_by_time_range(df: pd.DataFrame, lower_bound: float, upper_bound: float) -> pd.DataFrame:
    """
    Filter the DataFrame to only include rows where the 'time' column is within the specified range.
    
    Args:
        df (pd.DataFrame): A DataFrame containing a 'time' column.
        lower_bound (float): The lower bound of the time range.
        upper_bound (float): The upper bound of the time range.
    
    Returns:
        pd.DataFrame: A new DataFrame containing only the rows within the specified time range.
    
    Raises:
        ValueError: If the DataFrame does not contain the required 'time' column.
    """
    # Ensure the DataFrame contains the required 'time' column
    if 'time' not in df.columns:
        raise ValueError("DataFrame must contain a 'time' column.")

    # Apply the filter to include only rows within the specified time range
    filtered_df = df[(df['time'] >= lower_bound) & (df['time'] <= upper_bound)]

    return filtered_df

def adjust_rates_for_background(df: pd.DataFrame, negative_control: str, epsilon: float, rate_column: str = "rate") -> None:
    """
    Adjusts the rates in the DataFrame to account for background rates using a specified negative control.
    
    Args:
        df (pd.DataFrame): A DataFrame containing a 'samples' column and a column for rates.
        negative_control (str): The value in the 'samples' column to identify negative control samples.
        epsilon (float): A small positive value to replace any negative rates after background adjustment.
        rate_column (str): The name of the column containing the rates to be adjusted. Default is 'rate'.
    
    Returns:
        None: The DataFrame is modified in-place.
    
    Raises:
        ValueError: If the DataFrame does not contain the required columns.
    """
    # Ensure the DataFrame contains the required columns
    if 'samples' not in df.columns or rate_column not in df.columns:
        raise ValueError("DataFrame must contain 'samples' and the specified rate column.")

    # Calculate the mean background rate from negative control samples
    background_rate_mean = df[df['samples'] == negative_control][rate_column].mean()

    # Subtract the background rate from all rates
    df[f"{rate_column}_minus_background"] = df[rate_column] - background_rate_mean

    # Clip any negative rates to epsilon
    df.loc[df[f"{rate_column}_minus_background"] < 0, f"{rate_column}_minus_background"] = epsilon

def fit_line(group: pd.DataFrame, x_column: str, y_column: str) -> pd.Series:
    """
    Fits a linear model to the data in the specified group using the given x and y columns.

    Args:
        group (pd.DataFrame): A DataFrame group containing the data to fit.
        x_column (str): The name of the column to use as the independent variable.
        y_column (str): The name of the column to use as the dependent variable.

    Returns:
        pd.Series: A Series containing the slope (rate), intercept, and other statistics from the linear regression.
            - "rate": The slope of the fitted line.
            - "intercept": The y-intercept of the fitted line.
            - "r_value": The correlation coefficient.
            - "p_value": The two-sided p-value for a hypothesis test whose null hypothesis is that the slope is zero.
            - "std_err": The standard error of the estimated gradient.
    """
    # Perform linear regression using scipy's linregress
    slope, intercept, r_value, p_value, std_err = linregress(group[x_column], group[y_column])

    # Return the results as a pandas Series
    return pd.Series({
        "rate": slope,
        "intercept": intercept,
        "r_value": r_value,
        "p_value": p_value,
        "std_err": std_err
    })

def add_rate_column(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    group_columns: list,
    columns_to_return: list = ['rate']
) -> pd.DataFrame:
    """
    Adds specified columns to the DataFrame by fitting a linear model to the specified x and y columns for each group.

    Args:
        df (pd.DataFrame): A DataFrame containing the data to fit.
        x_column (str): The name of the column to use as the independent variable.
        y_column (str): The name of the column to use as the dependent variable.
        group_columns (list): A list of columns to group by before fitting the linear model.
        columns_to_return (list): A list of columns to retain in the final DataFrame. Default is ['rate'].

    Returns:
        pd.DataFrame: A new DataFrame with specified columns added, representing the results of the linear fit for each group.
    """
    # Apply the fit_line function to each group and reset index
    df_fits = df.groupby(group_columns).apply(fit_line, x_column=x_column, y_column=y_column).reset_index()

    # Filter the DataFrame to only include the specified columns
    df_fits = df_fits[group_columns + columns_to_return]

    return df_fits