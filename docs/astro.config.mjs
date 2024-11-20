// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightOpenAPI, { openAPISidebarGroups } from 'starlight-openapi'
import starlightUtils from "@lorenzo_lewis/starlight-utils";

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
        starlightUtils({
            navLinks: {
                leading: { useSidebarLabelled: "headerLinks" },
            },
            multiSidebar: {
                switcherStyle: "hidden"
            }
        }),
        starlightOpenAPI([
            {
                base: 'technical/ingest-api',
                label: 'ingest api',
                schema: 'https://raw.githubusercontent.com/CanDIG/candigv2-ingest/refs/heads/develop/ingest_openapi.yaml',
                collapsed: true
            },
            {
                base: 'technical/query-api',
                label: 'query api',
                schema: 'https://raw.githubusercontent.com/CanDIG/candigv2-query/refs/heads/stable/query_server/openapi.yaml',
                collapsed: true
            },
            {
                base: 'technical/katsu-api',
                label: 'katsu api',
                schema: 'https://raw.githubusercontent.com/CanDIG/katsu/refs/heads/stable/chord_metadata_service/mohpackets/docs/schemas/schema.yml',
                collapsed: true
            },
            {
                base: 'technical/htsget/drs-api',
                label: 'htsget drs api',
                schema: 'https://raw.githubusercontent.com/CanDIG/htsget_app/refs/heads/stable/htsget_server/drs_openapi.yaml',
                collapsed: true
            },
            {
                base: 'technical/htsget/beacon-api',
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
	    {
                base: 'technical/federation-api',
                label: 'htsget operations api',
                schema: 'https://raw.githubusercontent.com/CanDIG/federation_service/refs/heads/develop/candig_federation/federation.yaml',
                collapsed: true
            },
        ])
    ],
    sidebar: [
        {
            collapsed:true,
            label: 'headerLinks',
            items: [
                { label: 'Deployment', slug: 'deployment/local' },
                { label: 'Submission', slug: 'ingest' },
                { label: 'Technical', slug: 'technical/architecture'}
            ]
        },
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
            label: 'Submission',
            items: [
                // Each item here is one entry in the navigation menu.
                { 
                    label: 'Data submission steps', 
                    items: 
                    [
                        'ingest/prepare-clinical', 
                        'ingest/register-programs', 
                        'ingest/ingest-clinical',
                        'ingest/prepare-genomic',
                        'ingest/ingest-genomic',
                        'ingest/ingest-help',
                    ]
                }
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
