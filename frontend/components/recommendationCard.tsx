import React from "react";
import styles from "../styles/cardRec.module.css";

export const RecommendationCard = (props) => {

    return (
        <div className={styles.recommendationCard}>
            <a href={props.prod_url}>
                <img
                    src={props.image_url}
                    alt="recommendation"/>
                <div>
                    <h2>{props.prod_name}</h2>
                </div>
            </a>
        </div>
    );
};