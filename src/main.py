import asyncio
import time
import os

from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.mcp.mcp_connection_manager import MCPConnectionManager
from mcp_agent.workflows.llm.augmented_llm_anthropic import AnthropicAugmentedLLM  
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from mcp_agent.logging.logger import LoggingConfig
from rich import print

app = MCPApp(name="earnings_analyzer")


async def get_earnings_report():
    async with app.run() as agent_app:
        logger = agent_app.logger
        context = agent_app.context
        logger.info("Current config:", data=context.config.model_dump())
        try:
            context.config.mcp.servers["filesystem"].args.extend([os.getcwd()])
            logger.info("Added current directory to filesystem server args")
        except KeyError:
            logger.info("Warning: 'filesystem' key not found in context.config.mcp.servers")

        async with MCPConnectionManager(context.server_registry):
            current_date = time.strftime("%Y-%m-%d")
            
            # Initialize all agents
            retrieval_agent = Agent(
                name="retrieval",
                instruction="""You are an expert web researcher, with access to internet search (via Brave), the ability to fetch website data (via Fetch) and the ability to save and read files to the filesystem (via Filesystem).
                Given a company name, you will search the internet for the latest earnings report for that company.
                You must find the earnings report only from the company's official website, not any other sources. It is usually under "Investor Relations" or "Quarterly Results" sections.
                You will be looking for the most recent quarterly earnings report. Since today is {current_date}, the earning report's release date should be the one closest to today's date.  
                Save the earnings report you find to the filesystem in the /reports folder.
                """.format(current_date=current_date),
                server_names=["brave", "fetch", "filesystem"],
            )

            financial_metrics_agent = Agent(
                name="financial_metrics",
                instruction="""You are a financial metrics expert specializing in analyzing company performance data.
                Your role is to:
                1. Read the earnings report from the filesystem
                2. Extract and validate key financial metrics against historical data
                3. Analyze trends in revenue, margins, EPS, and other key performance indicators
                4. Identify any significant deviations from historical patterns
                5. Save your analysis to the filesystem in the /outputs/financial_metrics.md file
                
                Focus on quantitative analysis and statistical validation of the numbers presented in the report.
                """,
                server_names=["filesystem"],
            )

            sentiment_agent = Agent(
                name="executive_sentiment",
                instruction="""You are an expert in analyzing executive communication and corporate sentiment.
                Your tasks include:
                1. Read the earnings report from the filesystem
                2. Analyze the tone and confidence levels in executive statements
                3. Evaluate the language used in forward-looking statements
                4. Assess management's confidence in their strategy and execution
                5. Save your analysis to the filesystem in the /outputs/sentiment_analysis.md file
                
                Pay special attention to changes in tone compared to previous statements and any notable shifts in confidence levels.
                """,
                server_names=["filesystem"],
            )

            forecast_agent = Agent(
                name="forecast",
                instruction="""You are a forecasting specialist focused on future business performance.
                Your responsibilities include:
                1. Read the earnings report from the filesystem
                2. Analyze all forward-looking statements and guidance
                3. Evaluate the feasibility of projected metrics
                4. Compare guidance against industry trends and market conditions
                5. Save your analysis to the filesystem in the /outputs/forecast_analysis.md file
                
                Focus on the reliability of projections and identify potential risks or opportunities in the forecast.
                """,
                server_names=["filesystem", "brave"],
            )

            summary_agent = Agent(
                name="summary",
                instruction="""You are a senior investment analyst responsible for synthesizing multiple analyses into actionable insights.
                Your tasks include:
                1. Read all analysis files from the /outputs directory
                2. Synthesize insights from financial metrics, sentiment, and forecast analyses
                3. Generate comprehensive investment recommendations
                4. Provide clear rationale for the recommendations
                5. Save your final report to the filesystem in the /outputs/final_recommendation.md file
                
                Your output should be concise yet comprehensive, suitable for investment decision-making.
                """,
                server_names=["filesystem"],
            )

            research_prompt = """Produce an earnings analysis for the company Micron. The final analysis should be saved in the filesystem in markdown format, and
                contain the following: 
                1 - Revenue and earnings per share for the latest quarter
                2 - Statistics on the company's outlook and guidance for the next quarter
                3 - Any insights from Management's comments on this quarter and the future outlook
                4 - Analyze the trend of the company's fundamentals, and consider the future outlook to generate a recommendation to buy, sell, or hold based on this earnings report.
                """

            try:
                # Initialize LLM for all agents
                llm_anthr = await retrieval_agent.attach_llm(AnthropicAugmentedLLM)
                
                # Step 1: Retrieve earnings report
                logger.info("Starting earnings report retrieval...")
                retrieval_result = await llm_anthr.generate_str(research_prompt)
                logger.info("Retrieval task completed")

                # Step 2: Analyze financial metrics
                logger.info("Starting financial metrics analysis...")
                await financial_metrics_agent.attach_llm(AnthropicAugmentedLLM)
                metrics_result = await financial_metrics_agent.llm.generate_str(
                    "Analyze the financial metrics from the retrieved earnings report in /reports folder."
                )
                logger.info("Financial metrics analysis completed")

                # Step 3: Analyze executive sentiment
                logger.info("Starting sentiment analysis...")
                await sentiment_agent.attach_llm(AnthropicAugmentedLLM)
                sentiment_result = await sentiment_agent.llm.generate_str(
                    "Analyze the executive sentiment from the retrieved earnings report in /reports folder."
                )
                logger.info("Sentiment analysis completed")

                # Step 4: Analyze forecasts
                logger.info("Starting forecast analysis...")
                await forecast_agent.attach_llm(AnthropicAugmentedLLM)
                forecast_result = await forecast_agent.llm.generate_str(
                    "Analyze the forecasts and guidance from the retrieved earnings report in /reports folder."
                )
                logger.info("Forecast analysis completed")

                # Step 5: Generate final summary
                logger.info("Generating final summary...")
                await summary_agent.attach_llm(AnthropicAugmentedLLM)
                summary_result = await summary_agent.llm.generate_str(
                    "Synthesize all analyses from the /outputs directory into a final recommendation."
                )
                logger.info("Final summary completed")

                logger.info("All analyses completed successfully")
                
            finally:
                # Clean up all agents
                for agent in [retrieval_agent, financial_metrics_agent, sentiment_agent, 
                            forecast_agent, summary_agent]:
                    await agent.close()

    # Ensure logging is properly shutdown
    await LoggingConfig.shutdown()


if __name__ == "__main__":
    start = time.time()
    try:
        asyncio.run(get_earnings_report())
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt, shutting down gracefully...")
    except Exception as e:
        print(f"Error during execution: {e}")
        raise
    finally:
        end = time.time()
        t = end - start
        print(f"Total run time: {t:.2f}s")
