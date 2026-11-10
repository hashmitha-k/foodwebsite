// ============================================================
//  HOW TO CONNECT YOUR HTML FILES TO THE BACKEND
//  Copy-paste these functions into your HTML <script> tags
// ============================================================

const API = "http://127.0.0.1:8000";  // Change to your server URL when deployed

// Helper: read the saved token
function getToken() {
  return localStorage.getItem("token");
}

// Helper: headers with auth
function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${getToken()}`
  };
}


// ─── REGISTER ────────────────────────────────────────────────

async function register(username, email, password) {
  const res = await fetch(`${API}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password })
  });
  const data = await res.json();
  if (!res.ok) { alert(data.detail); return; }
  alert(data.message);
}


// ─── LOGIN ───────────────────────────────────────────────────

async function login(emailOrUsername, password) {
  const form = new URLSearchParams();
  form.append("username", emailOrUsername);  // FastAPI login uses 'username' field
  form.append("password", password);

  const res = await fetch(`${API}/auth/login`, {
    method: "POST",
    body: form
  });
  const data = await res.json();
  if (!res.ok) { alert(data.detail); return; }

  localStorage.setItem("token", data.access_token);  // Save token
  alert("Logged in!");
}


// ─── GET MY PROFILE ──────────────────────────────────────────

async function getMyProfile() {
  const res = await fetch(`${API}/users/me`, { headers: authHeaders() });
  const data = await res.json();
  console.log("My profile:", data);
  return data;
}


// ─── GET ALL RECIPES ─────────────────────────────────────────

async function getAllRecipes() {
  const res = await fetch(`${API}/recipes/`);
  const data = await res.json();
  return data;  // array of recipes
}


// ─── ADD A RECIPE ────────────────────────────────────────────

async function addRecipe(title, description, ingredients, steps, image_url) {
  const res = await fetch(`${API}/recipes/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ title, description, ingredients, steps, image_url })
  });
  const data = await res.json();
  if (!res.ok) { alert(data.detail); return; }
  return data;
}


// ─── FAVORITE A RECIPE ───────────────────────────────────────

async function favoriteRecipe(recipeId) {
  const res = await fetch(`${API}/favorites/${recipeId}`, {
    method: "POST",
    headers: authHeaders()
  });
  const data = await res.json();
  alert(data.message || data.detail);
}


// ─── GET MY FAVORITES ────────────────────────────────────────

async function getMyFavorites() {
  const res = await fetch(`${API}/favorites/`, { headers: authHeaders() });
  return await res.json();  // array of recipes
}


// ─── LOGOUT ──────────────────────────────────────────────────

function logout() {
  localStorage.removeItem("token");
  alert("Logged out!");
}
