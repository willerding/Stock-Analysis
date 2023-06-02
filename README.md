This package is a financial statement analysis tool that uses  Alpha Vantage and Streamlit to fetch and display 
financial data for a given stock ticker. 
It defines several functions that fetch and standardize financial data for a given ticker, as well as functions that 
display the data in a tabular format.

To use this package, first download it to your computer.
Unzip the folder and navigate to the folder in your terminal using the `cd` command as follows:
``` 
cd path/to/folder
```
for example if the folder is in your Downloads folder, you would run the following command:

```
cd /Users/username/Downloads/Stock-Analysis-main
```
where username is your username on your computer.

When you are in the project folder, install the required packages by running the following command:

```
pip install -r requirements.txt
```

Lastly you will need to have an Alpha Vantage API key. 
To get a free Alpha Vantage API key, go to https://www.alphavantage.co/support/#api-key.

To add your API key to your Streamlit secrets.toml file, go to secrets.toml file in .streamlit folder in your project directory.
Update the value of `alpha_vantage` in secrets.toml file:
```
alpha_vantage = "XXXXXXXXXXXXXXXX"
```
where xxxxxxxxxxxxxxxx is your API key.

You are now ready to use the tool. To run the tool, run the following command in your terminal:
```
streamlit run main.py
```

This app is for educational purposes only. It is not intended to provide investment advice.
The project aims to bring an interactive financial statement analysis tool to the classroom.
This project can also be used to teach students how to use Streamlit to build interactive data science applications.

**Note**: This project is still in development.

The project also uses OpenAI's ChatGPT to summarize news articles about a given stock ticker.
To use that feature you will need an OpenAI API key which you can get for free at https://beta.openai.com/.
