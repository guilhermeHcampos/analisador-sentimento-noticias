"use client";

import { useState, FormEvent } from "react";
import styles from "./page.module.css";
import React from "react";

interface Article {
    title: string;
    author: string | null;
    source_name: string;
    url: string;
    sentiment: "Positivo" | "Neutro" | "Negativo";
    polarity: number;
}

export default function Home() {
    const [searchTerm, setSearchTerm] = useState("");
    const [articles, setArticles] = useState<Article[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (event: FormEvent) => {
        event.preventDefault(); 
        if (!searchTerm.trim()) return;

        setIsLoading(true);
        setError(null);
        setArticles([]);

        try {
            const response = await fetch(`http://localhost:8000/analyze?q=${encodeURIComponent(searchTerm)}`);

            if (!response.ok) {
                throw new Error(`Ocorreu um erro: ${response.statusText}`);
            }

            const data = await response.json();
            setArticles(data.articles);

        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    const getSentimentClass = (sentiment: string) => {
        if (sentiment === "Positivo") return styles.positive;
        if (sentiment === "Negativo") return styles.negative;
        return styles.neutral;
    };

    return (
        <main className={styles.main}>
            <div className={styles.container}>
                <h1 className={styles.title}>Análise de Sentimento de Notícias</h1>
                <p className={styles.description}>
                    Digite um termo para buscar notícias e ver o sentimento associado aos seus títulos.
                </p>

                <form onSubmit={handleSubmit} className={styles.form}>
                    <input
                        type="text"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        placeholder="Ex: Inteligência Artificial, Brasil..."
                        className={styles.input}
                        disabled={isLoading}
                    />
                    <button type="submit" className={styles.button} disabled={isLoading}>
                        {isLoading ? "Buscando..." : "Analisar"}
                    </button>
                </form>

                {error && <p className={styles.error}>{error}</p>}

                <div className={styles.resultsGrid}>
                    {articles.map((article, index) => (
                        <a href={article.url} key={index} target="_blank" rel="noopener noreferrer" className={styles.card}>
                            <h3>{article.title}</h3>
                            <p>Fonte: {article.source_name}</p>
                            <div className={styles.sentiment}>
                                Sentimento: <span className={getSentimentClass(article.sentiment)}>{article.sentiment}</span>
                            </div>
                        </a>
                    ))}
                </div>
            </div>
        </main>
    );
}
