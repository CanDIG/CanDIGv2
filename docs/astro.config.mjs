// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightOpenAPI, { openAPISidebarGroups } from 'starlight-openapi'

import icon from 'astro-icon';

// https://astro.build/config
export default defineConfig({
    site: 'https://candig.github.io',
    base: 'CanDIGv2',
    integrations: [icon({
        include: {
            mdi: ["*"]
        }
    }), starlight({
    title: 'Docs',
    customCss: [
        './src/styles/custom.css'
    ],
    favicon: '/favicon.ico',
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
                collapsed: true
            },
            {
                base: 'technical/query',
                label: 'query api',
                schema: 'https://raw.githubusercontent.com/CanDIG/candigv2-query/refs/heads/stable/query_server/openapi.yaml',
                collapsed: true
            },
            {
                base: 'technical/katsu',
                label: 'katsu api',
                schema: 'https://raw.githubusercontent.com/CanDIG/katsu/refs/heads/stable/chord_metadata_service/mohpackets/docs/schemas/schema.yml',
                collapsed: true
            },
            {
                base: 'technical/htsget/drs',
                label: 'htsget drs api',
                schema: 'https://raw.githubusercontent.com/CanDIG/htsget_app/refs/heads/stable/htsget_server/drs_openapi.yaml',
                collapsed: true
            },
            {
                base: 'technical/htsget/beacon',
                label: 'htsget beacon api',
                schema: 'https://raw.githubusercontent.com/CanDIG/htsget_app/refs/heads/stable/htsget_server/beacon_openapi.yaml',
                collapsed: true
            },
            {
                base: 'technical/htsget/operations',
                label: 'htsget operations api',
                schema: 'https://raw.githubusercontent.com/CanDIG/htsget_app/refs/heads/stable/htsget_server/htsget_openapi.yaml',
                collapsed: true
            },
        ])
    ],
    sidebar: [
        {   
            collapsed: true,
            label: 'Deployment',
            items: [
                { label: 'Local deployment', slug: 'deployment/local' },
                { label: 'Production deployment', slug: 'deployment/production'},
                { label: 'Testing', slug: 'deployment/ingest-and-test'},
                { label: 'Interact using Make', slug: 'deployment/interact-with-the-stack'},
                { label: 'User roles', slug: 'deployment/user-roles'},
                { label: 'Logging', slug: 'deployment/logging'},
                { label: 'Back up/Restore', slug: 'deployment/backup-restore-candig'},
                { label: 'Troubleshooting', slug: 'deployment/stack-troubleshooting'}, 
            ]

        },
        {
            label: 'Guides',
            items: [
                // Each item here is one entry in the navigation menu.
                { 
                    label: 'Data ingest steps', 
                    items: 
                    [
                        'guides/ingest/prepare-clinical', 
                        'guides/ingest/register-programs', 
                        'guides/ingest/ingest-clinical',
                        'guides/ingest/prepare-genomic',
                        'guides/ingest/ingest-genomic',
                        'guides/ingest/ingest-help',
                    ]
                },
                { label: 'Data Exploration', slug: 'guides/explore' },
            ],
        },
        {
            label: 'Technical Docs',
            items: [ 
                { label: 'Architecture', slug: 'technical/architecture' },
                { label: 'Docker and submods', slug: 'technical/docker-and-submodules' },
                ...openAPISidebarGroups,
            ]
        },
    ],
		})]
});