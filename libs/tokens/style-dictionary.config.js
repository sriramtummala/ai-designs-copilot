import StyleDictionary from "style-dictionary";

const sd = new StyleDictionary({
  source: ["./src/ds-1.0/tokens.json"],
  platforms: {
    css: {
      transformGroup: "css",
      buildPath: "./dist/css/",
      files: [
        {
          destination: "theme.css",
          format: "css/variables",
        },
      ],
    },
    js: {
      transformGroup: "js",
      buildPath: "./dist/js/",
      files: [
        {
          destination: "tokens.js",
          format: "javascript/es6",
        },
      ],
    },
    json: {
      transformGroup: "web",
      buildPath: "./dist/json/",
      files: [
        {
          destination: "tokens-docs.json",
          format: "json/flat",
        },
      ],
    },
  },
});

await sd.buildAllPlatforms();
