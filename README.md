# Multi-Agent Earnings Analysis System

## System Architecture

This project implements a multi-agent approach to analyzing company earnings reports using Model Context Protocol (MCP). The architecture consists of five specialized agents working together to provide comprehensive earnings analysis.

### Agent Overview

1. **Retrieval Agent**
   - Primary Role: Web research and document retrieval
   - MCP Servers Used: 
     - `brave`: For internet search capabilities
     - `fetch`: For retrieving web content
     - `filesystem`: For saving retrieved reports
   - Output: Earnings report saved in `/reports` directory

2. **Financial Metrics Agent**
   - Primary Role: Quantitative analysis of financial data
   - MCP Servers Used:
     - `filesystem`: For reading reports and saving analysis
   - Output: Financial metrics analysis in `/outputs/financial_metrics.md`
   - Focus: Historical trends, KPI validation, performance metrics

3. **Executive Sentiment Agent**
   - Primary Role: Analysis of management communication
   - MCP Servers Used:
     - `filesystem`: For reading reports and saving analysis
   - Output: Sentiment analysis in `/outputs/sentiment_analysis.md`
   - Focus: Tone analysis, confidence assessment, communication patterns

4. **Forecast Agent**
   - Primary Role: Forward-looking analysis
   - MCP Servers Used:
     - `filesystem`: For reading reports and saving analysis
     - `brave`: For market context and industry trends
   - Output: Forecast analysis in `/outputs/forecast_analysis.md`
   - Focus: Guidance evaluation, market context, risk assessment

5. **Summary Agent**
   - Primary Role: Synthesis and recommendation
   - MCP Servers Used:
     - `filesystem`: For reading all analyses and saving final report
   - Output: Final recommendation in `/outputs/final_recommendation.md`
   - Focus: Comprehensive insight synthesis, actionable recommendations


## Directory Structure

```
multi_agent_earnings_analysis/
├── src/
│   └── main.py
├── reports/
│   └── [earnings reports]
├── outputs/
│   ├── financial_metrics.md
│   ├── sentiment_analysis.md
│   ├── forecast_analysis.md
│   └── final_recommendation.md
└── README.md
```

## Error Handling
- Comprehensive logging for debugging
- Exception handling for server connectivity issues

## Dependencies
- MCP Framework
- Anthropic Claude (via AnthropicAugmentedLLM)
- Rich (for enhanced logging)
- AsyncIO (for asynchronous operations)

## Monitoring and Logging
- Status updates for each agent
- Error tracking and reporting

## Future Enhancements
1. Parallel processing where applicable
3. Enhanced error recovery
4. Extended market context integration
5. Historical data comparison capabilities
