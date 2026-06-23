# 🛒 Cart System (React + TypeScript)

### 🔗 Live Demo: [👉 View Project on Netlify](https://cart-system-typescript-c9a973.netlify.app/)

A fully functional and responsive shopping cart system built with React, TypeScript, and Bootstrap. This project demonstrates clean UI design, state management using the Context API, and local storage persistence. It allows users to browse a product list, add or remove items from their cart, and view real-time cart totals based on quantity and pricing.

---

## 📌 Features:

* ✅ Add and remove items from cart.
* 📦 Auto-saves cart using localStorage.
* 🔢 Calculates price based on item quantity.
* 💰 Displays total price and total items in cart.
* 📱 Fully responsive layout (Bootstrap 5).
* 💡 Built with strongly typed TypeScript.

---

## 🧰 Tech Stack:
The following tech stack is used in this project:

* **React 19** : JavaScript library for building user interfaces with component-based architecture.
* **TypeScript** : A strongly typed superset of JavaScript that helps catch errors early and improves code quality.
* **React Bootstrap** : Bootstrap components rewritten as React components for easy integration with React apps.
* **Bootstrap 5** : A responsive CSS framework that provides pre-built UI styles and layout utilities.
* **React Router v7** : Handles client-side routing, allowing seamless navigation between pages without full reloads.
* **React Icons** : A popular icon library offering access to hundreds of SVG icons from various icon sets.

---

## 📦 Dependencies:
The following dependencies are used in this project:

```json
"dependencies": {
  "bootstrap": "^5.3.7",
  "react": "^19.1.0",
  "react-bootstrap": "^2.10.10",
  "react-dom": "^19.1.0",
  "react-icons": "^5.5.0",
  "react-router-dom": "^7.6.3"
}
```

## 📁 Project Structure:

The following structure is used in this project to maintain a clean and modular codebase:

```bash
cart-system-typescript/
├── node_modules/
├── public/
├── src/                         
│   ├── assets/                  # Images, icons, and other static assets
│   ├── components/              # Reusable UI components (Navbar, Footer, CartItem, etc.)
│   ├── context/                 # React Context logic (e.g., ShoppingCartContext)
│   ├── data/                    # Static item data (items.json)
│   ├── hooks/                   # Custom React hooks (e.g., useLocalStorage)
│   ├── pages/                   # Route components like Home and About
│   ├── utilities/               # Utility functions (e.g., formatCurrency)
│   ├── App.tsx                  # Main app component
│   └── main.tsx                 # Application entry point
├── .gitignore                   # Git ignored files
├── eslint.config.js
├── index.html                   # Main HTML template
├── LICENSE
├── package-lock.json
├── package.json                 # Project metadata and dependencies
├── README.md
├── tsconfig.app.json
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
```

---

## 🚀 Installation & Setup:
Follow these steps to successfully run the project:

#### 1. Clone the repository:

```bash
git clone https://github.com/PAIshanMadusha/cart-system-typescript.git
```
##### And, navigate to the project directory:

```bash
cd cart-system-typescript
```

#### 2. Install dependencies:

```bash
npm install
```

#### 3. Run the app locally:

```bash
npm run dev
```

## 📸 System Screenshots:
These screenshots illustrate how the system appears on desktop and mobile devices:

---
<p align="center">
  <img src="https://github.com/user-attachments/assets/d253c866-00f9-4c37-9a40-7ab92d7eec68" alt="Screenshot 1" width="700">
  <br><br>
  <img src="https://github.com/user-attachments/assets/20f6d1fe-d8a1-44ea-9c6d-c297402c3d86" alt="Screenshot 3" width="700">
  <br><br>
  <img src="https://github.com/user-attachments/assets/f1faa7fc-bda6-44fc-8812-5e75ea258d39" alt="Screenshot 4" width="700">
  <br><br>
  <img src="https://github.com/user-attachments/assets/aa7339eb-caad-43d3-9e0e-2fd7626d184b" alt="Screenshot 4" width="700">
  <br><br>
  <img src="https://github.com/user-attachments/assets/11068ade-e56d-4e7a-8886-6796c05c71aa" alt="Screenshot 4" width="340">&nbsp;&nbsp;&nbsp;
  <img src="https://github.com/user-attachments/assets/4da4faf2-b333-4af6-b6e0-1b4d526a4142" alt="Screenshot 4" width="340">
</p>

---

### 👨‍💻 Created by: 
**Ishan Madhusha**  
GitHub: [PAIshanMadusha](https://github.com/PAIshanMadusha)

Feel free to explore my work and get in touch if you'd like to collaborate! 🚀

---

## 📝 License:  
This project is licensed under the MIT License : See the [LICENSE](LICENSE) file for details.
