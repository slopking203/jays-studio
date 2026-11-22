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
    title: "AI for Normies: 10 Simple Ways to Make Use of AI",
    kicker: "Free ebook",
    pitch: "Ten practical things you can do with AI this week, each one written so you can try it in an evening. Join the list and it's yours free.",
    cta: "Send me the ebook",
    kitFormAction: "https://app.convertkit.com/forms/10224334/subscriptions",
    done: "You're on the list! Check your inbox and confirm your email. Your free copy of the ebook arrives a few minutes later.",
    signupUrl: ""
  },

  /* What the TV shows. The remote on the coffee table steps through these.
     playlist is the channel's uploads list: the channel ID with "UC" swapped for "UU".
     It plays the newest upload first and adds new videos by itself. */
  channels: [
    { screen: "youtube", name: "Slopking", title: "Slopking on YouTube", cta: "Open YouTube", url: "https://www.youtube.com/@Slopking203", blurb: "New uploads land here first.",
      playlist: "UU54mFCaaPLonPLPN5JACVfQ", subscribe: "https://www.youtube.com/@Slopking203?sub_confirmation=1" },
    { screen: "youtube", name: "Jay vs America", title: "Jay vs America on YouTube", cta: "Open YouTube", url: "https://www.youtube.com/@jayvsamerica", blurb: "My travel channel.",
      playlist: "UU4ftEyMIEDCNg7ToECjL3tA", subscribe: "https://www.youtube.com/@jayvsamerica?sub_confirmation=1" }
  ],

  /* One entry per clickable object in the 3D room (and a section in the 2D site). */
  links: {
    tv:     { where: "The TV", title: "Slopking on YouTube", cta: "Open YouTube", url: "https://www.youtube.com/@Slopking203", blurb: "My video channels. New uploads land here first." },
    phone:  { where: "The phone tripod", title: "TikTok", cta: "Open TikTok", url: "https://www.tiktok.com/@slopking203", blurb: "Short cuts, behind-the-build clips and whatever I filmed this week." },
    arcade: { where: "The arcade cabinet", title: "Retro hybrid games", cta: "Play the games", url: "/games/", blurb: "Classic games smashed together and playable in your browser. A new mashup every month.",
              /* Each game is its own page under /games/. The arcade page lists them from here too. */
              items: [
                { name: "Paddle Fighter", url: "/games/paddle-fighter/", mashup: "Pong x Street Fighter", blurb: "Fighters are the paddles. Specials, smashes and a KO when the ball gets past." },
                { name: "Brick Tilt", url: "/games/brick-tilt/", mashup: "Breakout x pinball", blurb: "Flippers, bumpers and a plunger, with a wall of bricks to clear at the top." },
                { name: "Dr. Tetris", url: "/games/dr-tetris/", mashup: "Dr. Mario x Tetris", blurb: "Falling pieces in three colors. Match four to wipe out the viruses." },
                { name: "Starflap", url: "/games/starflap/", mashup: "Flappy Bird x Galaga", blurb: "Flap your ship through an alien swarm and shoot your way out." },
                { name: "Mazeworm", url: "/games/mazeworm/", mashup: "Snake x Pac-Man", blurb: "Grow a snake in a maze while chasers bite chunks off your tail." }
              ] },
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
  /* any signup on the site (ebook form or game popup) unlocks the games on this device */
  function unlock(how) { try { localStorage.setItem("jaysstudio_signedup", "1"); } catch (e) {} return how; }
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
  }, function () { return viaPage(); }).then(unlock);
};

/* Player address for a channel's uploads (newest first), or "" if it has none. */
window.SITE_PLAYER = function (ch) {
  return ch && ch.playlist ? "https://www.youtube-nocookie.com/embed/videoseries?list=" + encodeURIComponent(ch.playlist) + "&rel=0&playsinline=1" : "";
};
