(function () {
  const config = window.SITE_CONFIG || {};
  const STR = {
    en: { connectedEnd: ".", notConnectedEnd: ".", emailLink: "Email hello@transwindcn.com", connected: "Form submissions are processed by Web3Forms and forwarded to TransWind so we can respond. See our ", privacy: "Privacy Policy", notConnectedNote: "This form is not connected yet. Submitting will not send your details. Please email ", notConnectedStatus: "This form is not connected yet. Your request has not been sent.", sending: "Sending\u2026", success: "Thank you. Your request has been sent.", error: "We could not send your request.", failed: "Submission failed" },
    zh: { connectedEnd: "。", notConnectedEnd: "。", emailLink: "发送邮件至 hello@transwindcn.com", connected: "表单提交内容由 Web3Forms 处理并转发给 TransWind，以便我们回复您。详见我们的", privacy: "隐私政策", notConnectedNote: "此表单尚未连接，提交不会发送您的信息。请发送邮件至 ", notConnectedStatus: "此表单尚未连接，您的需求尚未发送。", sending: "发送中\u2026", success: "谢谢，您的需求已发送。", error: "我们未能发送您的需求。", failed: "提交失败" },
    ja: { connectedEnd: "をご覧ください。", notConnectedEnd: "", emailLink: "hello@transwindcn.com にメールする", connected: "フォームの送信内容は Web3Forms で処理され、ご返信のために TransWind に転送されます。詳しくは", privacy: "プライバシーポリシー", notConnectedNote: "このフォームはまだ接続されていません。送信しても情報は届きません。次のアドレスにメールをお送りください：", notConnectedStatus: "このフォームはまだ接続されていません。ご相談内容は送信されていません。", sending: "送信中\u2026", success: "ありがとうございます。送信が完了しました。", error: "送信できませんでした。", failed: "送信に失敗しました" },
    fr: { connectedEnd: ".", notConnectedEnd: ".", emailLink: "Écrire à hello@transwindcn.com", connected: "Les envois de formulaires sont traités par Web3Forms puis transmis à TransWind afin que nous puissions vous répondre. Voir notre ", privacy: "politique de confidentialité", notConnectedNote: "Ce formulaire n\u2019est pas encore connecté. Son envoi ne transmettra pas vos informations. Merci d\u2019écrire à ", notConnectedStatus: "Ce formulaire n\u2019est pas encore connecté. Votre demande n\u2019a pas été envoyée.", sending: "Envoi en cours\u2026", success: "Merci. Votre demande a bien été envoyée.", error: "Nous n\u2019avons pas pu envoyer votre demande.", failed: "L\u2019envoi a échoué" }
  };
  const pageLang = (document.documentElement.lang || "en").slice(0, 2);
  const t = STR[pageLang] || STR.en;
  const langPrefix = pageLang === "en" || !STR[pageLang] ? "" : "/" + pageLang;
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
    link.textContent = t.emailLink;
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
        connectionNote.append(document.createTextNode(t.connected));
        const privacyLink = document.createElement("a");
        privacyLink.href = langPrefix + "/privacy.html";
        privacyLink.textContent = t.privacy;
        connectionNote.append(privacyLink);
        connectionNote.append(document.createTextNode(t.connectedEnd));
      } else {
        connectionNote.classList.add("notice");
        connectionNote.append(document.createTextNode(t.notConnectedNote));
        const emailLink = document.createElement("a");
        emailLink.href = "mailto:hello@transwindcn.com";
        emailLink.textContent = "hello@transwindcn.com";
        connectionNote.append(emailLink);
        connectionNote.append(document.createTextNode(t.notConnectedEnd));
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
        showStatus(status, t.notConnectedStatus);
        return;
      }
      data.delete("website");
      data.set("access_key", config.web3FormsAccessKey);
      data.set("subject", form.matches("[data-early-access-form]") ? "TransWind Education Program Interest" : "TransWind Website Enquiry");
      data.set("from_name", "TransWind Website");
      if (data.get("email")) data.set("replyto", data.get("email"));
      const submit = form.querySelector('[type="submit"]');
      if (submit) submit.disabled = true;
      if (status) { status.dataset.state = ""; status.textContent = t.sending; }
      try {
        const response = await fetch(config.formEndpoint, {
          method: "POST",
          body: JSON.stringify(Object.fromEntries(data.entries())),
          headers: { "Content-Type": "application/json", Accept: "application/json" }
        });
        const result = await response.json();
        if (!response.ok || result.success === false) throw new Error(result.message || t.failed);
        form.reset();
        if (status) {
          status.dataset.state = "success";
          status.textContent = t.success;
        }
        document.dispatchEvent(new CustomEvent("site:form-submit"));
      } catch (_) {
        showStatus(status, t.error);
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
