# ETL Reconciliation Agent

## Overview

The ETL Reconciliation Agent automatically validates your ETL transformations by analyzing your SQL code and generating comprehensive test scenarios.

## Features

- **Automatic Discovery**: Scans your SQL files to discover tables and transformations
- **Scenario Generation**: Automatically builds validation scenarios for each table
- **Comprehensive Checks**: Validates row counts, sums, averages, min/max, distinct counts
- **Multiple Reports**: Generates JSON, Markdown, and console reports
- **CI/CD Integration**: Works with GitHub Actions for PR validation

## Quick Start

1. **Install dependencies**:
   ```bash
   cd etl-reconciliation-agent
   pip install -r requirements.txt
   pip install -e .
