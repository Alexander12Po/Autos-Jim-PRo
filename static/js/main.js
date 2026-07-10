// =========================================================
// AutoMarket Premium - JavaScript principal
// =========================================================

// --- Loader ---
window.addEventListener("load", () => {
  const loader = document.getElementById("loader");
  setTimeout(() => loader.classList.add("hidden"), 400);
});

// --- Menu movil ---
const navToggle = document.getElementById("navToggle");
const navLinks = document.getElementById("navLinks");
if (navToggle) {
  navToggle.addEventListener("click", () => {
    navLinks.classList.toggle("open");
  });
}

// --- Modo oscuro ---
const darkModeToggle = document.getElementById("darkModeToggle");
const savedTheme = localStorageSafeGet("theme") || "light";
applyTheme(savedTheme);

if (darkModeToggle) {
  darkModeToggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme") || "light";
    const next = current === "dark" ? "light" : "dark";
    applyTheme(next);
    localStorageSafeSet("theme", next);
  });
}

function applyTheme(theme) {
  if (theme === "dark") {
    document.documentElement.setAttribute("data-theme", "dark");
    if (darkModeToggle) darkModeToggle.innerHTML = '<i class="fa-solid fa-sun"></i>';
  } else {
    document.documentElement.removeAttribute("data-theme");
    if (darkModeToggle) darkModeToggle.innerHTML = '<i class="fa-solid fa-moon"></i>';
  }
}

// Uso seguro de localStorage (disponible en navegador normal, no en artifacts)
function localStorageSafeGet(key) {
  try { return window.localStorage.getItem(key); } catch (e) { return null; }
}
function localStorageSafeSet(key, value) {
  try { window.localStorage.setItem(key, value); } catch (e) { /* ignore */ }
}

// --- Toasts: cerrar manualmente ---
document.querySelectorAll(".toast-close").forEach((btn) => {
  btn.addEventListener("click", () => {
    btn.closest(".toast").remove();
  });
});

// Auto-remover toasts despues de la animacion
setTimeout(() => {
  document.querySelectorAll(".toast").forEach((t) => t.remove());
}, 5200);

// --- Boton volver arriba ---
const backToTop = document.getElementById("backToTop");
if (backToTop) {
  window.addEventListener("scroll", () => {
    if (window.scrollY > 400) {
      backToTop.classList.add("show");
    } else {
      backToTop.classList.remove("show");
    }
  });
  backToTop.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}

// --- Navbar con sombra al hacer scroll ---
const navbar = document.getElementById("navbar");
if (navbar) {
  window.addEventListener("scroll", () => {
    if (window.scrollY > 20) {
      navbar.style.boxShadow = "0 2px 25px rgba(0,0,0,0.35)";
    } else {
      navbar.style.boxShadow = "0 2px 20px rgba(0,0,0,0.15)";
    }
  });
}

// --- Animacion de aparicion al hacer scroll (Intersection Observer) ---
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.style.animationPlayState = "running";
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll(".fade-in").forEach((el) => observer.observe(el));
