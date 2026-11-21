/* ============================================================
   Jay's Studio: shared content for BOTH versions.
   The 3D studio and the 2D site load this same file, so edit
   links and copy here once and republish both pages.
   An empty url ("") shows as "coming soon" instead of a link.
   ============================================================ */
window.SITE = {
  name: "Jay's Studio",
  tagline: "Everything I make, in one place.",

  versions: {
    studio: "/studio/",   // 3D walkable studio
    flat: "/"            // 2D site (home page)
  },

  /* Free ebook signup. Emails go straight into Jay's Kit form
     ("Newsletter site") through kitFormAction. To use a different Kit form,
     swap the number in the address. signupUrl, if set, replaces the form
     with a button to that page instead. */
  ebook: {
    title: "10 Things You Can Do With AI",
    kicker: "Free ebook",
    pitch: "Ten practical things you can do with AI this week, each one written so you can try it in an evening. Join the list and it's yours free.",
    cta: "Send me the ebook",
    kitFormAction: "https://app.convertkit.com/forms/10224334/subscriptions",
    done: "You're on the list. Check your inbox to confirm your email, and the ebook comes to you as soon as it's out.",
    signupUrl: ""
  },

  /* What the TV shows. The remote on the coffee table steps through these. */
  channels: [
    { screen: "youtube", name: "Slopking", title: "Slopking on YouTube", cta: "Open YouTube", url: "https://www.youtube.com/@Slopking203", blurb: "New uploads land here first." },
    { screen: "youtube", name: "Jay vs America", title: "Jay vs America on YouTube", cta: "Open YouTube", url: "https://www.youtube.com/@jayvsamerica", blurb: "My travel channel." }
  ],

  /* One entry per clickable object in the 3D room (and a section in the 2D site). */
  links: {
    tv:     { where: "The TV", title: "Slopking on YouTube", cta: "Open YouTube", url: "https://www.youtube.com/@Slopking203", blurb: "My video channels. New uploads land here first." },
    phone:  { where: "The phone tripod", title: "TikTok", cta: "Open TikTok", url: "https://www.tiktok.com/@slopking203", blurb: "Short cuts, behind-the-build clips and whatever I filmed this week." },
    arcade: { where: "The arcade cabinet", title: "Retro hybrid games", cta: "Play the games", url: "", blurb: "Classic games smashed together and playable in your browser. A new mashup every month.",
              items: ["Snake x Pac-Man", "Starflap", "Viral Stack", "Paddle Fighter", "Brick Tilt"] },
    laptop: { where: "The desk", title: "Apps and projects", cta: "See the projects", url: "", blurb: "Web apps and tools I build on my own time, including Scrollstop." },
    frame:  { where: "The frame on the wall", title: "About and contact", cta: "Get in touch", url: "", blurb: "Who I am, what I'm building next and how to reach me." }
  },

  about: "I'm Jay. I build web apps, AI video pipelines and retro game mashups, then make videos about how they came together."
};

/* Shared signup: sends an email address to the Kit form above.
   Resolves "ok" when Kit accepts it, "fallback" when the browser blocked the
   direct request and Kit's own page opened in a new tab instead.
   Rejects with "invalid" when Kit says the address is bad, "off" when no
   form is set. */
window.SITE_SUBSCRIBE = function (email) {
  var action = window.SITE && window.SITE.ebook && window.SITE.ebook.kitFormAction;
  if (!action) return Promise.reject("off");
  function viaPage() {
    var f = document.createElement("form");
    f.method = "post"; f.action = action; f.target = "_blank"; f.style.display = "none";
    var i = document.createElement("input"); i.type = "hidden"; i.name = "email_address"; i.value = email;
    f.appendChild(i); document.body.appendChild(f); f.submit(); f.remove();
    return "fallback";
  }
  return fetch(action, {
    method: "POST",
    headers: { "Accept": "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({ email_address: email })
  }).then(function (r) {
    return r.json().catch(function () { return {}; }).then(function (j) {
      if (j && j.status === "success") return "ok";
      if (j && j.errors) throw "invalid";
      if (r.ok) return "ok";
      return viaPage();
    });
  }, function () { return viaPage(); });
};
