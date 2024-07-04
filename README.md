# Stock Analysis and Visualization Application

This application fetches and visualises historical stock data and technical indicators for selected companies. Using Yahoo Finance data, it allows users to analyze stocks through various technical indicators such as Simple Moving Averages (SMA), Relative Strength Index (RSI), Moving Average Convergence Divergence (MACD), and Trailing Annual Returns.

## Features

- **Fetch Historical Data**: Retrieve historical stock data and market capitalization using Yahoo Finance.
- **Technical Indicators**: Calculate and plot technical indicators including SMA, RSI, MACD, and Trailing Annual Returns.
- **Interactive Plots**: Visualize data with interactive plots using Gradio.
- **Asynchronous Data Fetching**: Efficiently fetch data asynchronously for improved performance.
- **Caching**: Utilize caching to store data with a Time-To-Live (TTL) of one day, reducing redundant data fetches.

### Gradio Interface

- **Select Companies**: Choose one or multiple companies from the provided list.
- **Select Indicators**: Choose one or multiple technical indicators to plot.
- **Select All Indicators**: Option to select or deselect all available technical indicators.
- **View Plots**: Interactive gallery to view and analyze the generated plots.

## Example Workflow

1. **Select Companies**: Choose companies such as Apple, Microsoft, and Amazon.
2. **Select Indicators**: Choose technical indicators like SMA, RSI, or MACD.
3. **Generate Plots**: View the generated plots in the interactive gallery, displaying the selected indicators for the chosen companies.

## Code Overview

- **Global Configuration**: Define global settings and ticker mappings.
- **Data Fetching**: Functions to fetch historical stock data both synchronously and asynchronously.
- **Technical Indicator Calculation**: Functions to compute various technical indicators.
- **Plotting**: Functions to create and convert plots to images.
- **Gradio Interface**: Functions to launch and manage the Gradio interface for user interaction.

