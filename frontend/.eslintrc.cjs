module.exports = {
  root: true,
  extends: ["next/core-web-vitals", "plugin:prettier/recommended"],
  rules: {
    "prettier/prettier": [
      "error",
      {
        singleQuote: false,
        semi: true,
        tabWidth: 2,
        trailingComma: "es5",
        printWidth: 100
      }
    ]
  }
};
