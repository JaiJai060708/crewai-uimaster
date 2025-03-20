import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		port: 3000,
		proxy: {
		  '/api': 'http://127.0.0.1:5000'
		}
	  }
});
