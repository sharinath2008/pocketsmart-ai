// Where the Flask backend lives.
// - Running locally (localhost / 127.0.0.1): talks to Flask on port 5000.
// - Deployed on GitHub Pages: talks to your hosted backend.
//   >>> Replace the URL below with your real backend URL after deploying. <<<
const PRODUCTION_API_URL = "https://YOUR-BACKEND-NAME.onrender.com";

const IS_LOCAL = ["localhost", "127.0.0.1"].includes(window.location.hostname);
const API_BASE = IS_LOCAL ? "http://127.0.0.1:5000" : PRODUCTION_API_URL;
