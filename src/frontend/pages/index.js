import Head from "next/head";
import Profile from "../components/Profile";

export default function Home() {
  return (
    <div>
      <Head>
        <title>NutricionAI - Asistente Nutricional</title>
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main>
        <h1>NutricionAI</h1>
        <Profile />
      </main>
    </div>
  );
}
