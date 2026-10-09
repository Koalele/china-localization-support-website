(function () {
  const config = window.SITE_CONFIG || {};
  const year = document.querySelector("[data-year]");
  if (year) year.textContent = new Date().getFullYear();

  const params = new URLSearchParams(window.location.search);
  const serviceField = document.querySelector('[name="service"]');
  if (serviceField && params.has("service")) {
    const value = params.get("service");
    if ([...serviceField.options].some((option) => option.value === value)) serviceField.value = value;
  }

  const toggle = document.querySelector("[data-menu-toggle]");
  const nav = document.querySelector("[data-site-nav]");
  if (toggle && nav) toggle.addEventListener("click", () => {
    const open = toggle.getAttribute("aria-expanded") !== "true";
    toggle.setAttribute("aria-expanded", String(open));
    nav.classList.toggle("is-open", open);
  });
  if (toggle && nav) nav.addEventListener("click", (event) => {
    if (event.target.closest("a")) {
      toggle.setAttribute("aria-expanded", "false");
      nav.classList.remove("is-open");
    }
  });
  if (toggle && nav) document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && nav.classList.contains("is-open")) {
      toggle.setAttribute("aria-expanded", "false");
      nav.classList.remove("is-open");
      toggle.focus();
    }
  });

  function showStatus(status, message) {
    if (!status) return;
    status.replaceChildren();
    status.dataset.state = "error";
    status.append(document.createTextNode(message + " "));
    const link = document.createElement("a");
    link.href = "mailto:hello@transwindcn.com";
    link.textContent = "Email hello@transwindcn.com";
    status.append(link);
  }

  document.querySelectorAll("[data-contact-form], [data-early-access-form]").forEach((form) => {
    const status = form.querySelector("[data-form-status]");
    const note = form.querySelector("[data-form-note]");
    const connectionNote = form.closest(".form-shell")?.querySelector("[data-form-connection-note]") || note;
    const configured = Boolean(config.formEndpoint && config.web3FormsAccessKey);
    if (connectionNote) {
      connectionNote.replaceChildren();
      if (configured) {
        connectionNote.classList.remove("notice");
        connectionNote.append(document.createTextNode("Form submissions are processed by Web3Forms and forwarded to TransWind so we can respond. See our "));
        const privacyLink = document.createElement("a");
        privacyLink.href = "/privacy.html";
        privacyLink.textContent = "Privacy Policy";
        connectionNote.append(privacyLink);
        connectionNote.append(document.createTextNode("."));
      } else {
        connectionNote.classList.add("notice");
        connectionNote.append(document.createTextNode("This form is not connected yet. Submitting will not send your details. Please email "));
        const emailLink = document.createElement("a");
        emailLink.href = "mailto:hello@transwindcn.com";
        emailLink.textContent = "hello@transwindcn.com";
        connectionNote.append(emailLink);
        connectionNote.append(document.createTextNode("."));
      }
    }
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const data = new FormData(form);
      if (data.get("website")) {
        form.reset();
        return;
      }
      if (!configured) {
        showStatus(status, "This form is not connected yet. Your request has not been sent.");
        return;
      }
      data.delete("website");
      data.set("access_key", config.web3FormsAccessKey);
      data.set("subject", form.matches("[data-early-access-form]") ? "TransWind Education Program Interest" : "TransWind Website Enquiry");
      data.set("from_name", "TransWind Website");
      if (data.get("email")) data.set("replyto", data.get("email"));
      const submit = form.querySelector('[type="submit"]');
      if (submit) submit.disabled = true;
      if (status) { status.dataset.state = ""; status.textContent = "Sending…"; }
      try {
        const response = await fetch(config.formEndpoint, {
          method: "POST",
          body: JSON.stringify(Object.fromEntries(data.entries())),
          headers: { "Content-Type": "application/json", Accept: "application/json" }
        });
        const result = await response.json();
        if (!response.ok || result.success === false) throw new Error(result.message || "Submission failed");
        form.reset();
        if (status) {
          status.dataset.state = "success";
          status.textContent = "Thank you. Your request has been sent.";
        }
        document.dispatchEvent(new CustomEvent("site:form-submit"));
      } catch (_) {
        showStatus(status, "We could not send your request.");
      } finally {
        if (submit) submit.disabled = false;
      }
    });
  });

  if (config.analyticsProvider && config.analyticsId) {
    document.dispatchEvent(new CustomEvent("site:analytics-ready", {
      detail: { provider: config.analyticsProvider, id: config.analyticsId }
    }));
  }
  if (config.spamProtection && config.spamProtection.provider) {
    document.dispatchEvent(new CustomEvent("site:spam-protection-configured", {
      detail: config.spamProtection
    }));
  }
})();
