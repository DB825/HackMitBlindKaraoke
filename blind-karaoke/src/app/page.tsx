import React from "react";
import Link from "next/link";

/**
 * Blind Karaoke — Home Page
 * - Background hero image (fill/cover)
 * - Title: "blind karaoke"
 * - Start button
 * - Decorative SVG assets from Figma
 *
 * HOW TO USE
 * 1) Save this file as: src/app/page.tsx  (or place the component and import it there)
 * 2) Set your background image in `HERO_BG_URL` below.
 * 3) (Optional) Install the "Anonymous Pro" font in your globals.css (see comment at bottom).
 */

const HERO_BG_URL = "/images/home-hero.jpg"; // TODO: replace with your actual path

export default function HomePage() {
  return (
    <main className="min-h-screen w-full">
      <section
        className="relative mx-auto flex h-[2362px] w-[1575px] max-w-full flex-col items-center justify-center overflow-hidden rounded-2xl shadow"
        style={{
          backgroundImage: `url(${HERO_BG_URL})`,
          backgroundPosition: "50% 50%",
          backgroundSize: "cover",
          backgroundRepeat: "no-repeat",
        }}
      >
        {/* Title */}
        <h1
          className="mb-8 text-center font-bold text-black"
          style={{ fontFamily: '"Anonymous Pro", monospace', fontSize: 48, lineHeight: 1 }}
        >
          blind karaoke
        </h1>

        {/* Decorative assets cluster (position as needed) */}
        <div className="pointer-events-none absolute left-6 top-6 flex flex-col gap-6 opacity-90">
          <AssetGroup2 />
          <AssetGroup13 />
          <AssetGroup11 />
          <AssetGroup10 />
        </div>

        {/* Start Button */}
        <Link
          href="/play/demo"
          className="group inline-flex h-[74px] w-[345px] items-center justify-center rounded-[23px] bg-[#8DD7FF] shadow transition-transform active:scale-[0.98]"
          aria-label="Start"
        >
          <span
            className="text-white"
            style={{ fontFamily: '"Anonymous Pro", monospace', fontSize: 48, lineHeight: 1 }}
          >
            Start
          </span>
        </Link>

        {/* MIT Tim the Beaver image (optional) */}
        {/* <div
          className="absolute right-6 bottom-6 h-[855px] w-[1226px] rounded-xl"
          style={{
            backgroundImage: 'url(/images/tim-the-beaver.jpg)', // TODO: replace
            backgroundPosition: "50% 50%",
            backgroundSize: "cover",
            backgroundRepeat: "no-repeat",
          }}
        /> */}
      </section>
    </main>
  );
}

/* ================= SVG Assets from Figma ================= */
function AssetGroup2() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="51" height="67" viewBox="0 0 51 67" fill="none">
      <path d="M12.9011 1.49927C12.4674 4.98178 9.85224 12.8536 7.00052 18.7804C5.12605 22.6762 1.95415 25.141 1.94758 25.8112C1.86489 34.2455 9.82596 13.353 13.1048 9.39078C16.962 4.72964 22.0739 16.8223 28.4279 19.8843C31.4359 21.3339 34.3481 22.5258 36.3259 23.1763C41.6137 24.9155 28.2504 31.6986 25.1753 38.2628C24.0471 40.6712 24.7285 44.7876 24.5117 46.1478C24.0008 49.352 19.0513 38.322 14.4518 33.0588C12.4806 30.437 10.2859 28.2292 7.66417 26.6982C6.34344 26.0346 5.04242 25.6009 1.07367 23.8399" stroke="#F6F6F6" strokeWidth="2" strokeLinecap="round"/>
      <path d="M49.027 62.1795C48.5262 62.1795 47.016 62.1795 44.9935 62.5552C44.151 62.7117 43.9728 63.6821 44.2195 64.3196C44.4661 64.9571 45.2174 65.4579 45.9801 65.5908C46.7428 65.7236 47.4941 65.4731 48.0063 64.9685C48.5186 64.4638 48.769 63.7125 48.5224 63.075C48.2757 62.4376 47.5244 61.9367 46.7504 61.4207" stroke="#F6F6F6" strokeWidth="2" strokeLinecap="round"/>
    </svg>
  );
}

function AssetGroup13() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="91" height="77" viewBox="0 0 91 77" fill="none">
      <path d="M52.3045 13.389C52.3045 19.4233 50.7018 29.1486 47.4601 36.0267C44.8202 41.6277 40.1873 46.948 37.5344 50.6207C33.7285 55.8898 47.8122 39.7359 52.092 34.0477C55.3707 29.6901 54.32 23.1264 55.5402 18.2638C55.8372 17.0802 55.1456 15.8416 55.1395 15.8233C53.9383 12.2197 61.9934 23.0779 71.8947 32.5785C74.8702 35.4336 78.1901 35.2436 80.0174 35.6443C84.0774 36.5345 75.7861 43.7183 74.3655 50.5843C73.7111 53.7475 74.1591 59.0166 73.9588 60.8985C73.5067 65.1452 65.6844 51.8531 60.8217 48.6113C55.9591 45.7702 52.3166 44.5561 49.2934 43.949C47.4722 43.7426 45.0682 43.7426 42.5913 43.7426" stroke="#F6F6F6" strokeWidth="2" strokeLinecap="round"/>
      <path d="M84.5523 75.7604H89.809" stroke="#F6F6F6" strokeWidth="2" strokeLinecap="round"/>
      <path d="M1.7944 4.79401C1.7944 5.40259 2.70727 6.32467 4.54682 7.24676C5.42139 7.68514 6.38638 7.56026 7.16093 7.10383C8.83772 6.11572 9.47535 3.88115 9.47996 2.34588C9.48204 1.65509 8.26743 1.41919 7.34073 1.26244C6.41404 1.10568 5.50118 1.10568 5.03091 2.17069C4.56065 3.23569 4.56065 5.36571 6.40482 8.48235" stroke="#F6F6F6" strokeWidth="2" strokeLinecap="round"/>
    </svg>
  );
}

function AssetGroup11() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="64" height="46" viewBox="0 0 64 46" fill="none">
      <path d="M8.99895 44.8434C8.99895 32.9449 6.53975 6.39053 3 2C8.56424 3.02467 13.9546 4.26668 23.4002 4.88769C31.6161 5.09884 46.7811 5.09884 62.4057 5.09884" stroke="#F6F6F6" strokeWidth="2" strokeLinecap="round"/>
      <path d="M23 44.6467C23 43.8269 23 36.0271 23.8197 25.0538C24.0945 21.3762 26.2789 21.868 27.9432 22.2841C39.494 23.5324 54.4479 23.1225 57.5467 22.5015C59.0061 22.2903 60.2357 22.2903 61.5026 22.2903" stroke="#F6F6F6" strokeWidth="2" strokeLinecap="round"/>
    </svg>
  );
}

function AssetGroup10() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="44" height="40" viewBox="0 0 44 40" fill="none">
      <path d="M27.0824 1C29.1441 3.88148 33.2676 9.66929 38.037 15.6744C40.0715 18.2361 41.5643 20.8599 42.1915 22.9278C43.8514 28.4005 29.5913 28.7218 14.9292 33.8949C11.3709 34.9444 9.32152 35.3542 7.65101 35.7703C5.98049 36.1864 4.7509 36.5962 1 38.2606" stroke="#F6F6F6" strokeWidth="2" strokeLinecap="round"/>
      <path d="M18.6235 2.93494C20.0812 4.02006 21.539 8.39343 24.0929 13.693C25.302 16.2019 27.3812 17.9074 28.4827 19.1844C30.8761 21.9588 20.8375 22.2918 15.538 24.6648C14.2501 25.2183 13.165 25.58 11.8825 25.9472C10.6001 26.3144 9.15329 26.6761 6.56653 27.0488" stroke="#F6F6F6" strokeWidth="2" strokeLinecap="round"/>
    </svg>
  );
}

/* ===== Optional: include Anonymous Pro in globals.css =====
@import url('https://fonts.googleapis.com/css2?family=Anonymous+Pro:wght@400;700&display=swap');
*/
