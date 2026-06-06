/// <reference types="vite/client" />

// Declare Vue single-file components
declare module '*.vue' {
	import type { DefineComponent } from 'vue';
	const component: DefineComponent<{}, {}, any>;
	export default component;
}
