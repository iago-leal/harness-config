document.addEventListener("DOMContentLoaded", function() {
  // Destacar o menu atual
  const body = document.body;
  const pageId = body.getAttribute("data-page-id") || "index";
  
  // Se o menu foi injetado pelo Publisher
  const navItems = document.querySelectorAll(".nav-item");
  navItems.forEach(item => {
    const itemId = item.getAttribute("data-page-id");
    if (itemId === pageId) {
      item.classList.add("active");
      item.setAttribute("aria-current", "page");
    } else {
      item.classList.remove("active");
    }
  });
  
  // Se por algum motivo o menu não estiver injetado e tivermos window.RV_DATA.nav
  const navMenu = document.querySelector(".nav-menu");
  if (navMenu && (navMenu.children.length === 0 || navMenu.querySelector(".placeholder-nav"))) {
    navMenu.innerHTML = ""; // Limpa placeholder
    if (window.RV_DATA && window.RV_DATA.nav) {
      window.RV_DATA.nav.forEach(page => {
        const a = document.createElement("a");
        a.className = "nav-item";
        a.href = page.href;
        // Se for uma página de feature, vamos ajustar o caminho relativo se necessário
        if (pageId.startsWith("feature") && !page.id.startsWith("feature") && page.id !== "index") {
          a.href = "../" + page.href;
        } else if (!pageId.startsWith("feature") && page.id.startsWith("feature")) {
          // do index/modulos para features/
          a.href = page.href;
        }
        a.setAttribute("data-page-id", page.id);
        
        // Ícone simplificado por ID
        let icon = "📄";
        if (page.id === "index") icon = "🚀";
        else if (page.id === "arquitetura") icon = "📐";
        else if (page.id === "modulos") icon = "🧩";
        else if (page.id === "topologia") icon = "⚙️";
        else if (page.id === "metricas") icon = "📊";
        else if (page.id === "timeline") icon = "📅";
        else if (page.id === "glossario") icon = "📖";
        else if (page.id === "deck") icon = "🎴";
        else if (page.id.startsWith("feature-")) icon = "⚡";
        
        a.textContent = icon + " " + page.label;
        if (page.id === pageId) {
          a.classList.add("active");
          a.setAttribute("aria-current", "page");
        }
        navMenu.appendChild(a);
      });
    }
  }
});
