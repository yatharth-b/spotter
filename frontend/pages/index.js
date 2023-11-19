import Head from 'next/head'
import Image from 'next/image'
import { Inter } from 'next/font/google'
import styles from '@/styles/Home.module.css'
// import { signin } from "firebase/auth";
import { signInWithGoogle } from '@/firebase/firebase'
import { useRouter } from 'next/router'

export default function Home() {

  const router = useRouter()

  return (
    <div className={styles.Home}>
      <div className={styles.tagline}>Your closet called, it needs a makeover.</div>
      <span className={styles.LoginButton} onClick={() => {
        signInWithGoogle().then((result) => {
          router.push('/home')
        })
      }}><img src='/google.png' className={styles.GoogleIcon}></img> Login</span>
    </div>
  )
}
