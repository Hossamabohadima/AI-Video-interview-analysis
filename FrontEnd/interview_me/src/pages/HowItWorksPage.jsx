import { useEffect, useRef, useState } from "react";

const steps = [
  {
    id: "upload-video",
    circleClassName: "absolute top-[400px] left-[215px] w-[100px] h-[100px]",
    iconType: "image",
    iconSrc: "https://c.animaapp.com/zou3Gdv0/img/group-7@2x.png",
    iconAlt: "Upload video icon",
    label: <>Upload Video</>,
    labelClassName:
      "absolute top-[531px] left-[191px] w-[147px] h-[71px] flex items-center justify-center [font-family:'Inter',Helvetica] font-bold text-[#808080] text-[25px] text-center tracking-[0] leading-[normal]",
  },
  {
    id: "extract-streams",
    circleClassName:
      "absolute top-[400px] left-[465px] w-[100px] h-[100px] bg-neutral-200 rounded-[50px] border-2 border-solid border-[#009986] opacity-[0.99]",
    iconType: "image",
    iconSrc: "https://c.animaapp.com/zou3Gdv0/img/extraction-icon.svg",
    iconAlt: "Extraction icon",
    iconClassName:
      "absolute top-[416px] left-[481px] w-[67px] h-[67px] aspect-[1]",
    label: (
      <>
        Extract Streams
        <br />
        (Audio, Text, Visual )
      </>
    ),
    labelClassName:
      "top-[531px] left-[387px] w-[259px] h-[71px] absolute [font-family:'Inter',Helvetica] font-bold text-[#808080] text-[25px] text-center tracking-[0] leading-[normal]",
  },
  {
    id: "ai-engine-analysis",
    circleClassName:
      "absolute top-[399px] left-[715px] w-[100px] h-[100px] bg-neutral-200 rounded-[50px] border-2 border-solid border-[#009986] opacity-[0.99]",
    iconType: "image",
    iconSrc: "https://c.animaapp.com/zou3Gdv0/img/ai-engine-icon.svg",
    iconAlt: "Ai engine icon",
    iconClassName:
      "absolute top-[407px] left-[722px] w-[85px] h-[85px] aspect-[1]",
    label: (
      <>
        Ai Engine
        <br />
        Analysis
      </>
    ),
    labelClassName:
      "top-[531px] left-[700px] w-[130px] h-[71px] absolute [font-family:'Inter',Helvetica] font-bold text-[#808080] text-[25px] text-center tracking-[0] leading-[normal]",
  },
  {
    id: "get-practical-report",
    circleClassName:
      "absolute top-[399px] left-[965px] w-[100px] h-[100px] bg-neutral-200 rounded-[50px] border-2 border-solid border-[#009986] opacity-[0.99]",
    iconType: "image",
    iconSrc: "https://c.animaapp.com/zou3Gdv0/img/report.svg",
    iconAlt: "Report",
    iconClassName:
      "absolute top-[416px] left-[982px] w-[65px] h-[65px] aspect-[1]",
    label: <>Get Practical Report</>,
    labelClassName:
      "top-[543px] left-[932px] w-[163px] h-[60px] flex items-center justify-center absolute [font-family:'Inter',Helvetica] font-bold text-[#808080] text-[25px] text-center tracking-[0] leading-[normal]",
  },
];

const connectorLines = [
  {
    id: "line-1",
    className: "top-[448px] left-[315px] absolute w-[150px] h-0.5",
  },
  {
    id: "line-2",
    className: "top-[448px] left-[565px] absolute w-[150px] h-0.5",
  },
  {
    id: "line-3",
    className: "top-[447px] left-[815px] absolute w-[150px] h-0.5",
  },
];

function HowItWorksPage() {
  const [productsOpen, setProductsOpen] = useState(false);
  const productsRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (productsRef.current && !productsRef.current.contains(event.target)) {
        setProductsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <main
      className="bg-[#e5e4e2] w-full min-w-[1280px] min-h-[859px] relative"
      data-model-id="15:40"
    >
      <header className="absolute top-[37px] left-[30px] right-[30px] flex items-center justify-between z-20">
        <div className="w-[191px] h-10 flex items-center [font-family:'Pacifico',Helvetica] font-normal text-[#009986] text-[35px] leading-[normal] whitespace-nowrap">
          Interview me
        </div>

        <nav aria-label="Primary" className="flex items-center gap-[36px]">
          <a
            href="#"
            className="inline-flex min-w-[62px] items-center justify-center text-[#56606B] text-[25px] font-bold whitespace-nowrap [font-family:'Alegreya_Sans',Helvetica]"
          >
            Home
          </a>

          <a
            href="#"
            aria-current="page"
            className="inline-flex min-w-[62px] items-center justify-center text-[#56606B] text-[25px] font-bold whitespace-nowrap [font-family:'Alegreya_Sans',Helvetica]"
          >
            How it works
          </a>

          <div
            ref={productsRef}
            className="relative inline-flex flex-col items-center"
          >
            <button
              type="button"
              onClick={() => setProductsOpen((prev) => !prev)}
              className="inline-flex flex-col items-center min-w-[90px] focus:outline-none"
            >
              <span className="inline-flex items-center justify-center text-[#009986] text-[25px] font-bold whitespace-nowrap [font-family:'Alegreya_Sans',Helvetica]">
                Products
              </span>

              <svg
                className={`mt-[6px] h-[11px] w-[13px] transition-transform duration-200 ${
                  productsOpen ? "rotate-180" : ""
                }`}
                viewBox="0 0 13 11"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M6.5 11L0.00480938 0.5L12.9952 0.5L6.5 11Z"
                  fill="#009986"
                />
              </svg>
            </button>

            {productsOpen && (
              <div className="absolute top-[50px] left-1/2 z-30 w-[340px] -translate-x-1/2 rounded-[20px] bg-[#E6F7F5] px-5 py-5 shadow-[0_6px_14px_rgba(0,0,0,0.12)]">
                <div className="flex flex-col gap-4">
                  <a
                    href="#"
                    className="flex items-center gap-3 text-[#009986] transition-opacity hover:opacity-80"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="-3 0 30 24"
                      fill="none"
                      stroke="#0FA99D"
                      strokeWidth="2.4"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="h-10 w-10 shrink-0"
                    >
                      <path d="M20 16.5A4.5 4.5 0 0 0 17 8h-1.26A8 8 0 1 0 4 15.25" />
                      <path d="M12 20V11" />
                      <path d="m8.8 14.2 3.2-3.2 3.2 3.2" />
                    </svg>
                    <span className="[font-family:'Alegreya_Sans',Helvetica] text-[18px] font-bold leading-none">
                      Analyze my interview
                    </span>
                  </a>

                  <a
                    href="#"
                    className="flex items-center gap-3 text-[#009986] transition-opacity hover:opacity-80"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="#009986"
                      strokeWidth="2.1"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="h-8 w-8 shrink-0"
                    >
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <path d="M14 2v6h6" />
                      <path d="M8 13h8" />
                      <path d="M8 17h5" />
                    </svg>
                    <span className="[font-family:'Alegreya_Sans',Helvetica] text-[18px] font-bold leading-none">
                      View my report
                    </span>
                  </a>
                </div>
              </div>
            )}
          </div>

          <a
            href="#"
            className="ml-[8px] h-[45px] px-[28px] rounded-[15px] bg-[#009986] inline-flex items-center justify-center"
          >
            <span className="[font-family:'Alegreya_Sans',Helvetica] font-medium text-white text-[25px] leading-[normal] whitespace-nowrap">
              Sign up
            </span>
          </a>
        </nav>
      </header>

      <section
        aria-labelledby="how-it-works-heading"
        className="absolute left-1/2 top-[180px] w-full max-w-[1200px] -translate-x-1/2 px-8"
      >
        <h1
          id="how-it-works-heading"
          className="text-center [font-family:'Inter',Helvetica] text-[40px] font-bold text-[#009986]"
        >
          How It works ?
        </h1>

        <div className="relative mt-32">
          <div className="absolute left-[12.5%] right-[12.5%] top-[52px] h-[2px] bg-[#009986]" />

          <div className="relative z-10 grid grid-cols-4 items-start text-center">
            <div className="flex flex-col items-center">
              <div className="flex h-[100px] w-[100px] items-center justify-center rounded-full border-2 border-[#009986] bg-[#E5E4E2]">
                <img
                  src="https://c.animaapp.com/zou3Gdv0/img/group-7@2x.png"
                  alt="Upload video icon"
                  className="h-[100px] w-[100px] object-contain"
                />
              </div>
              <div className="mt-10 [font-family:'Inter',Helvetica] text-[25px] font-bold text-[#808080] leading-tight">
                Upload
                <br />
                Video
              </div>
            </div>

            <div className="flex flex-col items-center">
              <div className="flex h-[100px] w-[100px] items-center justify-center rounded-full border-2 border-[#009986] bg-neutral-200">
                <img
                  src="https://c.animaapp.com/zou3Gdv0/img/extraction-icon.svg"
                  alt="Extraction icon"
                  className="h-[67px] w-[67px]"
                />
              </div>
              <div className="mt-10 [font-family:'Inter',Helvetica] text-[25px] font-bold text-[#808080] leading-tight">
                Extract Streams
                <br />
                (Audio, Text, Visual )
              </div>
            </div>

            <div className="flex flex-col items-center">
              <div className="flex h-[100px] w-[100px] items-center justify-center rounded-full border-2 border-[#009986] bg-neutral-200">
                <img
                  src="https://c.animaapp.com/zou3Gdv0/img/ai-engine-icon.svg"
                  alt="AI engine icon"
                  className="h-[85px] w-[85px]"
                />
              </div>
              <div className="mt-10 [font-family:'Inter',Helvetica] text-[25px] font-bold text-[#808080] leading-tight">
                Ai Engine
                <br />
                Analysis
              </div>
            </div>

            <div className="flex flex-col items-center">
              <div className="flex h-[100px] w-[100px] items-center justify-center rounded-full border-2 border-[#009986] bg-neutral-200">
                <img
                  src="https://c.animaapp.com/zou3Gdv0/img/report.svg"
                  alt="Report"
                  className="h-[65px] w-[65px]"
                />
              </div>
              <div className="mt-10 [font-family:'Inter',Helvetica] text-[25px] font-bold text-[#808080] leading-tight">
                Get Practical
                <br />
                Report
              </div>
            </div>
          </div>
        </div>
      </section>

      <footer className="absolute bottom-6 left-1/2 -translate-x-1/2">
        <p className="[font-family:'Inter',Helvetica] text-xs font-normal text-[#888888] text-center">
          © 2026 Interview Me. All rights reserved.
        </p>
      </footer>
    </main>
  );
}

export default HowItWorksPage;
