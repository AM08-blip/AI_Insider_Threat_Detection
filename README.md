# AI-Based Insider Threat Detection System

## 📌 Project Overview

The **AI-Based Insider Threat Detection System** is a web-based security application designed to identify potentially suspicious user behavior by analyzing user activity patterns. The system uses Machine Learning to classify activity as normal or suspicious and provides an interface for reviewing activity records and threat assessment results.

The project aims to demonstrate how Artificial Intelligence and Machine Learning can support insider threat monitoring by helping administrators identify unusual activities and investigate potential security risks.

## 🎯 Objectives

- Monitor and record relevant user activities.
- Analyze behavioral features to identify potentially suspicious patterns.
- Use a trained Machine Learning model to classify user activity.
- Provide separate administrator and employee interfaces.
- Manage document-related operations according to user permissions.
- Display threat prediction results and relevant explanations.
- Generate PDF reports for reviewing available system information.

## ✨ Key Features

- **User Authentication:** Login functionality for authorized users.
- **Role-Based Interfaces:** Separate administrator and employee dashboards.
- **Activity Monitoring:** Records relevant user activities for security review.
- **Document Management:** Supports the document operations implemented in the application.
- **AI-Based Threat Detection:** Uses a trained Machine Learning model to classify activity as normal or suspicious.
- **Risk Assessment:** Displays prediction details and risk-related information supported by the application.
- **Activity Logs:** Allows authorized users to review recorded activities.
- **PDF Report Generation:** Generates reports containing available application information.
- **Web-Based Interface:** Provides a user-friendly interface built with HTML and CSS.

## 🛠️ Technologies Used

- **Programming Language:** Python
- **Web Framework:** Flask
- **Machine Learning:** scikit-learn
- **Data Processing:** pandas and NumPy
- **Database:** SQLite
- **Model Persistence:** Joblib
- **Frontend:** HTML, CSS, JavaScript
- **PDF Reports:** ReportLab

## ⚙️ How It Works

1. An authorized user logs in to the web application.
2. The application records relevant user activity.
3. Activity data is processed into behavioral features.
4. The trained Machine Learning model analyzes the available features.
5. The system produces a normal or suspicious activity prediction.
6. Authorized users can review activity records and threat assessment results.
7. Available information can be exported through the PDF reporting feature.

## 🧠 Machine Learning

The project uses a trained **Random Forest classifier** to analyze behavioral features such as:

- Failed login attempts
- Document views
- Document downloads
- Document uploads
- Total recorded actions
- Average login hour

The model uses these features to classify activity based on patterns learned during training.

## 🖥️ Application Architecture

The application consists of the following main components:

- **Frontend:** Provides login pages, dashboards, and application interfaces.
- **Backend:** Uses Flask to handle application requests and business logic.
- **Database:** Uses SQLite to store application data.
- **Machine Learning Module:** Processes behavioral features and generates predictions.
- **Reporting Module:** Generates PDF reports from supported application data.

## 🚀 Running the Project Locally

### Prerequisites

- Python installed on your system
- Project source code
- Required Python packages
- Database and trained model files, where required

### Installation

1. Clone the repository:

   ```bash
   git clone <your-repository-url>
   ```

2. Navigate to the project directory:

   ```bash
   cd AI_Insider_Threat_Detection
   ```

3. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment on Windows:

   ```bash
   venv\Scripts\activate
   ```

5. Install the project dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Start the application:

   ```bash
   python app.py
   ```

7. Open the local address displayed in the terminal in your web browser.

**Note:** These instructions assume that `requirements.txt` and the necessary database and model files are included in the repository. Adjust the setup steps to match the actual files in your project.

## 🔒 Security and Responsible Use

This project is intended for educational purposes and security monitoring demonstrations. A suspicious prediction is an indication for further investigation, not proof of malicious intent. Real-world deployment requires appropriate access controls, secure configuration, privacy safeguards, and evaluation using representative data.

## ⚠️ Limitations

- Model performance depends on the quality and representativeness of the training data.
- Synthetic test data may not represent all real-world employee behavior.
- Predictions may include false positives and false negatives.
- Production deployment requires additional security and performance testing.

## 🔮 Future Enhancements

- Real-time activity monitoring
- Improved detection using real-world, appropriately authorized datasets
- Automated security alerts
- Enhanced threat visualization and analytics
- Multi-factor authentication
- Cloud deployment
- Integration with external security monitoring systems

## 👨‍💻 Project Purpose

This project was developed as an academic Mini Project to explore the practical application of Artificial Intelligence, Machine Learning, web development, database management, and cybersecurity.

---

**Technologies:** Python · Flask · SQLite · scikit-learn · pandas · NumPy · HTML · CSS · JavaScript