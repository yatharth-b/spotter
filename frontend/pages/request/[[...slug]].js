import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { db } from "@/firebase/firebase";
import { doc, getDoc } from "firebase/firestore";
import Header from "@/components/header/Header";

import styles from "../../styles/Request.module.css";

export default function Page() {
  const router = useRouter();
  const { slug } = router.query;
  const [recs, setRecs] = useState();
  const [image, setImage] = useState();

  useEffect(() => {
    if (slug) {
      const docRef = doc(db, "users", slug[0]);
      getDoc(docRef).then(async (snap) => {
        const data = snap.data();

        const target_req = data.requests[0]; // filter out and find the request using parameteres

        const temp_recs = [];

        await Promise.all(
          target_req.recs.map(async (rec) => {
            try {
              const metadata_ = await fetch("/api/hello", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({
                  url: "https://hollisterco.com" + rec,
                }),
              });
              const metadata = await metadata_.json();
              console.log(metadata.prod_name)
              temp_recs.push({
                prod: metadata.prod_name,
                prod_image: metadata.ogImageUrl,
                prod_link: rec,
              });
            } catch {}
          })
        );

        console.log(temp_recs);

        setRecs([...temp_recs]);
        setImage(target_req.image_url);
      });
    }
  }, [router.query]);

  return (
    recs && (
      <>
        <div className={styles.Request}>
          <Header></Header>
          <div className={styles.RequestImage}>
            <img src={image} className={styles.RequestImageImage}></img>
            <div className={styles.RequestGradient}></div>
            <div className={styles.RequestCardContent}>
              <div className={styles.RequestCardDate}>Nov 18</div>
              <div className={styles.RequestCardNum}>
                {" "}
                {recs.length} Recommendations Available
              </div>
            </div>
          </div>
          <div className={styles.Recommendations}>
            {recs.map((rec) => {
              return (
                <div className={styles.RecommendationCard}>
                  <img
                    src={rec.prod_image}
                    className={styles.RecommendationImage}
                  ></img>
                  <div className={styles.RequestGradient}></div>
                  <div className={styles.RecommendationCardContent}>
                    <div className={styles.RecommendationCardDate}>{rec.prod}</div>
                    {/* <div className={styles.RecommendationCardNum}>
                      {rec.pro}
                    </div> */}
                  </div>
                </div>
              );
            })}
            {/* <div className=""></div> */}
          </div>
        </div>
      </>
    )
  );
}
