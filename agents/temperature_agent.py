# temperature_agent.py (updated)
class TemperatureAgent:
    """Converts temperature values in the context from Kelvin to Celsius and Fahrenheit."""
    def run(self, context):
        if "weather" in context and isinstance(context["weather"], dict):
            weather = context["weather"]
            main = weather.get("main", {})
            # Convert all temperature fields to Celsius and Fahrenheit
            for key in ["temp", "feels_like", "temp_min", "temp_max"]:
                if key in main and main[key] is not None:
                    # Convert from Kelvin to Celsius and Fahrenheit
                    temp_k = main[key]
                    temp_c = round(temp_k - 273.15, 2)
                    temp_f = round((temp_c * 9/5) + 32, 2)
                    
                    # Store both units in the context
                    main[key + "_c"] = temp_c
                    main[key + "_f"] = temp_f
            
            # Create a readable weather summary
            desc = ""
            if "weather" in weather and isinstance(weather["weather"], list) and weather["weather"]:
                desc = weather["weather"][0].get("description", "").capitalize()
            
            # Store formatted temperatures
            context["weather_summary"] = (
                f"{desc} with a temperature of {main['temp_f']}°F "
                f"({main['temp_c']}°C), feels like {main['feels_like_f']}°F"
            )
            
            # Update context with converted values
            weather["main"] = main
            context["weather"] = weather
        return context