// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightOpenAPI, { openAPISidebarGroups } from 'starlight-openapi'

// https://astro.build/config
export default defineConfig({
    site: 'https://candig.github.io',
    base: 'CanDIGv2',
	integrations: [
		starlight({
			title: 'Docs',
            editLink: {
                baseUrl: 'https://github.com/CanDIG/CanDIGv2/edit/develop/'
            },
            logo: {
                src: './src/assets/my-logo.png',
                replacesTitle: true,
            },
			social: {
				github: 'https://github.com/candig/CanDIGv2',
			},
            plugins: [
                starlightOpenAPI([
                    {
                        base: 'technical/ingest',
                        label: 'ingest api',
                        schema: 'https://raw.githubusercontent.com/CanDIG/candigv2-ingest/refs/heads/develop/ingest_openapi.yaml',
                    },
                    {
                        base: 'technical/query',
                        label: 'query api',
                        schema: 'https://raw.githubusercontent.com/CanDIG/candigv2-query/refs/heads/develop/query_server/openapi.yaml',
                    },
                    {
                        base: 'technical/katsu',
                        label: 'katsu api',
                        schema: 'https://raw.githubusercontent.com/CanDIG/katsu/refs/heads/develop/chord_metadata_service/mohpackets/docs/schemas/schema.yml',
                    },
                    {
                        base: 'technical/htsget/drs',
                        label: 'htsget drs api',
                        schema: 'https://raw.githubusercontent.com/CanDIG/htsget_app/refs/heads/develop/htsget_server/drs_openapi.yaml',
                    },
                    {
                        base: 'technical/htsget/beacon',
                        label: 'htsget beacon api',
                        schema: 'https://raw.githubusercontent.com/CanDIG/htsget_app/refs/heads/develop/htsget_server/beacon_openapi.yaml',
                    },
                    {
                        base: 'technical/htsget/operations',
                        label: 'htsget operations api',
                        schema: 'https://raw.githubusercontent.com/CanDIG/htsget_app/refs/heads/develop/htsget_server/htsget_openapi.yaml',
                    },
                ])
            ],
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
                        { label: 'Architecture', slug: 'technical/architecture' },
                        ...openAPISidebarGroups,
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
