MathJax.Hub.Config({
    extensions: ["tex2jax.js"],
    jax: ["input/TeX", "output/CommonHTML"],
    tex2jax: {
      inlineMath: [ ['$','$'], ["\\(","\\)"] ],
      displayMath: [ ['$$','$$'], ["\\[","\\]"] ],
      processEscapes: true
    },
    "HTML-CSS": { availableFonts: ["TeX"] },
    menuSettings: {
        zoom: "Double-Click",
        mpContext: true,
        mpMouse: true
      },
    config: [],
    showProcessingMessages: false,
    messageStyle: "none",
    showMathMenu: false
  });