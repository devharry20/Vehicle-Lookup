# Vehicle Lookup

This project leverages the UK DVSA [MOT History API](https://documentation.history.mot.api.gov.uk/) to retrieve basic vehicle information and comprehensive MOT data. The gathered data is then formatted and presented in a PDF file. To use the API, you must apply for access and follow the steps outlined in the API documentation to obtain the necessary authorization details for making requests.

## Installation

To run this project on your local machine, follow these steps:

1. Clone or download the repository from [https://github.com/devharry20/Vehicle-Lookup](https://github.com/devharry20/Vehicle-Lookup).
2. Create a `.env` file and populate it with `API_KEY` and `AUTHORIZATION_KEY` fields
3. Install the required dependencies by running the command: `pip install -r requirements.txt`

## Important Notes
The API provides limited data for newer vehicles, which is why many model fields are optional. New vehicles are MOT-exempt for the first 3 years, so MOT data will not be available for them until after their first test.

## Example 
![Main image](main-info.png)
![Second image](mot-info.png)
