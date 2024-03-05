# NYU DevOps Project Template

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

This is a skeleton you can use to start your projects

## Overview

This project template contains starter code for your class project. The `/service` folder contains your `models.py` file for your model and a `routes.py` file for your service. The `/tests` folder has test case starter code for testing the model and the service separately. All you need to do is add your functionality. You can use the [lab-flask-tdd](https://github.com/nyu-devops/lab-flask-tdd) for code examples to copy from.

## Dev Environment Setup

<details>
  <summary>Using Visual Studio Code</summary>
  
  ### Requirements
  1. Visual Studio Code
  2. Docker 
  3. Install the Dev Containers extension on VS Code

  ### Install instructions
1. Git clone this repo to your machine
2. Start VS Code, run the `Dev Containers: Open Folder in Container...` command from the Command Palette (`F1`)
3. Try `pytest` in the terminal to run tests make sure the environment has been installed correctly.
</details>

<details>
  <summary>Common issues</summary>

1. Database cannot connect / authentication is wrong.
   - Check that the `DATABASE_URI` being used in the repository matches up and the postgres container is running in docker. You may need to recreate the database.
2. Can't start up the dev environment on VS Code.
   - You may need to delete instances of the containers which may have conflicting names with your existing configuration. Alternatively you can also change the config file.
</details>

## App Endpoints

```text
/index              - Root URL
/payment-method    
                    - GET : List all payment methods for a user
                    - POST: Create a payment method
/payment-method/:id
                    - GET: Provide detailed information about an existing payment method
                    - PUT: Update a given payment method
                    - DELETE: Delete a payment method
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```

## License

Copyright (c) 2016, 2024 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
