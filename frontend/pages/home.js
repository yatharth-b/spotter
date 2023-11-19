import { getAuth, onAuthStateChanged } from "firebase/auth";
import { app, auth, db, storage } from "@/firebase/firebase";
import { useEffect } from "react";
import styles from "@/styles/Dashboard.module.css";
import Header from "@/components/header/Header";
import { doc, getDoc, setDoc, updateDoc } from "firebase/firestore";
import { useRouter } from "next/router";
import { useState } from "react";
import {
  getStorage,
  uploadString,
  ref,
  getDownloadURL,
  uploadBytes,
} from "firebase/storage";
// import { get } from "express/lib/response";

export default function Home() {
  const router = useRouter();

  const [loading, setLoading] = useState(false);
  const [uid, setUid] = useState();

  useEffect(() => {
    onAuthStateChanged(auth, async (user) => {
      if (user) {
        setUid(user.uid);
        const docRef = doc(db, "users", user.uid);
        const docSnap = await getDoc(docRef);

        if (!docSnap.exists()) {
          await setDoc(doc(db, "users", user.uid), {
            requests: [],
            req_count: 0,
          });
        }
      } else {
        router.push("/");
      }
    });
  }, []);

  const handleImageChange = (event) => {
    setLoading(true);
    const file = event.target.files[0]; // Get the first selected file
    if (file) {
      const reader = new FileReader();
      const currentDate = new Date();

      const month = (currentDate.getMonth() + 1).toString().padStart(2, "0");
      const day = currentDate.getDate().toString().padStart(2, "0");
      const hours = currentDate.getHours().toString().padStart(2, "0");
      const minutes = currentDate.getMinutes().toString().padStart(2, "0");
      const seconds = currentDate.getSeconds().toString().padStart(2, "0");
      const milliseconds = currentDate
        .getMilliseconds()
        .toString()
        .padStart(3, "0"); // 3 digits for milliseconds
      const formattedDateTime = `${month}-${day}_${hours}-${minutes}-${seconds}-${milliseconds}`;

      const storageRef = ref(storage, formattedDateTime);

      reader.onloadend = () => {
        const base64String = reader.result;
        uploadBytes(storageRef, file).then(() => {
          fetchRecs(formattedDateTime, base64String);
        });
      };

      reader.readAsDataURL(file);
    }
  };

  function fetchRecs(url, base64image) {
    let image_id = 0;
    fetch("https://style-select-still-star-3228-holy-sun-1738-misty-thunder-7478.fly.dev/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        base64_image: base64image.split(",")[1],
      }),
    }).then((res) => {
      res.json().then(async (api_data) => {
        const snap = await getDoc(doc(db, "users", uid));
        const reqs = snap.data().requests;
        const req_count = snap.data().req_count;

        image_id = req_count + 1;

        // console.log(reqs)
        // console.log(api_data.response)
        reqs.push({
          time: new Date(),
          image_url: url,
          recs: api_data.response,
          id: image_id,
        });

        const newData = {
          requests: reqs,
          req_count: image_id,
        };

        await updateDoc(doc(db, "users", uid), newData);
        router.push(`/request/${uid}/${image_id}`);
      });
    });
  }

  return (
    uid && (
      <div className={styles.Home}>
        <div></div>
        <div className={styles.HomeContent}>
          {loading ? (
            <div className={styles.Loader}>Loading</div>
          ) : (
            <div className={styles.AddImage}>
              <div className={styles.AddContent}>
                <img src="/add.png"></img>
                <div className={styles.AddMessage}>
                  Let's upgrade your closet
                </div>
              </div>
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className={styles.ImageInput}
              />
            </div>
          )}
        </div>
      </div>
    )
  );
}
