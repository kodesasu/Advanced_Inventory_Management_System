Hi There,
This is my first official Repo, been coding for a while now and decided to start pushing to Github, which am extremly new at.
This will enable me to track my Progress in the cloud and get the networking that i desperately need. Am excited to Learn.

Anyhow, this is the real "Readme" if you are interested..

Advanced Inventory Management System (AIMS)
A console based Python application designed to manage product inventories using a clean layered architecture. This is part of a Learning Series Project Assignments, 
The system allows for product registration, stock tracking, inventory searching, and data analysis with built-in logging and input validation.

Features:
- Layered Architecture (DVOU): Organized into Data, Validation, Operation, and UI layers for high maintainability.

- Smart ID Generation: Automatically creates unique alphanumeric IDs based on product attributes.

- Advanced Search: Search by keywords or use "Advanced Search" to search down by Company, Category, or Sub-category.

- Data Analysis: Get summaries of stock counts, category distribution, and average stock levels.

- Validation: Prevents bad data entry (empty strings, negative numbers, duplicate names).

- Logging: Detailed activity tracking using RotatingFileHandler to monitor system operations without bloating disk space.

Technical Stack:
- Language: Python 3.x

- Storage: Used In-memory dictionary-based storage with namedtuple objects.

- Modules Used: collections (namedtuple, Counter, defaultdict), logging, os.

Installation & Usage
- Clone the repository:
git clone https://github.com/Kodesasu/Advanced_Inventory_Management_System.git

cd Advanced_Inventory_Management_System

- Run the application:
python main.py
The system automatically creates a ProductInventoryLogs.log file in the project directory to track all additions and errors.

How it Works:
- Data Layer: Manages the core data structures and "database" state.

- Validation Layer: Ensures all user inputs meet specific criteria before processing.

- Operation Layer: Handles the "business logic," such as calculating analysis and filtering search results.

- User Interface (UI) Layer: Manages the menu system and console interactions.

Sample Analysis Output:
- For example, when you select the "Display Product Analysis" option, the system provides: Total product count by category.

i would Love your advise and critique, any feedback is good

Average stock levels per category.

Low-stock alerts (items with less than 10 units).
