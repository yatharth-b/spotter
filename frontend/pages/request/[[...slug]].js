import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { db } from "@/firebase/firebase";
import { doc, getDoc, Timestamp } from "firebase/firestore";
import Header from "@/components/header/Header";
import { ref, getDownloadURL } from "firebase/storage";
import { storage } from "@/firebase/firebase";

import styles from "../../styles/Request.module.css";

export default function Page() {
  const router = useRouter();
  const { slug } = router.query;
  const [recs, setRecs] = useState();
  const [image, setImage] = useState();
  const [time, setTime] = useState();

  useEffect(() => {
    if (slug) {
      const docRef = doc(db, "users", slug[0]);
      getDoc(docRef).then(async (snap) => {
        const data = snap.data();

        const target_req = data.requests.filter((req) => {
          return req.id === parseInt(slug[1], 10);
        })[0];

        console.log(target_req);

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

              temp_recs.push({
                prod: metadata.prod_name,
                prod_image: metadata.ogImageUrl,
                prod_link: rec,
              });
            } catch {}
          })
        );

        setRecs([...temp_recs]);
        setImage(target_req.image_url);
        setTime(target_req.time);
      });
    }
  }, [router.query]);

  var monthAbbreviations = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];

  return (
    recs && (
      <>
        <div className={styles.Request}>
          <span className={styles.SlugHeader}>
            <a href="/home">
              <img src="/backar.svg" className={styles.BackArrow}></img>
            </a>
            Go Back
          </span>

          <div className={styles.RequestImage}>
            <img src={image} className={styles.RequestImageImage}></img>
            <div className={styles.RequestGradient}></div>
            <div className={styles.RequestCardContent}>
              <div className={styles.RequestCardDate}>
                {monthAbbreviations[time.toDate().getMonth()]}{" "}
                {time.toDate().getDate()}
              </div>
              <div className={styles.RequestCardNum}>
                {" "}
                {recs.length} Recommendations Available
              </div>
            </div>
          </div>
          <div className={styles.Recommendations}>
            {recs.map((rec) => {
              return (
                <a href={"https://hollisterco.com" + rec.prod_link}>
                  <div className={styles.RecommendationCard}>
                    <img
                      src={rec.prod_image}
                      className={styles.RecommendationImage}
                    ></img>
                    <div className={styles.RequestGradient}></div>
                    <div className={styles.RecommendationCardContent}>
                      <div className={styles.RecommendationCardDate}>
                        {rec.prod}
                      </div>
                      <div className={styles.RecommendationCardNum}>
                        Hollister
                      </div>
                    </div>
                  </div>
                </a>
              );
            })}
            {/* <div className=""></div> */}
          </div>
        </div>
      </>
    )
  );
}
