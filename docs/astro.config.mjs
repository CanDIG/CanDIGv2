// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
    site: 'https://candig.github.io',
    base: 'CanDIGv2',
	integrations: [
		starlight({
			title: 'Docs',
            logo: {
                src: './src/assets/my-logo.png',
            },
			social: {
				github: 'https://github.com/candig/CanDIGv2',
			},
			sidebar: [
                {
                    label: 'Deployment',
                    items: [
                        { label: 'Local deployment', slug: 'deployment/local' },
                        { label: 'Testing', slug: 'deployment/ingest-and-test'},
                        { label: 'Interact using Make', slug: 'deployment/interact-with-the-stack'},
                        { label: 'Production deployment', slug: 'deployment/production'},
                        { label: 'Back up/Restore', slug: 'deployment/backup-restore-candig'}, 
                    ]

                },
				{
					label: 'Guides',
					items: [
						// Each item here is one entry in the navigation menu.
						{ label: 'Data ingest', slug: 'guides/ingest' },
                        { label: 'Data Exploration', slug: 'guides/explore' },
					],
				},
                {
                    label: 'Technical Docs',
                    items: [ 
                        {label: 'Architecture', slug: 'technical/architecture'}
                    ]
                },
				{
					label: 'Reference',
					autogenerate: { directory: 'reference' },
				},
			],
		}),
	],
});
