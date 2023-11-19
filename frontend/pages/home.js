import { getAuth, onAuthStateChanged } from "firebase/auth";
import { app, auth, db } from "@/firebase/firebase";
import { useEffect } from "react";
import styles from "@/styles/Dashboard.module.css";
import Header from "@/components/header/Header";
import { doc, getDoc, setDoc, updateDoc } from "firebase/firestore";
import { useRouter } from "next/router";
import { useState } from "react";

export default function Home() {
  const router = useRouter();

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
          });
        }
      } else {
        router.push("/");
      }
    });
  }, []);
  
  const handleImageChange = (event) => {
    const file = event.target.files[0]; // Get the first selected file
    if (file) {
      const reader = new FileReader();

      reader.onloadend = () => {
        const base64String = reader.result; // Get the base64 representation of the image
        fetchRecs(base64String)
      };

      reader.readAsDataURL(file);
    }
  };

  function fetchRecs(base64image) {
    console.log(base64image)
    // fetch("http://127.0.0.1:5000/test/get_description", {
    //   method: "POST",
    //   headers: {
    //     "Content-Type": "application/json",
    //   },
    //   body: JSON.stringify({
    //     base64_image: base64image.split(",")[1],
    //   }),
    // })
    fetch('/test.json').then((res) => {
      res.json().then(async (api_data) => {
        const snap = await getDoc(doc(db, "users", uid))
        const reqs = snap.data().requests;
        console.log(reqs)
        console.log(api_data.response)
        const b64 = base64image.split(",")[1];
        reqs.push({
          // time: new Date(),
          image: b64,
          recs: api_data.response
        })
        
        const newData = {
          requests: reqs
        }

        console.log(newData)
        updateDoc(doc(db, "users", uid), {
          requests: reqs
        })
      })
    })
  }

  return (
    uid && 
    <div className={styles.Home}>
      <Header></Header>
      <div className={styles.HomeContent}>
        <div className={styles.AddImage}>
          <div className={styles.AddContent}>
            <img src="/add.png"></img>
            <div className={styles.AddMessage}>Let's upgrade your closet</div>
          </div>
          <input type="file" accept="image/*" onChange={handleImageChange} className={styles.ImageInput} />
        </div>
      </div>
    </div>
  );
}
