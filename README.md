# Facebook Marketplace Auto Lister

Automated tool for listing vehicles on Facebook Marketplace and Groups.

## Features

- Automated vehicle listing on Facebook Marketplace
- Anti-detection technology to bypass Facebook's bot detection
- Human-like interaction patterns
- Bulk listing from Excel spreadsheet
- Image upload support
- Automated form filling for vehicle details

## Setup

1. Install requirements:
   ```
   pip install -r requirements.txt
   ```

2. Add Facebook account details to `accounts.json`:
   ```json
   {
     "accounts": [
       {
         "email": "your_email@example.com",
         "password": "your_password"
       }
     ]
   }
   ```

3. Add vehicle listings to `products.xlsx` with the following columns:
   - images: Comma-separated image filenames from the 'images' folder
   - vehicle_type: Type of vehicle (Car/Truck, Motorcycle, etc.)
   - year: Vehicle year
   - make: Vehicle make/brand
   - model: Vehicle model
   - mileage: Vehicle mileage
   - price: Listing price
   - fuel_type: Fuel type (Gasoline, Diesel, etc.)
   - transmission: Transmission type
   - body_style: Body style (Sedan, SUV, etc.)
   - exterior_color: Exterior color
   - interior_color: Interior color
   - condition: Condition of the vehicle (New, Used, etc.)
   - description: Detailed description of the vehicle

4. Place vehicle images in the `images` folder.

## Usage

Run the script:
```
python app.py
```

When prompted, solve any CAPTCHA or security challenges to complete the login process.

## Disclaimer

This tool is for educational purposes only. Users are responsible for complying with Facebook's Terms of Service. 