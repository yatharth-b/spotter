// Next.js API route support: https://nextjs.org/docs/api-routes/introduction

import cheerio from 'cheerio';

export default async function handler(req, resp) {
    const res = await fetch("https://www.hollisterco.com/shop/us/p/hollister-feel-good-hoodie-53392322?categoryId=12551&faceout=model&seq=01");
    const prod_info = await res.text();
    const $ = cheerio.load(prod_info);
    const ogTitleMetaTag = $('meta[property="og:title"]').attr('content');
    prod_name = ogTitleMetaTag.split(" | ")[0];
    const ogImageUrl  = $('meta[property="og:image"]').attr('content');
    console.log(ogTitleMetaTag, ogImageUrl);
    return {
        props: {
            prod_name,
            ogImageUrl,
        }
    };
}