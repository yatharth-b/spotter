import styles from "../styles/Closet.module.css";
import Header from "@/components/header/Header";
import { auth, db } from "@/firebase/firebase";
import { getDoc, onSnapshot, doc } from "firebase/firestore";
import { useState, useEffect } from "react";
import { onAuthStateChanged } from "firebase/auth";

export default function Closet() {
  const [requests, setRequests] = useState();

  useEffect(() => {
    onAuthStateChanged(auth, async (user) => {
      if (user) {
        console.log(user.uid)
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
      <Header></Header>
      {requests ? (
        <div className={styles.RequestsContainer}>
          {requests.map((request) => {
            return (
              <div className={styles.Request}>
                <img
                  src="https://cdn.discordapp.com/attachments/588057941714927625/1175275313975009321/IMG20231117222410.jpg?ex=656aa36e&is=65582e6e&hm=540f04ff77f31654765094cc4c304f5e651e1a3e72686fdb0508576834d4d930&"
                  className={styles.RequestImage}
                ></img>
                <div className={styles.RequestGradient}></div>
                <div className={styles.RequestCardContent}>
                  <div className={styles.RequestCardDate}>Nov 18</div>
                  <div className={styles.RequestCardNum}>{request.recs.length} Recommendations Available</div>
                </div>
              </div>
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
