import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig(({ command, mode }) => {
	const isDev = command === 'serve';
	const isProd = command === 'build';

	return {
		plugins: [sveltekit()],
		server: isDev
			? {
					port: 3001,
					allowedHosts: true,
					proxy: {
						'/api': 'http://127.0.0.1:3002'
					}
			  }
			: undefined,
		build: isProd
			? {
				port: 3001,
				allowedHosts: false,
				proxy: {
					'/api': 'http://127.0.0.1:3002' // change this to your backend port
				}
			}
			: undefined
	};
});
