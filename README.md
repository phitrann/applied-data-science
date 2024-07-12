# Applied Data Science

This project, named "Applied Data Science", is designed to showcase the integration of various data science techniques and tools to solve real-world problems. It leverages a range of technologies including natural language processing, machine learning models, and data visualization to provide insightful solutions.

## Project Structure

The project is structured as follows:

- `__init__.py`: An initialization script for Python packages.
- `cache/`: Contains cached models and data for quick access.
- `data/`: Directory for raw and processed data.
- `dependencies.py`: Script for managing project dependencies.
- `experiments/`: Contains experimental scripts and notebooks.
- `notebooks/`: Jupyter notebooks for exploratory data analysis and prototyping.
- `pyproject.toml`: Configuration file for project metadata and dependencies.
- `README.md`: This file, providing an overview of the project.
- `requirements.txt`: Lists the Python package dependencies for the project.
- `src/`: Source code for the project's main functionality.
- `tests/`: Unit and integration tests for the project.

## Installation

To set up the project environment, follow these steps:

1. Ensure you have Python 3.8 or higher installed.
2. Clone the repository to your local machine.
3. Install the dependencies by running:

```sh
pip install -r requirements.txt
```

```bash
curl -O https://raw.githubusercontent.com/kingabzpro/jobzilla_ai/main/jz_skill_patterns.jsonl
pip install -U --index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/Triton-Nightly/pypi/simple/ triton-nightly
```

## Usage
To start the application, navigate to the src/applied_data_science directory and run:

```bash
streamlit run app.py --server.fileWatcherType none
```

This will launch the Streamlit application in your default web browser, where you can interact with the provided functionalities.

## Features
- __PDF Processing:__ Upload and process PDF documents to extract and analyze content.
- __Data Visualization:__ Interactive charts and graphs to explore data insights.
- __Job Recommendation System:__ Recommends jobs based on the processed data and user inputs.

## Contributing
Contributions to the project are welcome! Please refer to the contributing guidelines for more information.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
