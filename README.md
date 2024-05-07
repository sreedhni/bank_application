Banking Application using Django REST Framework

Overview
This banking application, developed using Django REST Framework, provides a robust platform for managing accounts, loans, and financial planning. With a focus on security and user-friendliness, the application offers a comprehensive suite of features for staff, customers, and administrators.

User Authentication and Security
User authentication is a top priority in the application:

Authentication: Users log in using their email and password, with JWT (JSON Web Token) authentication ensuring secure access to the platform.
Account Locking: After 5 unsuccessful login attempts, the user's account is locked for 1 hour, enhancing security measures.
Customer Account Management
Customers can perform various account-related activities:

Account Opening: Customers submit details for account opening. Only after meeting predefined requirements set by administrators can customers apply for an account.
Account Activation: Once staff members verify the submitted details and ensure they meet requirements, the account is activated, and a unique account number is assigned.
Transactions: Customers can deposit and withdraw funds securely. Transactions require UPI PIN verification to ensure authorized access.
Loan Repayment: Customers can repay loans, ensuring timely settlement of outstanding amounts.
Loan Management
The application offers efficient loan management services:

Loan Applications: Customers can apply for different types of loans, such as personal loans, home loans, and car loans, with online application forms and instant approval processes.
Loan Verification: Staff members review loan applications and ensure that customers meet predefined requirements before approving loans.
Loan Repayment: Customers can repay existing loans. No two loans can be active simultaneously, preventing multiple loan burdens on customers.
Financial Planning Tools
Comprehensive financial planning tools aid users in managing their finances effectively:

Budgeting and Expense Tracking: Users can set budgets, categorize expenses, and track spending patterns using integrated tools.
Savings Goals: Users can establish savings goals, monitor progress, and receive notifications upon reaching milestones, fostering effective financial planning.
Unique Identifiers and Security Measures
Unique Identifiers: Unique identifiers such as Aadhar number, PAN card number, and mobile number are utilized during account opening to ensure accurate customer identification.
Security Measures: JWT authentication is employed for secure user authentication and session management, ensuring data integrity and confidentiality.
Documentation and Contribution
Documentation: Comprehensive API documentation is provided using Swagger, facilitating easy reference to endpoints and functionalities. Detailed docstrings in the codebase offer insights into each function and method.
Contribution: Contributors are encouraged to follow guidelines outlined in the CONTRIBUTING.md file to maintain code quality and consistency.
Technologies Used
Django REST Framework: The primary framework for developing RESTful APIs.
JWT Authentication: Ensures secure user authentication and session management.
