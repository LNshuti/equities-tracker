![image](https://github.com/LNshuti/equities-tracker/assets/13305262/34269ca9-8762-46a6-8e7a-c6d76314eabc)


<img src="https://github.com/LNshuti/equities-tracker/assets/13305262/34269ca9-8762-46a6-8e7a-c6d76314eabc" alt="image" width="200" height="200"/>

# Stock Analysis and Visualization Application

## [Prototype](https://huggingface.co/spaces/LeonceNsh/active-equities)

![image](https://github.com/LNshuti/equities-tracker/assets/13305262/ea270ec3-f0be-4b62-b31f-43eb4885d770)


This application pulls and visualises historical stock data and technical indicators for selected companies. With this app, users can analyze stocks through various technical indicators such as Simple Moving Averages (SMA), Relative Strength Index (RSI), and Trailing Annual Returns.

## Dependencies 
* Yahoo Finance data via [yfinance](https://pypi.org/project/yfinance)
* matplotlib
* gradio

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

1. **Select one or multiple** companies such as Apple, Microsoft, and Amazon.
2. **Select technical indicators** like Simple Moving Average **(SMA 55, SMA 200)**, Relative Strength Index **(RSI)**, and Moving Average Convergence Divergence **(MACD)**.
3. **Generate Plots**: in the interactive gallery, displaying the selected indicators for the chosen companies.

---

Thank you for your interest in our technical trading analysis tool. How can we make this tool more useful for you? 

Please take a moment to answer the following 3 question survey.
### [Google Form](https://docs.google.com/forms/d/e/1FAIpQLScNnM8CAuOINnoYiVPzwaf0dM8TzAD1CjEJgcbO-mfAKTSQtg/viewform?usp=sharing)
