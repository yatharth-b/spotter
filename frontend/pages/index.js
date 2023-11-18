import Head from 'next/head'
import Image from 'next/image'
import { Inter } from 'next/font/google'
import styles from '@/styles/Home.module.css'
import { signInWithPopup } from "firebase/auth";
import { provider, auth } from '../firebase/firebase'
import { RecommendationCard } from '../components/recommendationCard';

export default function Home() {
  return (
    <>
        <div className={styles.Home}>
            <div className={styles.tagline}>Your closet called, it needs a makeover.</div>
            <span className={styles.LoginButton} onClick={() => {
            signInWithPopup(auth, provider).then((result) => {
                console.log(result.user)
            })
            }}><img src='/google.png' className={styles.GoogleIcon}></img> Login</span>
        </div>
        <div className="card">
            <RecommendationCard prod_url = "" img_url = "" prod_name="temp"/>
        </div>
    </>
  )
}
