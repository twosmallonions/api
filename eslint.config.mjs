import globals from 'globals';
import pluginJs from '@eslint/js';
import tseslint from 'typescript-eslint';
import eslintConfigPrettier from 'eslint-config-prettier';
import importPlugin from 'eslint-plugin-import';

export default [
    { files: ['**/*.{js,mjs,cjs,ts}'] },
    { languageOptions: { globals: globals.node } },
    pluginJs.configs.recommended,
    ...tseslint.configs.recommended,
    eslintConfigPrettier,
    importPlugin.flatConfigs.recommended,
    importPlugin.flatConfigs.typescript,
    {
        rules: {
            'import/order': 'error',
        },
    },
    {
        ignores: ['node_modules/', 'dist/'],
    },
    {
        settings: {
            'import/resolver': {
                typescript: {
                    alwaysTryTypes: true,
                },
            },
        },
    },
];
