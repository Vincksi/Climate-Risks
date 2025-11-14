# CO2 Emissions Prediction for China's Steel Industry

## Project Overview
This project focuses on analyzing and predicting CO2 emissions from China's steel industry using plant-level production data. It includes data processing, visualization, and predictive modeling to forecast future emissions trends for different steel companies in China.

## Project Structure
- [china_emissions_prediction.ipynb](cci:7://file:///c:/Users/kerri/OneDrive/Documents/Travail/AIDAMS/ESSEC%20Y3/Research%20&%20Emerging%20Topics/Labs/Lab3%20-%20CO2%20Emissions%20Prediction/china_emissions_prediction.ipynb:0:0-0:0): Main Jupyter notebook containing the data analysis and modeling
- [dashboard.py](cci:7://file:///c:/Users/kerri/OneDrive/Documents/Travail/AIDAMS/ESSEC%20Y3/Research%20&%20Emerging%20Topics/Labs/Lab3%20-%20CO2%20Emissions%20Prediction/dashboard.py:0:0-0:0): Interactive Streamlit dashboard for visualizing emissions and predictions
- [Plant-level-data-Global-Iron-and-Steel-Tracker.xlsx](cci:7://file:///c:/Users/kerri/OneDrive/Documents/Travail/AIDAMS/ESSEC%20Y3/Research%20&%20Emerging%20Topics/Labs/Lab3%20-%20CO2%20Emissions%20Prediction/Plant-level-data-Global-Iron-and-Steel-Tracker.xlsx:0:0-0:0): Primary dataset containing plant-level steel production data
- [owner_emissions_cleaned.csv](cci:7://file:///c:/Users/kerri/OneDrive/Documents/Travail/AIDAMS/ESSEC%20Y3/Research%20&%20Emerging%20Topics/Labs/Lab3%20-%20CO2%20Emissions%20Prediction/owner_emissions_cleaned.csv:0:0-0:0): Processed dataset with calculated CO2 emissions by company
- [Country-crude-steel-production.xlsx](cci:7://file:///c:/Users/kerri/OneDrive/Documents/Travail/AIDAMS/ESSEC%20Y3/Research%20&%20Emerging%20Topics/Labs/Lab3%20-%20CO2%20Emissions%20Prediction/Country-crude-steel-production.xlsx:0:0-0:0): Supplementary data on steel production by country

## Key Features
- Data processing and cleaning of steel production data
- Calculation of CO2 emissions based on production methods (BF-BOF, EAF, etc.)
- Time series analysis of emissions trends
- Polynomial regression modeling for emissions forecasting
- Interactive dashboard for exploring company-specific emissions and predictions

## Technologies Used
- Python 3.x
- Pandas for data manipulation
- NumPy for numerical operations
- Matplotlib and Seaborn for data visualization
- Scikit-learn for machine learning models
- Streamlit for the interactive dashboard

## Getting Started

### Prerequisites
- Python 3.7+
- Required Python packages (pandas, numpy, matplotlib, seaborn, scikit-learn, streamlit)


### Running the Dashboard
1. Ensure all dependencies are installed
2. Run the Streamlit dashboard with:
   ```bash
   streamlit run dashboard.py
   ```
3. Open the provided local URL in your web browser
4. Upload the processed CSV file to explore the data and predictions

## Methodology
1. **Data Collection**: Gathered plant-level steel production data from Global Energy Monitor
2. **Data Processing**:
   - Cleaned and transformed raw data
   - Calculated CO2 emissions based on production methods
   - Aggregated data by company and year
3. **Analysis**:
   - Explored trends in steel production and emissions
   - Identified key contributors to CO2 emissions
   - Developed predictive models for future emissions
4. **Visualization**:
   - Created interactive visualizations of historical and predicted emissions
   - Built an interactive dashboard for data exploration