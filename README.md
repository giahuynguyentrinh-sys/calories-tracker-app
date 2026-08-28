# Calories Tracker

A simple command-line calorie tracking application written in Python.

## v1.0.0 — Initial Release

The first version focuses on the core calorie-tracking functionality:

* Create and save a user profile
* Calculate BMR and TDEE
* Set a daily calorie target based on the user's goal
* Calculate daily protein target
* Add food entries by food name and weight
* Automatically calculate protein, carbohydrates, fat, and calories
* View today's food log
* Store user data and food logs using JSON files
* Load saved user data when starting the application

## Current Structure

### `entry`

Represents a food entry.

An entry stores:

* Food name
* Weight
* Entry date

The nutritional values are calculated automatically using `fooddatabase.json`.

### `user`

Stores the user's basic information and calculates:

* BMR
* TDEE
* Daily calorie target
* Daily protein target

### Data Storage

The application currently uses JSON files:

* `fooddatabase.json` — food nutrition database
* `personstat.json` — saved user profile
* `log.json` — saved food entries

## Running the Program

Make sure Python is installed, then run:

```bash
python calorie_tracker.py
```

## Roadmap

### v2.0.0

Expand the tracker with additional features such as:

* Better food and meal management
* More detailed food history
* Improved user experience
* Additional tracking features

### v3.0.0

Introduce statistics and smarter recommendations based on the user's tracking data.

Possible features:

* Nutrition statistics
* Calorie and protein trends
* Progress tracking
* Personalized recommendations
* AI-assisted insights
