import StyleDictionary from "style-dictionary";

const sd = new StyleDictionary({
  source: ["./src/ds-1.0/tokens.json"],
  hooks: {
    formats: {
      "typescript/declarations": ({ dictionary }) => {
        const exports = dictionary.allTokens
          .map((token) => `export declare const ${token.name}: string;`)
          .join("\n");
        const interfaceBody = dictionary.allTokens
          .map((token) => `  ${token.name}: string;`)
          .join("\n");
        return [
          "/** Do not edit directly, this file was auto-generated. */",
          "",
          exports,
          "",
          "export interface Tokens {",
          interfaceBody,
          "}",
          "",
        ].join("\n");
      },
    },
  },
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
        {
          destination: "tokens.d.ts",
          format: "typescript/declarations",
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
