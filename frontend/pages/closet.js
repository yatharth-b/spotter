import styles from "../styles/Closet.module.css";
import Header from "@/components/header/Header";
import { auth, db } from "@/firebase/firebase";
import { getDoc, onSnapshot, doc } from "firebase/firestore";
import { useState, useEffect } from "react";
import { onAuthStateChanged } from "firebase/auth";

export default function Closet() {
  const [requests, setRequests] = useState();
  const [uid, setUid] = useState()

  useEffect(() => {
    onAuthStateChanged(auth, async (user) => {
      if (user) {
        setUid(user.uid)
        const docRef = doc(db, "users", user.uid);
        const docSnap = await getDoc(docRef);

        if (!docSnap.exists()) {
          await setDoc(doc(db, "users", user.uid), {
            requests: [],
          });
        }

        const unsub = onSnapshot(
          doc(db, "users", user.uid),
          { includeMetadataChanges: true },
          (doc) => {
            console.log(doc.data());
            setRequests(doc.data().requests);
          }
        );
      } else {
        router.push("/");
      }
    });
  }, []);

  

  return (
    <div className={styles.Closet}>
      <Header curr="closet"></Header>
      {requests && uid ? (
        <div className={styles.RequestsContainer}>
          {requests.map((request) => {
            return (
              <a href={`/request/${uid}/${request.id}`}>
                <div className={styles.Request}>
                  <img
                    src={request.image_url}
                    className={styles.RequestImage}
                  ></img>
                  <div className={styles.RequestGradient}></div>
                  <div className={styles.RequestCardContent}>
                    <div className={styles.RequestCardDate}>{request.time.getDate()}</div>
                    <div className={styles.RequestCardNum}>{request.recs.length} Recommendations Available</div>
                  </div>
                </div>
              </a>
            );
          })}
        </div>
      ) : (
        <div className={styles.ErrorContainer}>
          <div>You haven't made any requests yet!</div>
        </div>
      )}
    </div>
  );
}
