## Setting up for local development
1. Ensure you have the following installed:
    * Python: `3.10` or above
2. Installing dependencies:
    1. Install poetry on your machine: https://python-poetry.org/
    2. Run `poetry install` to install the required dependencies.
3. Set and export the required environment variables:
    ```bash
    export POSTGRES_HOST="127.0.0.1" \
        POSTGRES_PORT="5432" \
        POSTGRES_DB="test1" \
        POSTGRES_RESEARCH_DB="test2" \
        POSTGRES_USER="test" \
        POSTGRES_RESEARCH_USER="test2" \
        POSTGRES_PASSWORD="test" \
        POSTGRES_RESEARCH_PASSWORD="test2"
    ```

# Anonymization
1. Run `poetry run python generate_anon_data.py --k <value>` to start anonymizing process with `value` anonymity.
Eg: `poetry run python generate_anon_data.py --k 3`
## Testing
1. Run `poetry run python test.py <k anonymity value> <l diversity value>` to test. 
Eg: `poetry run python test.py 2 2`