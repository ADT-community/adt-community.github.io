// Practice-mode market data for ADT Invest.
// IMPORTANT: these are SAMPLE prices for practice, not live quotes. They move in a
// simulation. A live price feed replaces them before real trading.
const INVEST = {
  practiceStartGHS: 5000,
  sampleUsdRate: 15.5,        // sample cedis per US dollar, practice only
  feePct: 1.0,                // practice fee per trade, % of amount
  minGHS: 20,                 // minimum buy in cedis
  stocks: [
    // Ghana Stock Exchange (GSE), prices in cedis
    { t: "MTNGH", n: "MTN Ghana", m: "GSE", c: "GHS", p: 3.2, s: "Telecoms", y: 6.5, themes: ["ghana", "dividends"], about: "Ghana's largest mobile network and the company behind MTN MoMo." },
    { t: "GCB", n: "GCB Bank", m: "GSE", c: "GHS", p: 6.9, s: "Banking", y: 7.0, themes: ["ghana", "banks", "dividends"], about: "One of Ghana's biggest banks, with branches across the country." },
    { t: "EGH", n: "Ecobank Ghana", m: "GSE", c: "GHS", p: 7.5, s: "Banking", y: 4.0, themes: ["ghana", "banks"], about: "Ghana arm of the pan-African Ecobank group." },
    { t: "SCB", n: "Standard Chartered Ghana", m: "GSE", c: "GHS", p: 25.0, s: "Banking", y: 8.0, themes: ["ghana", "banks", "dividends"], about: "Ghana subsidiary of the international bank." },
    { t: "SOGEGH", n: "Societe Generale Ghana", m: "GSE", c: "GHS", p: 1.9, s: "Banking", y: 5.0, themes: ["ghana", "banks"], about: "Ghana subsidiary of the French banking group." },
    { t: "ACCESS", n: "Access Bank Ghana", m: "GSE", c: "GHS", p: 6.5, s: "Banking", y: 3.0, themes: ["ghana", "banks"], about: "Ghana arm of Nigeria's Access Bank." },
    { t: "EGL", n: "Enterprise Group", m: "GSE", c: "GHS", p: 3.0, s: "Insurance", y: 4.5, themes: ["ghana", "dividends"], about: "Insurance, pensions and property group." },
    { t: "GOIL", n: "Ghana Oil Company", m: "GSE", c: "GHS", p: 1.6, s: "Energy", y: 3.5, themes: ["ghana"], about: "Fuel stations and oil marketing across Ghana." },
    { t: "FML", n: "Fan Milk", m: "GSE", c: "GHS", p: 3.1, s: "Food", y: 0, themes: ["ghana"], about: "Maker of FanIce, FanYogo and other dairy snacks." },
    { t: "GGBL", n: "Guinness Ghana Breweries", m: "GSE", c: "GHS", p: 5.0, s: "Drinks", y: 2.0, themes: ["ghana"], about: "Brewer of Guinness, Malta Guinness and other drinks." },
    { t: "ALLGH", n: "Atlantic Lithium", m: "GSE", c: "GHS", p: 4.5, s: "Mining", y: 0, themes: ["ghana", "growth"], about: "Developing a lithium mine in Ghana's Central Region." },
    // US stocks, prices in US dollars
    { t: "AAPL", n: "Apple", m: "US", c: "USD", p: 355, s: "Technology", y: 0.4, themes: ["tech"], about: "Maker of the iPhone, Mac and Apple services." },
    { t: "MSFT", n: "Microsoft", m: "US", c: "USD", p: 520, s: "Technology", y: 0.7, themes: ["tech"], about: "Windows, Office, Azure cloud and AI." },
    { t: "AMZN", n: "Amazon", m: "US", c: "USD", p: 266, s: "Shopping & cloud", y: 0, themes: ["tech"], about: "Online shopping and Amazon Web Services cloud." },
    { t: "GOOGL", n: "Alphabet (Google)", m: "US", c: "USD", p: 320, s: "Technology", y: 0.3, themes: ["tech"], about: "Google Search, YouTube, Android and Google Cloud." },
    { t: "META", n: "Meta", m: "US", c: "USD", p: 628, s: "Technology", y: 0.3, themes: ["tech"], about: "Facebook, Instagram and WhatsApp." },
    { t: "NVDA", n: "Nvidia", m: "US", c: "USD", p: 175, s: "Chips", y: 0, themes: ["tech", "growth"], about: "Chips that power AI and gaming." },
    { t: "TSLA", n: "Tesla", m: "US", c: "USD", p: 340, s: "Cars & energy", y: 0, themes: ["growth"], about: "Electric cars, batteries and solar." },
    { t: "NFLX", n: "Netflix", m: "US", c: "USD", p: 110, s: "Entertainment", y: 0, themes: ["tech"], about: "Streaming films and series." },
    { t: "KO", n: "Coca-Cola", m: "US", c: "USD", p: 70, s: "Drinks", y: 2.9, themes: ["dividends"], about: "The world's biggest drinks company." },
    { t: "JPM", n: "JPMorgan Chase", m: "US", c: "USD", p: 300, s: "Banking", y: 2.0, themes: ["banks", "dividends"], about: "The largest US bank." },
    { t: "VOO", n: "S&P 500 fund (Vanguard)", m: "US", c: "USD", p: 600, s: "Index fund", y: 1.2, themes: ["dividends"], about: "One share of the 500 biggest US companies at once." }
  ],
  themes: [
    { id: "tech", name: "Tech giants" }, { id: "ghana", name: "Made in Ghana" }, { id: "banks", name: "Banks" },
    { id: "dividends", name: "Dividend payers" }, { id: "growth", name: "Fast growers" }
  ]
};
