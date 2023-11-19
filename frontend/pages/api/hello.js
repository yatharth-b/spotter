import cheerio from "cheerio";

export default async function handler(req, resp) {
  console.log(req.body);

  const { url } = req.body;

  const res = await fetch(url);

  const prod_info = await res.text();

  const $ = cheerio.load(prod_info);
  const ogTitleMetaTag = $('meta[property="og:title"]').attr("content");
  const prod_name = ogTitleMetaTag.split(" | ")[0];
  const ogImageUrl = $('meta[property="og:image"]').attr("content");
  console.log(ogTitleMetaTag, ogImageUrl);
  resp.status(200).json({
    prod_name,
    ogImageUrl,
  });
}
