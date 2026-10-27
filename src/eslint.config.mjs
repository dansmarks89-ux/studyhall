// Used by src/lint.py: the page scripts are classic (non-module) browser scripts.
import globals from "globals";

export default [{
  languageOptions: {
    ecmaVersion: "latest",
    sourceType: "script",
    globals: { ...globals.browser, SH: "readonly", SHUI: "readonly", SHVoice: "readonly", supabase: "readonly", claude: "readonly" },
  },
  rules: { "no-undef": "error" },
}];
