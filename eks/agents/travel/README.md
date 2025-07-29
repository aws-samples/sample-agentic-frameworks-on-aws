# Travel Planning Multi-Agent System

# Coming soon

A demonstration of how multiple AI agents collaborate to create personalized travel itineraries. This system showcases the practical implementation of multi-agent architecture for real-world applications.

## System Overview

This system consists of three specialized agents working together:

1. **Travel Agent (Main Coordinator)**
   - Coordinates between other agents
   - Creates final itinerary
   - Handles user interaction

2. **Weather Agent**
   - Provides weather forecasts
     - The forecasts contains if condition is appropriate for outdoor activity or not 
   - Alerts about weather conditions

3. **Activities Agent**
   - Maintains database of local activities
   - Provides activity recommendations
   - Includes operating hours and locations

## How It Works

1. User submits a travel query
2. Travel Agent processes the request
3. Weather Agent checks forecast
4. Activities Agent suggests suitable options
5. Travel Agent compiles final itinerary

## Example Usage

### Sample Prompt:
```
I'm will be in San Francisco starting tomorrow, I have 3 days free that I want to have some fun and do activities, it's my first time there. Suggest a daily itinerary of activities and don't forget to take weather conditions when recommending an activity.
```

### Expected Information in Response:
- Daily weather forecast
- Activity recommendations per day
- Timing for each activity
- Indoor/outdoor alternatives
- Transportation suggestions
- Estimated costs (optional)


## Features

- Weather-aware planning
- Dynamic activity scheduling
- Personalized recommendations

## Integration Notes

- Works in conjunction with Weather Agent for weather-appropriate suggestions
- Coordinates with Travel Agent for timing and scheduling
- Can adapt recommendations based on real-time conditions

## Capabilities

- Natural language understanding
- Context-aware recommendations
- Time-based activity planning
- Weather-conscious suggestions
- Price range considerations
- Local insights integration

## Limitations

- Weather forecasts limited to 7 days
- Activities based on available database
- Operating hours may vary

## Future Enhancements

- Restaurant recommendations
- Public transportation integration
- Real-time booking capabilities
- User preference learning
