# Hack&Roll 2024
![Chioset Logo](https://github.com/emery97/HackAndRoll/blob/main/HackAndRoll/front-end/logo.png)

Chioset is a full-stack application designed to help users make quick, informed outfit decisions. By integrating weather data, wardrobe management, and Augmented Reality (AR), Chioset offers a fun and interactive way to choose outfits based on real-time conditions and personal style.

## Inspiration
Chioset was born from the daily challenge of deciding what to wear, considering factors like weather, occasion, and personal preferences. We wanted to develop a solution that not only saves time but also makes the process of dressing up more engaging. The addition of Augmented Reality was inspired by the idea of letting users visualize their outfits in real-time, creating a bridge between imagination and reality.

## What It Does
Chioset simplifies the decision-making process by:
- **Recommending outfits** based on the current weather conditions (e.g., sunny, rainy, cold).
- Categorizing clothes in your **personal wardrobe** and using that data to generate a tailored **“Outfit of the Day.”**
- Offering an **AR experience** where users can virtually try on clothes, helping them visualize how outfits will look in real life.
- Providing real-time **weather updates** that influence outfit choices.

## How We Built It
Chioset is a full-stack application developed with the following technologies:
- **Frontend**: React.js was used to create an interactive and responsive user interface.
- **Backend**: Node.js powers the server and handles API requests.
- **Database**: MongoDB stores wardrobe data, including images, attributes, and metadata.
- **Augmented Reality**: TensorFlow.js was integrated to offer real-time AR outfit visualization.
- **Weather Integration**: The WeatherAPI provides up-to-date weather conditions to influence outfit recommendations.
- **Image Processing**: We used Removebg to remove backgrounds from clothing images for a cleaner AR experience.

## Challenges We Ran Into
- **Integrating AR**: The most significant challenge was incorporating Augmented Reality in a seamless way. TensorFlow.js posed some difficulties with real-time processing, but we overcame this by optimizing the experience for smoother interaction.
- **Weather Data Reliability**: Ensuring that weather data was both accurate and timely required careful handling of API calls and error management.

## Accomplishments We're Proud Of
- Successfully integrating **Augmented Reality** into the platform to allow users to virtually try on outfits.
- The seamless interaction between the **weather API** and wardrobe data to create **personalized outfit suggestions**.
- Our ability to quickly build a **full-stack application** that is not only functional but also user-friendly and engaging.

## What We Learned
- We gained valuable experience in integrating **Augmented Reality** using TensorFlow.js, learning about its capabilities and limitations.
- The project taught us how to manage **live weather data** and incorporate it into an app for real-time functionality.
- We also learned how to efficiently store and retrieve **metadata and images** from a MongoDB database.

## What's Next for Chioset
- **Enhanced AR Experience**: We're planning to integrate more advanced features for a more accurate 'try-on' experience using Outfit Anyone.
- **Improved Weather Integration**: We want to incorporate more granular weather details (e.g., wind speed, humidity) to suggest even more customized outfits.
- **User Accounts**: Allow users to create profiles and save their wardrobe, favorite outfits, and style preferences for a more personalized experience.

## Built With
- **Frontend**: React.js
- **Backend**: Node.js
- **Database**: MongoDB
- **Augmented Reality**: TensorFlow.js
- **Weather Data**: WeatherAPI
- **Image Background Removal**: Removebg
