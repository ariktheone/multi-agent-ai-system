#main.py
import json, dotenv, requests, time, sys
import datetime
import os
from textwrap import fill
from agents.planner_agent import PlannerAgent
from agents.api_fetch_agent import APIFetchAgent
from agents.summarizer_agent import SummarizerAgent
from agents.news_agent import NewsAgent
from agents.wikipedia_agent import WikipediaAgent
from agents.holidays_agent import HolidaysAgent
from agents.air_quality_agent import AirQualityAgent
from agents.finance_agent import FinanceAgent
from agents.books_agent import BooksAgent
from agents.covid_agent import COVIDAgent
from agents.sports_agent import SportsAgent
from agents.movies_agent import MoviesAgent
from agents.sentiment_agent import SentimentAgent
from agents.factcheck_agent import FactCheckAgent
from agents.exchange_rate_agent import ExchangeRateAgent
from agents.weather_alerts_agent import WeatherAlertsAgent
from agents.wikipedia_summary_agent import WikipediaSummaryAgent
from utils.entity_extractor import extract_entities
from concurrent.futures import ThreadPoolExecutor, as_completed
from agents.health_agent import HealthAgent
from agents.heatcheck_agent import HeatCheckAgent
from agents.pollution_agent import PollutionAgent
from agents.traffic_agent import TrafficAgent
from agents.currency_agent import CurrencyAgent
from agents.event_agent import EventAgent
from agents.job_market_agent import JobMarketAgent
from agents.temperature_agent import TemperatureAgent
from agents.base_agent import BaseAgent
from utils.context import AgentContext
import logging

# Terminal color codes
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

# Text width for wrapping
TEXT_WIDTH = 80

dotenv.load_dotenv()

with open('configs/agents.json') as f:
    configs = json.load(f)

def load_agents(configs):
    # Dynamically load agents, can be extended for plugin support
    return {
        "weather": APIFetchAgent(configs["weather"]),
        "spacex_next": APIFetchAgent(configs["spacex_next"]),
        "news": NewsAgent(),
        "summarizer": SummarizerAgent(),
        "wikipedia": WikipediaAgent(),
        "holidays": HolidaysAgent(),
        "air_quality": AirQualityAgent(),
        "finance": FinanceAgent(),
        "books": BooksAgent(),
        "covid": COVIDAgent(),
        "sports": SportsAgent(),
        "movies": MoviesAgent(),
        "sentiment": SentimentAgent(),
        "fact_check": FactCheckAgent(),
        "exchange_rate": ExchangeRateAgent(),
        "weather_alerts": WeatherAlertsAgent(),
        "wikipedia_summary": WikipediaSummaryAgent(),
        "health": HealthAgent(),
        "heat_check": HeatCheckAgent(),
        "pollution": PollutionAgent(),
        "traffic": TrafficAgent(),
        "currency": CurrencyAgent(),
        "events": EventAgent(),
        "job_market": JobMarketAgent(),
        "temperature": TemperatureAgent(),
    }

available_agents = load_agents(configs)

planner = PlannerAgent()

def print_section(title, color=CYAN):
    title = f" {title} "
    print(f"\n{color}{BOLD}{title.center(TEXT_WIDTH, '=')}{RESET}")

def print_agent_step(agent_name, step, color=YELLOW):
    print(f"{color}{BOLD}[{agent_name}]{RESET} {step}")

def wrap_text(text, indent=0, width=TEXT_WIDTH):
    """Wrap text with proper indentation and line breaks"""
    return fill(text, width=width, initial_indent=' '*indent, subsequent_indent=' '*indent)

def print_paragraph(title, content, color=RESET, indent=0):
    """Print formatted paragraph with title and wrapped content"""
    if not content:
        return
    print(f"{BOLD}{title}:{RESET}")
    print(wrap_text(content, indent))
    print()

def evaluate_agent_trajectory(context, trajectory_log):
    """Print and log the agent execution trajectory and context enrichment."""
    print_section("AGENT TRAJECTORY & DATA ENRICHMENT", BLUE)
    for step in trajectory_log:
        agent = step["agent"]
        keys_before = step["context_keys_before"]
        keys_after = step["context_keys_after"]
        new_keys = set(keys_after) - set(keys_before)
        print(f"{BOLD}{agent}:{RESET} Added keys: {GREEN}{', '.join(new_keys) if new_keys else 'None'}{RESET}")
        if step.get("error"):
            print(f"  {RED}Error:{RESET} {step['error']}")
    print()

def evaluate_planner_routing(old_chain, new_chain):
    """Show planner's routing logic and changes to the agent chain."""
    print_section("PLANNER ROUTING EVALUATION", MAGENTA)
    print(f"{BOLD}Previous agent chain:{RESET} {', '.join(old_chain)}")
    print(f"{BOLD}New agent chain:{RESET} {GREEN}{', '.join(new_chain)}{RESET}")
    if old_chain == new_chain:
        print(f"{YELLOW}No changes to agent chain by planner.{RESET}")
    else:
        print(f"{GREEN}Planner refined the agent chain for better goal satisfaction.{RESET}")
    print()

def execute_chain(chain, goal, max_iterations=3):
    context = AgentContext(
        goal=goal,
        start_time=time.time(),
        entities=extract_entities(goal).get("entities", []),
        entity_key=extract_entities(goal).get("entity_key", "general"),
        agent_chain=chain
    )
    satisfied = False
    iteration = 1
    trajectory_log = []

    while not satisfied and iteration <= max_iterations:
        print_section(f"Execution Iteration {iteration}", MAGENTA)
        context_snapshot_before = dict(context.data)  # For trajectory tracking

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(available_agents[agent_name].run, context.data): agent_name for agent_name in chain}
            for future in as_completed(futures):
                agent_name = futures[future]
                keys_before = list(context.data.keys())
                try:
                    result = future.result()
                    # --- FIX: update context.data, not context ---
                    if agent_name == "spacex_next" and isinstance(result, dict):
                        context.data.update(result)
                        launchpad_id = result.get("launchpad")
                        if launchpad_id:
                            pad_resp = requests.get(f"https://api.spacexdata.com/v4/launchpads/{launchpad_id}")
                            if pad_resp.ok:
                                pad = pad_resp.json()
                                if pad.get("locality"):
                                    context.data["launch_location"] = pad["locality"]
                                if pad.get("latitude") and pad.get("longitude"):
                                    context.data["lat"] = pad["latitude"]
                                    context.data["lon"] = pad["longitude"]
                    elif agent_name == "summarizer":
                        context.data["summary"] = result
                    elif agent_name == "sentiment":
                        context.data["sentiment_score"] = result.get("score", 0)
                        context.data["sentiment"] = result.get("label", "Neutral")
                        context.data["sentiment_reasoning"] = result.get("reasoning", "")
                    elif isinstance(result, dict):
                        context.data.update(result)
                    else:
                        context.data[agent_name] = result

                    print_agent_step(agent_name, "Completed successfully", GREEN)
                    keys_after = list(context.data.keys())
                    trajectory_log.append({
                        "agent": agent_name,
                        "context_keys_before": keys_before,
                        "context_keys_after": keys_after,
                        "error": None
                    })
                except Exception as e:
                    logging.error(f"Agent {agent_name} failed: {str(e)}", exc_info=True)
                    context.errors.append(f"{agent_name}: {str(e)}")
                    print_agent_step(agent_name, f"Error: {str(e)}", RED)
                    keys_after = list(context.data.keys())
                    trajectory_log.append({
                        "agent": agent_name,
                        "context_keys_before": keys_before,
                        "context_keys_after": keys_after,
                        "error": str(e)
                    })
                time.sleep(0.1)

        # --- FIX: use context.data.get(...) ---
        summary = context.data.get("summary", "")
        if summary and len(summary.split()) > 30:
            satisfied = True
            feedback = "Goal satisfied: summary generated"
        elif "error" in context.data:
            satisfied = False
            feedback = f"Goal not satisfied due to error: {context.data['error']}"
        else:
            satisfied = False
            feedback = "Goal not satisfied: summary missing or incomplete"

        print_section("Evaluation", YELLOW)
        print(f"{BOLD}{feedback}{RESET}")

        # Show agent trajectory and context enrichment
        evaluate_agent_trajectory(context, trajectory_log)

        if not satisfied:
            print_section("Refining Agent Chain", RED)
            new_chain = planner.plan(goal, list(available_agents.keys()))
            evaluate_planner_routing(chain, new_chain)
            if new_chain != chain:
                chain = new_chain
                print(f"{BOLD}New agent chain:{RESET} {GREEN}{chain}{RESET}")
            else:
                print(f"{YELLOW}No changes to agent chain{RESET}")
            iteration += 1

    context.data["processing_time"] = time.time() - context.start_time
    context.data["trajectory_log"] = trajectory_log  # Save for later reporting
    return context.data

# main.py (update generate_comprehensive_analysis function)
# main.py (update generate_comprehensive_analysis function)
def generate_comprehensive_analysis(context, goal):
    """Generate deep paragraph-style analysis"""
    analysis = []
    goal_lower = goal.lower()
    
    # 1. Executive Summary
    if "summary" in context and context["summary"]:
        # Clean up summary text
        clean_summary = context["summary"]
        if "📊 In-depth Analytical Summary (Cohere):" in clean_summary:
            clean_summary = clean_summary.replace("📊 In-depth Analytical Summary (Cohere):", "").strip()
        analysis.append(("EXECUTIVE OVERVIEW", clean_summary))
    else:
        analysis.append(("EXECUTIVE OVERVIEW", "No summary was generated, but all available data is presented below."))

    # 2. Thematic Analysis
    thematic_analysis = ""
    
    # Environmental Factors
    env_factors = []
    weather_summary = ""
    if "weather" in context and isinstance(context["weather"], dict):
        weather = context["weather"]
        desc = ""
        if "weather" in weather and isinstance(weather["weather"], list) and weather["weather"]:
            desc = weather["weather"][0].get("description", "").capitalize()
        main = weather.get("main", {})
        temp_k = main.get("temp")
        feels_like_k = main.get("feels_like")
        humidity = main.get("humidity", "N/A")
        wind = weather.get("wind", {}).get("speed", "N/A")

        temp_c = kelvin_to_celsius(temp_k)
        temp_f = kelvin_to_fahrenheit(temp_k)
        feels_like_c = kelvin_to_celsius(feels_like_k)
        feels_like_f = kelvin_to_fahrenheit(feels_like_k)

        temp_str = f"{temp_k}K / {temp_c}°C / {temp_f}°F"
        feels_like_str = f"{feels_like_k}K / {feels_like_c}°C / {feels_like_f}°F"

        weather_summary = (
            f"{desc} with a temperature of {temp_str}, "
            f"feels like {feels_like_str}, "
            f"humidity {humidity}%, wind {wind} m/s."
        )
        env_factors.append(
            f"Weather: {desc}. Temperature: {temp_str} (feels like {feels_like_str}). "
            f"Humidity: {humidity}%. Wind: {wind} m/s."
        )
        # Inject for summarizer
        context["weather_summary"] = weather_summary
    
    if "air_quality" in context: 
        env_factors.append(f"Air quality index: {context['air_quality']}")
    if "pollution" in context: 
        env_factors.append(f"Pollution levels: {context['pollution']}")
    if "weather_alerts" in context: 
        alerts = context["weather_alerts"]
        if isinstance(alerts, list) and "No weather alerts" in str(alerts):
            env_factors.append("No weather alerts")
        else:
            env_factors.append(f"Weather alerts: {alerts}")
    
    if env_factors:
        thematic_analysis += "Environmental Context:\n"
        thematic_analysis += "The analysis of environmental factors reveals: " + ". ".join(env_factors) + "\n\n"
    
    # Health Insights
    health_insights = []
    if "health" in context: 
        health_data = context['health']
        if isinstance(health_data, list):
            health_insights = [str(item) for item in health_data]
        else:
            health_insights.append(str(health_data))
    
    if "covid" in context and any(word in goal_lower for word in ["covid", "pandemic"]): 
        covid_data = context['covid']
        if isinstance(covid_data, list):
            health_insights.extend(str(item) for item in covid_data)
        else:
            health_insights.append(str(covid_data))
    
    if health_insights:
        thematic_analysis += "Health Sector Analysis:\n"
        thematic_analysis += "Public health indicators show: " + ". ".join(health_insights) + "\n\n"
    
    # Economic Indicators
    econ_indicators = []
    if "finance" in context: 
        econ_indicators.append(f"Financial analysis of {len(context['finance'])} entities")
    if "exchange_rate" in context: 
        econ_indicators.append(f"Exchange rates: {context['exchange_rate']}")
    if "job_market" in context: 
        econ_indicators.append(f"Job market: {context['job_market']}")
    
    if econ_indicators:
        thematic_analysis += "Economic Landscape:\n"
        thematic_analysis += "The economic environment is characterized by: " + ", ".join(econ_indicators) + ". "
        sentiment = "positive" if context.get('sentiment_score', 0) > 0 else "cautious" if context.get('sentiment_score', 0) < 0 else "neutral"
        thematic_analysis += f"These indicators suggest {sentiment} economic prospects.\n\n"
    
    # Sentiment Analysis
    if "sentiment" in context:
        sentiment = context["sentiment"]
        thematic_analysis += f"Sentiment Analysis:\nOverall sentiment is assessed as {sentiment}. "
        if "sentiment_reasoning" in context:
            thematic_analysis += f"This assessment is based on: {context['sentiment_reasoning']}\n\n"
    
    if thematic_analysis:
        analysis.append(("THEMATIC ANALYSIS", thematic_analysis))
    
    # 3. Detailed Entity Analysis
    entity_analysis = []
    entities = context.get("entities", [])
    for entity in entities:
        entity_text = f"Analysis of {entity}:\n\n"
        
        # Financial Analysis
        if "finance" in context:
            for f in context["finance"]:
                if isinstance(f, dict) and entity.lower() in f.get("symbol", "").lower():
                    entity_text += f"Financial Performance: {f.get('symbol')} is currently trading at {f.get('price', 'N/A')} "
                    entity_text += f"with a market capitalization of {f.get('market_cap', 'N/A')}. "
                    if "reasoning" in f:
                        entity_text += f"Analytical assessment indicates: {f['reasoning']} "
                    entity_text += "\n\n"
        
        # News Analysis
        if "news" in context:
            entity_news = [n for n in context["news"] if entity.lower() in n.get("title", "").lower()]
            if entity_news:
                entity_text += "Recent Developments:\n"
                for news_item in entity_news[:5]:
                    entity_text += f"- {news_item.get('title', 'No title')} "
                    if "published" in news_item:
                        entity_text += f"({news_item['published']}) "
                    if "source" in news_item:
                        entity_text += f"[Source: {news_item['source']}]"
                    entity_text += "\n"
                entity_text += "\n"
        
        # Fact Verification
        if "fact_checks" in context:
            entity_facts = [f for f in context["fact_checks"] if entity.lower() in f.get("claim", {}).get("text", "").lower()]
            if entity_facts:
                entity_text += "Fact Verification Findings:\n"
                for fact in entity_facts:
                    rating = fact.get("rating", "Unrated")
                    entity_text += f"- Claim: '{fact.get('claim', {}).get('text', 'N/A')}' "
                    entity_text += f"was rated as '{rating}' with explanation: {fact.get('explanation', 'No explanation provided')}\n"
                entity_text += "\n"
        
        if len(entity_text) > len(f"Analysis of {entity}:\n\n"):
            entity_analysis.append((f"ENTITY ANALYSIS: {entity.upper()}", entity_text))
    
    if entity_analysis:
        for title, content in entity_analysis:
            analysis.append((title, content))
    
    # 4. Critical Insights
    critical_insights = []
    
    if "finance" in context and "news" in context:
        critical_insights.append("Financial metrics should be evaluated alongside recent news events for complete context.")
    
    if "fact_checks" in context:
        false_claims = [f for f in context["fact_checks"] if f.get("rating") in ["False", "Misleading"]]
        if false_claims:
            critical_insights.append(f"Caution advised: {len(false_claims)} unverified/misleading claims detected.")
    
    if "weather_alerts" in context and "No weather alerts" not in str(context["weather_alerts"]):
        critical_insights.append(f"Weather alerts indicate potential disruptions: {context['weather_alerts']}")
    
    if not critical_insights:
        critical_insights.append("Analysis shows no critical anomalies requiring immediate attention.")
    
    analysis.append(("CRITICAL INSIGHTS", "\n".join([f"- {i}" for i in critical_insights])))
    
    # 5. Data Quality and Limitations
    data_quality = "Data Quality Assessment:\n"
    errors = context.get("errors", [])
    if errors:
        data_quality += f"Analysis encountered {len(errors)} operational issues. "
        data_quality += "Key limitations: " + ", ".join(errors[:3]) + ". "
        data_quality += "Consider these constraints when interpreting findings."
    else:
        data_quality += "All data sources validated successfully. "
        data_quality += "Findings represent a comprehensive assessment based on available information."
    
    analysis.append(("METHODOLOGY & LIMITATIONS", data_quality))
    
    # 6. Conclusions and Recommendations
    conclusions = "Synthesis of Findings:\n"
    conclusions += "Based on comprehensive analysis, key conclusions:\n"
    
    if "summary" in context:
        # Clean up summary text
        clean_summary = context["summary"]
        if "📊 In-depth Analytical Summary (Cohere):" in clean_summary:
            clean_summary = clean_summary.replace("📊 In-depth Analytical Summary (Cohere):", "").strip()
        conclusions += "- " + clean_summary.replace(". ", ".\n- ")[:500] + "\n"
    
    conclusions += "\nStrategic Recommendations:\n"
    if "sentiment_score" in context:
        if context["sentiment_score"] > 0.3:
            conclusions += "Positive indicators suggest opportunities for growth-oriented strategies."
        elif context["sentiment_score"] < -0.3:
            conclusions += "Challenging conditions recommend cautious approaches and risk mitigation."
        else:
            conclusions += "Neutral assessment suggests maintaining current strategies with careful monitoring."
    
    if "weather_alerts" in context and "No weather alerts" not in str(context["weather_alerts"]):
        conclusions += " Incorporate weather advisories into operational planning."
    
    analysis.append(("CONCLUSIONS & RECOMMENDATIONS", conclusions))
    
    return analysis

    
def print_detailed_report(context, goal):
    """Print professional report with deep paragraph-style analysis"""
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Report Header
    print_section("AI RESEARCH REPORT", BLUE)
    print(f"{BOLD}Research Goal:{RESET} {goal}")
    print(f"{BOLD}Date of Analysis:{RESET} {current_time}")
    print(f"{BOLD}Processing Metrics:{RESET} Completed in {context.get('processing_time', 0):.2f} seconds")
    print(f"{BOLD}Agent Workflow:{RESET} {', '.join(context.get('agent_chain', []))}\n")
    
    # Generate comprehensive analysis
    analysis = generate_comprehensive_analysis(context, goal)
    
    # Print each section with proper formatting
    section_texts = {}
    for section_title, section_content in analysis:
        print_section(section_title, CYAN)
        print(wrap_text(section_content, indent=2))
        print()
        section_texts[section_title] = section_content  # Collect for total summary

    # --- TOTAL SUMMARY SECTION ---
    print_section("TOTAL SUMMARY", GREEN)
    print(wrap_text(
        "This section provides a concise synthesis of all key findings, insights, and recommendations from the analysis above. Use this as a quick reference for decision-making.",
        indent=2
    ))
    print()

    # Synthesize from previous sections
    if "EXECUTIVE OVERVIEW" in section_texts:
        print(f"{BOLD}Executive Overview:{RESET}")
        print(wrap_text(section_texts["EXECUTIVE OVERVIEW"], indent=4))
        print()
        # Add word count
        word_count = len(section_texts["EXECUTIVE OVERVIEW"].split())
        print(f"{BOLD}Executive Overview Word Count:{RESET} {word_count}\n")
    if "THEMATIC ANALYSIS" in section_texts:
        print(f"{BOLD}Key Environmental & Thematic Insights:{RESET}")
        print(wrap_text(section_texts["THEMATIC ANALYSIS"], indent=4))
        print()
    if "CRITICAL INSIGHTS" in section_texts:
        print(f"{BOLD}Critical Insights:{RESET}")
        # Present each insight as a bullet point
        for line in section_texts["CRITICAL INSIGHTS"].split('\n'):
            if line.strip():
                print("    •", line.strip().lstrip('-').strip())
        print()
    if "CONCLUSIONS & RECOMMENDATIONS" in section_texts:
        print(f"{BOLD}Conclusions & Recommendations:{RESET}")
        print(wrap_text(section_texts["CONCLUSIONS & RECOMMENDATIONS"], indent=4))
        print()
    # --- END TOTAL SUMMARY ---

    # Footer
    print_section("END OF REPORT", BLUE)
    print(f"{BOLD}Report Generated By:{RESET} ADK Research Platform v3.0")
    print(f"{BOLD}Confidentiality:{RESET} This report contains privileged analysis for authorized use only\n")

def optimize_agent_selection(goal):
    """Select agents based on goal content for deep analysis"""
    goal_lower = goal.lower()
    base_agents = ["news", "wikipedia_summary", "sentiment", "summarizer"]
    
    # Entity-specific agents
    if "finance" in goal_lower or any(word in goal_lower for word in ["stock", "market", "investment"]):
        base_agents.insert(0, "finance")
        base_agents.insert(3, "fact_check")
    
    if "weather" in goal_lower or any(word in goal_lower for word in ["temperature", "forecast", "climate"]):
        base_agents.insert(0, "weather")
        base_agents.insert(1, "temperature")  # <-- Insert temperature agent after weather
        base_agents.insert(2, "air_quality")
        base_agents.insert(3, "weather_alerts")
    
    if "health" in goal_lower or any(word in goal_lower for word in ["medical", "disease", "hospital"]):
        base_agents.insert(0, "health")
        if "covid" in goal_lower:
            base_agents.insert(0, "covid")
    
    if "spacex" in goal_lower or "launch" in goal_lower:
        base_agents.insert(0, "spacex_next")
        base_agents.insert(1, "weather")
        base_agents.insert(2, "air_quality")
    
    # Analysis depth agents
    if any(word in goal_lower for word in ["analyze", "impact", "effect", "trend"]):
        if "fact_check" not in base_agents:
            base_agents.insert(2, "fact_check")
        base_agents.insert(3, "sentiment")
    
    # Ensure summarizer is last
    if "summarizer" in base_agents:
        base_agents.remove("summarizer")
        base_agents.append("summarizer")
    
    return base_agents

def print_execution_metrics(context):
    """Print performance metrics"""
    print_section("SYSTEM PERFORMANCE METRICS", MAGENTA)
    print(f"{BOLD}Total Processing Time:{RESET} {context.get('processing_time', 0):.2f} seconds")
    
    errors = context.get("errors", [])
    if errors:
        print(f"{BOLD}{RED}Operational Issues:{RESET} {len(errors)} errors encountered")
        for error in errors[:3]:
            print(f"  - {error}")
    else:
        print(f"{BOLD}{GREEN}Operational Status:{RESET} All agents executed successfully")
    
    # Data quality assessment
    print(f"\n{BOLD}Data Quality Assessment:{RESET}")
    if "summary" in context:
        word_count = len(context["summary"].split())
        quality = "Comprehensive" if word_count > 200 else "Detailed" if word_count > 100 else "Basic"
        print(f"  • Analysis Depth: {quality} ({word_count} words)")
    else:
        print(f"  • Analysis Depth: {RED}Insufficient{RESET}")
    
    entities = len(context.get("entities", []))
    print(f"  • Entity Coverage: {entities} key entities analyzed")
    
    coverage_score = min(100, entities * 15 + (40 if "summary" in context else 0))
    print(f"  • Comprehensive Coverage Index: {coverage_score}/100")
    print()

if __name__ == "__main__":
    print(f"{BOLD}{BLUE}{' ADVANCED RESEARCH PLATFORM ':^80}{RESET}")
    print(f"{BOLD}{'Intelligent Analysis System v3.0':^80}{RESET}\n")
    print(f"{YELLOW}Example research queries:{RESET}")
    print(wrap_text("- Comprehensive analysis of Tesla's financial performance, market sentiment, and recent news impact on stock valuation", 2))
    print(wrap_text("- In-depth assessment of climate conditions in New York with air quality metrics and weather advisories", 2))
    print(wrap_text("- Research report on COVID-19 trends and healthcare system impacts in California with policy recommendations", 2))
    print()
    
    goal = input(f"{BOLD}Enter research objective:{RESET} ").strip()
    if not goal:
        print(f"{RED}Error: Research objective required{RESET}")
        sys.exit(1)
    
    start_time = time.time()
    
    # Optimize agent selection
    print_section("INITIALIZING ANALYSIS", CYAN)
    agent_chain = optimize_agent_selection(goal)
    print(f"{BOLD}Analysis Workflow:{RESET} {GREEN}{' → '.join(agent_chain)}{RESET}")
    
    # Execute analysis
    result = execute_chain(agent_chain, goal)
    result["agent_chain"] = agent_chain
    
    # Generate comprehensive report
    print_detailed_report(result, goal)
    print_execution_metrics(result)
    
    # Save report to file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reports/{goal[:20].replace(' ', '_')}_{timestamp}.txt"
    with open(filename, "w") as f:
        sys.stdout = f
        print_detailed_report(result, goal)
        print_execution_metrics(result)
        sys.stdout = sys.__stdout__
    
    print(f"{GREEN}Full report saved to {filename}{RESET}")
    print(f"{BOLD}{YELLOW}Analysis complete. Thank you for using ADK Research Platform{RESET}")