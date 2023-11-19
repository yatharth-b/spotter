import styles from './Header.module.css'

export default function Header() {
  return (
    <div className={styles.Header}>
      <img src='/logo.svg' className={styles.Logo}></img>
      <div className={styles.HeaderItem}>scan</div>
      <div className={styles.HeaderItem}>closet</div>
    </div>
  )
}