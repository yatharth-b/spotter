import React from "react";
import styles from "../styles/cardRec.module.css";

export const RecommendationCard = (props) => {

    return (
        <a href={props.prod_url}>
            <div className={styles.recommendationCard} style={{
                borderRadius: "12",
                boxShadow: "0px 4px 4px rgba(0, 0, 0, 0.25)",
                display: "flex",
                flexDirection: "column",
                justifyContent: "flex-end",
                margin: "auto",
                width: "60vw",
                height: "40vh",
                backgroundImage: `url(${props.img_url})`,
                backgroundSize: "cover",
                backgroundPosition: "center",
                backgroundRepeat: "no-repeat",
                }}>
                <div style={{
                    background: "linear-gradient(30deg, #000 -3.85%, rgba(255, 255, 255, 0.00) 100.31%)"
                }}></div>
                    <div className={styles.textDiv}>
                        <h2 className={styles.prodName} style = {{
                        color: "white",
                        padding: "2vh",
                        textAlign: "left",
                        fontWeight: '100',
                        fontFamily: "Playfair Display",
                    }}>
                        {props.prod_name}</h2>
                    </div>
            </div>
        </a>
    );
};