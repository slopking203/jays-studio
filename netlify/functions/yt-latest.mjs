/* Newest upload on a YouTube channel, for the TV in the 3D studio.
   GET /api/yt-latest?ch=UC...        -> { id, title, published, thumb }
   GET /api/yt-latest?ch=UC...&img=1  -> that video's thumbnail (jpeg), served
   from this site so the 3D room can paint it onto the TV screen.
   Reads the channel's public feed; the CDN keeps each answer for 15 minutes. */

const CACHE = {
  "Cache-Control": "public, max-age=300",
  "Netlify-CDN-Cache-Control": "public, s-maxage=900, stale-while-revalidate=3600",
};

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...(status === 200 ? CACHE : { "Cache-Control": "no-store" }) },
  });

const decode = (s) =>
  s.replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");

async function latest(ch) {
  const r = await fetch("https://www.youtube.com/feeds/videos.xml?channel_id=" + ch, {
    headers: { "User-Agent": "Mozilla/5.0 (compatible; JaysStudio/1.0)" },
  });
  if (!r.ok) throw new Error("feed " + r.status);
  const entry = (await r.text()).split("<entry>")[1];
  if (!entry) return null;
  const id = (entry.match(/<yt:videoId>([\w-]{11})<\/yt:videoId>/) || [])[1];
  if (!id) return null;
  const title = decode((entry.match(/<title>([\s\S]*?)<\/title>/) || [])[1] || "").trim();
  const published = (entry.match(/<published>([^<]+)<\/published>/) || [])[1] || "";
  return { id, title, published };
}

export default async (req) => {
  const url = new URL(req.url);
  const ch = url.searchParams.get("ch") || "";
  if (!/^UC[\w-]{22}$/.test(ch)) return json({ error: "unknown channel" }, 400);
  const given = url.searchParams.get("v") || "";
  let v;
  try { v = url.searchParams.get("img") && /^[\w-]{11}$/.test(given) ? { id: given } : await latest(ch); } catch (e) { return json({ error: String(e.message || e) }, 502); }
  if (!v) return json({ error: "no videos yet" }, 404);

  if (url.searchParams.get("img")) {
    for (const name of ["maxresdefault", "hqdefault"]) {
      const t = await fetch("https://i.ytimg.com/vi/" + v.id + "/" + name + ".jpg");
      if (t.ok) {
        return new Response(await t.arrayBuffer(), { headers: { "Content-Type": "image/jpeg", ...CACHE } });
      }
    }
    return json({ error: "no thumbnail" }, 404);
  }
  return json({ ...v, thumb: "/api/yt-latest?ch=" + ch + "&img=1&v=" + v.id });
};

export const config = { path: "/api/yt-latest" };
