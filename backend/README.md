README - GreenScan
# 🍎 GreenScan - Fruit Health Analyzer Web App

GreenScan is a Flask-based web application designed to analyze fruit freshness from images, retrieve nutritional data, and suggest synergic fruits tailored to a user's dietary needs. It integrates AI services like Gemini for visual analysis, USDA APIs for nutrition, and DeepSeek for personalized recommendations.

---

## 📁 Project Structure

```
.
│   .env
│   all_code_snippets.txt
│   app.py
│   copy_utils.py
│   models.py
│   requirements.txt
│
├───.dist
├───instance/
│   └── app.db
├───services/
│   ├── deepseek_service.py
│   ├── gemini_service.py
│   └── usda_service.py
├───static/
│   ├── css/
│   ├── images/
│   ├── js/
│   └── uploads/
├───templates/
└───__pycache__/
```

---

## 🚀 Features

- **Image-based Fruit Analysis**: Upload or capture an image to check if the fruit is fresh or rotten.
- **Nutritional Breakdown**: Get detailed macro- and micro-nutrient values using USDA FoodData Central.
- **Synergic Recommendations**: Get suggestions for fruits to balance nutrition, based on your profile.
- **User Authentication**: Register, login, update profiles, and maintain scan history.
- **Beautiful UI**: Mobile-responsive design using HTML, CSS, and JavaScript.

---

## 🧠 Tech Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Services**:
  - **Gemini (via OpenRouter)** – for fruit condition analysis.
  - **USDA API** – for nutritional data.
  - **DeepSeek AI** – for dietary recommendations.
- **Database**: SQLite

---

## 🔐 Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <your_repo_url>
   cd <your_project_folder>
   ```

2. **Set Up Python Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the root and add:
   ```env
   SECRET_KEY=your_secret_key
   OPENROUTER_API_KEY=your_openrouter_key
   GEMINI_KEY=your_gemini_key
   USDA_KEY=your_usda_api_key
   ```

5. **Run the App**
   ```bash
   flask run
   ```

6. **Access**
   Open your browser and go to: [http://localhost:5000](http://localhost:5000)

---

## 📝 Notable Files

- `app.py`: Main Flask application with routing and logic.
- `models.py`: SQLAlchemy models for `User` and `ScanHistory`.
- `services/`: Contains all third-party integration logic.
- `templates/`: Jinja2 templates for web views.
- `static/`: CSS, JS, images, and uploaded scans.

---

## 📸 Scanning Flow

1. Upload or capture fruit image
2. Gemini analyzes freshness and type
3. USDA provides nutritional data
4. DeepSeek suggests complementary fruits
5. Results + recommendations shown and saved

---

## ✅ To Do

- [ ] Add unit & integration tests
- [ ] Improve error handling for external APIs
- [ ] Modularize Flask app using blueprints

---

## 👨‍💻 Author

Built with ❤️ by [Your Name].

---

## 📄 License

This project is licensed under the MIT License.
