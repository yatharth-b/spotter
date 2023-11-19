import styles from './Header.module.css'

export default function Header({ curr }) {
  return (
    <div className={styles.Header}>
      <a href='/home'><div className={curr === "scan" ? styles.HeaderItemOrange : styles.HeaderItem}>Scan</div></a>
      <a href='/closet'><div className={curr === "closet" ? styles.HeaderItemOrange : styles.HeaderItem}>Closet</div></a>
    </div>
  )
}